import os

import matplotlib.pyplot as plt
import torch
from cellpose.models import CellposeModel
import random
from pathlib import Path
import shutil
from cellpose import io, models, train
import numpy as np

device = torch.device("mps" if torch.backends.mps.is_available() else
                      "cuda" if torch.cuda.is_available() else "cpu")

def split_train_test(finetune_dir, train_ratio=0.8, seed=42):
    random.seed(seed)
    finetune_dir = Path(finetune_dir)
    output_dir = finetune_dir.parent
    train_dir = output_dir / "Train"
    test_dir = output_dir / "Test"

    for d in [train_dir, test_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Trouver les paires image/masque
    image_files = [f for f in finetune_dir.glob("*.tif") if "_masks" not in f.name]
    mask_files = list(finetune_dir.glob("*_masks.tif"))

    pairs = []
    for img in image_files: 
        name = img.stem  # ex: image_1
        expected_mask = finetune_dir / f"{name}_masks.tif"  # We rebuild the path to the expected mask file to see if for example image_1_masks.tif exists
        if expected_mask.exists():                          # This is more robust than using ```matching_masks = [m for m in mask_files if name in m.name]```, because image_1 is also IN image_10, so it would match image_10_masks.tif as well and image_1 won't appear in the list of files, hence finetuning will crash bc of missing mask.
            pairs.append((img, expected_mask))
        else:
            print(f"Aucun masque trouvé pour {img.name}")

    # Shuffle + split
    print("Splitting dataset into train and test sets...")
    random.shuffle(pairs)
    split_idx = int(len(pairs) * train_ratio)   
    train_pairs = pairs[:split_idx]
    test_pairs = pairs[split_idx:]

    def copy_pairs(pairs, dest_dir):
        for img_path, mask_path in pairs:
            print(f"Processing pair: {img_path.name} and {mask_path.name}")
            for f in [img_path, mask_path]:
                dst = dest_dir / f.name
                print(f"Copying {f} → {dst}")
                shutil.copy(f, dst)

    copy_pairs(train_pairs, train_dir)
    copy_pairs(test_pairs, test_dir)

    print(f"Dataset split: {len(train_pairs)} train, {len(test_pairs)} test")
    return train_dir, test_dir

def finetune_cellpose(output_path, epochs, lr, model_name):
    
    output_path = Path(output_path)
    print("output_path in finetune_cellpose: ", output_path)
    train_dir = output_path.parent / "Train"
    test_dir = output_path.parent / "Test"
    save_dir = output_path.parent   # Path where the model and loss curve will be saved.

    save_dir.mkdir(parents=True, exist_ok=True)
    train_dir.mkdir(parents=True, exist_ok=True)
    test_dir.mkdir(parents=True, exist_ok=True)

    print(f"Train directory: {train_dir}")
    print(f"Test directory: {test_dir}")
    print(f"Save directory: {save_dir}")
    
    output = io.load_train_test_data(str(train_dir), str(test_dir),
                                    mask_filter="_masks",look_one_level_down=False)  # !!! Need to add str to train_dir and test_dir because they are Path objects defined above, and io.load_train_test_data expects strings
    images, labels, image_names, test_images, test_labels, image_names_test = output

    # Cast data to float32 before training
    images = [img.astype(np.float32) for img in images]
    labels = [lbl.astype(np.float32) for lbl in labels]
    test_images = [img.astype(np.float32) for img in test_images]
    test_labels = [lbl.astype(np.float32) for lbl in test_labels]

    print("test labels len",len(test_labels))
    print("unique values in test labels:")
    print([np.unique(lbl) for lbl in test_labels])
    print("shapes of test labels:")
    print([lbl.shape for lbl in test_labels])

    # Cast data to float32 and labels to int32 before training. Let cellpose handle the conversion to torch tensors.
    images = np.array([img.astype(np.float32) for img in images])
    labels = np.array([lbl.astype(np.int32)   for lbl in labels])       # labels = entiers !
    test_images = np.array([img.astype(np.float32) for img in test_images])
    test_labels = np.array([lbl.astype(np.int32)   for lbl in test_labels])

    print("Using device:", device)
    model = CellposeModel(gpu=True, device=device, pretrained_model='cpsam')
    
    # Très important : forcer tous les poids/buffers en float32
    net = model.net.float()
    net.dtype = torch.float32 
    print("net dtype:", next(model.net.parameters()).dtype)
    print("images dtype:", images.dtype)
    # # # torch.set_default_dtype(torch.float32)
    # # # model.net = model.net.to(dtype=torch.float32, device=device)
    
    print("GPU disponible:", torch.backends.mps.is_available())
    print("GPU utilisé:", model.device)
    print("lr: ", lr, "epochs: ", epochs)
    model_path, train_losses, test_losses = train.train_seg(
        net,
        model_name=model_name,
        save_path=save_dir,
        train_data=images, train_labels=labels,
        test_data=test_images, test_labels=test_labels, 
        min_train_masks=1,
        #weight_decay=1e-4,
        learning_rate=lr,
        n_epochs=epochs,
        channel_axis=None # None pour 2D, -1 pour 3D (mais pas de 3D dans ce cas)
    )

    return save_dir, train_losses, test_losses

def save_loss_curve(save_path, train_losses, test_losses, model_name):
    print(save_path)
    plt.figure()
    plt.plot(train_losses, label="Train Loss")
    plt.plot(test_losses, label="Test Loss", linestyle='--')
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training and Test Loss over Epochs")
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, f"loss_{model_name}.png"))
    plt.close()
