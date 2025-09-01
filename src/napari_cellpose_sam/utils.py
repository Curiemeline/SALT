import os
from pathlib import Path

from napari.utils.notifications import show_info
from qtpy.QtWidgets import QFileDialog
from tifffile import imwrite


def create_analysis_structure(base_path: Path, experiment_name: str) -> Path:
    """
    Creates a new file structure to launch a image analysis.
    REturns root folder path of this analysis.
    """
    analysis_dir = base_path / experiment_name
    subdirs = ["raw", "segmented_frames", "segmented_stacks", "finetune"]
    for subdir in subdirs:
        (analysis_dir / subdir).mkdir(parents=True, exist_ok=True)
    return analysis_dir


def browse_file(line_edit):
    path, _ = QFileDialog.getOpenFileName()
    if path:
        line_edit.setText(path)


def browse_folder(line_edit):
    folder = QFileDialog.getExistingDirectory()
    if folder:
        line_edit.setText(folder)


def parse_frame_range(frame_range_str):
    # Accept format like "1-5" or "3" or "1,2,4-6"
    frames = []
    for part in frame_range_str.split(","):
        if "-" in part:
            start, end = part.split("-")
            frames.extend(range(int(start), int(end) + 1))
        else:
            frames.append(int(part))
    return frames


def save_img_masks(
    viewer, img_layer, mask_layer, save_path, frame_indices=None
):
    if len(viewer.layers) < 2:
        show_info(
            viewer,
            "There needs to be at least 2 layers: an image and a mask layer.",
        )
        return

    if not save_path:
        show_info("Please specify a save path.")
        return

    if not img_layer or not mask_layer:
        show_info(
            viewer, "Please select both an image layer and a mask layer."
        )
        return
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)

    image = img_layer.data
    mask_data = mask_layer.data
    base_name = img_layer.name
    base_name = os.path.splitext(base_name)[
        0
    ]  # remove .tif or .tiff or whatever extension
    print(type(image), type(mask_data))

    if mask_data.shape[0] != image.shape[0]:
        show_info(
            "Number of frames doesn't match between image and masks layers."
        )
        return

    # Force les données en liste de frames pour unifier les cas
    if mask_data.ndim == 2:
        image = [image]
        mask_data = [mask_data]
    elif mask_data.ndim == 3:
        if mask_data.shape[0] != image.shape[0]:
            show_info(
                "Le nombre de frames ne correspond pas entre les images et les masques."
            )
            return
        # image_frames = image
        # mask_frames = mask_data
    else:
        show_info(f"Format non supporté : ndim = {mask_data.ndim}")
        return

    # Si aucune frame spécifiée, on prend tout
    if frame_indices is None:
        frame_indices = list(range(len(image)))
    print(type(frame_indices), frame_indices)

    saved = 0
    for i in frame_indices:
        if i < 0 or i >= len(image):
            print(f"Frame index {i} is out of range. Skipping.")
            continue

        img = image[i]
        msk = mask_data[i]

        if len(image) == 1:
            image_filename = os.path.join(save_path, f"{base_name}.tif")
            mask_filename = os.path.join(save_path, f"{base_name}_masks.tif")
        else:
            image_filename = os.path.join(
                save_path, f"{base_name}_frame{i}.tif"
            )
            mask_filename = os.path.join(
                save_path, f"{base_name}_frame{i}_masks.tif"
            )

        imwrite(image_filename, img.astype("uint16"))
        imwrite(mask_filename, msk.astype("uint16"))

        print(f"Frame {i} sauvegardée :")
        print(f"  -> Image : {image_filename}")
        print(f"  -> Masque : {mask_filename}")
        saved += 1

    show_info(f"{saved} image(s) et masque(s) sauvegardés dans :\n{save_path}")
