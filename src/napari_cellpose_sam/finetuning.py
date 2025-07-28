import os

import matplotlib.pyplot as plt
import torch
from cellpose.models import CellposeModel
from tifffile import imread


def load_dataset(folder):
    X, Y = [], []
    for fname in os.listdir(folder):
        if fname.endswith("_img.tif"):
            img = imread(os.path.join(folder, fname))
            mask = imread(os.path.join(folder, fname.replace("_img", "_mask")))
            X.append(img)
            Y.append(mask)
    return X, Y


def train_model(X, Y, model_path, lr=0.001, n_epochs=100):
    model = CellposeModel(pretrained_model=model_path, gpu=True)
    optimizer = torch.optim.Adam(model.net.parameters(), lr=lr)
    criterion = torch.nn.CrossEntropyLoss()

    train_losses = []
    # test_losses = []

    for epoch in range(n_epochs):
        model.net.train()
        epoch_loss = 0
        for x, y in zip(X, Y, strict=False):
            x_tensor = (
                torch.from_numpy(x).unsqueeze(0).unsqueeze(0).float().cuda()
            )
            y_tensor = torch.from_numpy(y).unsqueeze(0).long().cuda()
            pred = model.net(x_tensor)[0]  # get logits
            loss = criterion(pred, y_tensor)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        train_losses.append(epoch_loss / len(X))

        print(f"Epoch {epoch + 1}/{n_epochs} - Loss: {train_losses[-1]:.4f}")

    return model, train_losses


def save_loss_curve(train_losses, save_path):
    plt.figure()
    plt.plot(train_losses, label="Train Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title("Training Loss Curve")
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, "training_loss_curve.png"))
    plt.close()
