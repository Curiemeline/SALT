import cv2
import numpy as np


def get_layer_data(viewer, name):
    for layer in viewer.layers:
        if layer.name == name:
            return layer
    return None


def rename_layer(viewer, old_name, new_name="committed_objects"):
    layer = get_layer_data(viewer, old_name)
    if layer:
        layer.name = new_name


def apply_opencv_morphology(viewer, layer_name, operation):
    layer = get_layer_data(viewer, layer_name)
    if layer is None:
        return

    data = layer.data.astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    if operation == "erode":
        result = cv2.erode(data, kernel, iterations=1)
    elif operation == "dilate":
        result = cv2.dilate(data, kernel, iterations=1)
    elif operation == "open":
        result = cv2.morphologyEx(data, cv2.MORPH_OPEN, kernel)
    elif operation == "close":
        result = cv2.morphologyEx(data, cv2.MORPH_CLOSE, kernel)
    else:
        raise ValueError("Unknown operation")

    layer.data = result
