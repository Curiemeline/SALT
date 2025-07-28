import os

import numpy as np
from cellpose import models
from tifffile import imwrite


def segment_image_stack(
    image_stack,
    model_type="cpsam",
    model_path=None,
    flow_threshold=0.4,
    cellprob_threshold=0.0,
    save_path=None,
    save_flows=False,
    save_outlines=False,
    save_cellprob=False,
):
    # Load model
    if model_type == "custom model" and model_path:
        model = models.CellposeModel(gpu=True, pretrained_model=model_path)
    else:
        model = models.CellposeModel(gpu=True)

    # Create output folder
    os.makedirs(save_path, exist_ok=True)

    for idx in range(image_stack.shape[0]):
        img = image_stack[idx]
        result = model.eval(
            img,
            # channels=[0, 0],
            flow_threshold=flow_threshold,
            cellprob_threshold=cellprob_threshold,
        )

        if len(result) == 4:
            masks, flows, styles, diams = result
        else:
            masks, flows, styles = result
            # diams = None

        # Save mask
        imwrite(
            os.path.join(save_path, f"mask_{idx:03d}.tif"),
            masks.astype(np.uint16),
        )

        # Optionally save other outputs
        if save_flows:
            imwrite(os.path.join(save_path, f"flow_{idx:03d}.tif"), flows[0])
        if save_outlines:
            imwrite(
                os.path.join(save_path, f"outlines_{idx:03d}.tif"), flows[2]
            )
        if save_cellprob:
            imwrite(
                os.path.join(save_path, f"cellprob_{idx:03d}.tif"), flows[1]
            )


def segment_single_slice(
    image,
    model_type="cpsam",
    model_path=None,
    flow_threshold=0.4,
    cellprob_threshold=0.0,
):
    if model_type == "custom model" and model_path:
        model = models.CellposeModel(gpu=True, pretrained_model=model_path)
    else:
        model = models.CellposeModel(gpu=True)

    result = model.eval(
        image,
        # channels=[0, 0],
        flow_threshold=flow_threshold,
        cellprob_threshold=cellprob_threshold,
    )

    if len(result) == 4:
        masks, flows, styles, diams = result
    else:
        masks, flows, styles = result
        # diams = None

    return masks, flows


def save_corrected_masks(viewer, label_layer_name, save_path, frame_indices):
    from pathlib import Path

    os.makedirs(save_path, exist_ok=True)
    layer = next(
        (layer for layer in viewer.layers if layer.name == label_layer_name),
        None,
    )
    if layer is None:
        return

    data = layer.data
    for idx in frame_indices:
        if idx < data.shape[0]:
            mask = data[idx].astype(np.uint16)
            outname = Path(save_path) / f"mask_{idx:03d}.tif"
            imwrite(str(outname), mask)
