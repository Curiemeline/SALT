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


# def apply_opencv_morphology(viewer, layer_name, operation):
#     layer = get_layer_data(viewer, layer_name)
#     if layer is None:
#         return

#     data = layer.data.astype(np.uint8)
#     kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

#     if operation == "erode":
#         result = cv2.erode(data, kernel, iterations=1)
#     elif operation == "dilate":
#         result = cv2.dilate(data, kernel, iterations=1)
#     elif operation == "open":
#         result = cv2.morphologyEx(data, cv2.MORPH_OPEN, kernel)
#     elif operation == "close":
#         result = cv2.morphologyEx(data, cv2.MORPH_CLOSE, kernel)
#     else:
#         raise ValueError("Unknown operation")

#     layer.data = result


def _apply_morpho_2d(data2d, operation, kernel_size=3):
    """Apply a morphological operation on a 2D mask (single object expected)."""
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (kernel_size, kernel_size)
    )

    if operation == "erode":
        return cv2.erode(data2d, kernel, iterations=1)
    elif operation == "dilate":
        return cv2.dilate(data2d, kernel, iterations=1)
    elif operation == "open":
        return cv2.morphologyEx(data2d, cv2.MORPH_OPEN, kernel)
    elif operation == "close":
        return cv2.morphologyEx(data2d, cv2.MORPH_CLOSE, kernel)
    else:
        raise ValueError(f"Unknown operation: {operation}")


def apply_opencv_morphology(viewer, layer_name, operation, kernel_size=3):
    """
    Apply morphology operation on 'current_object' layer.
    Works for both 2D and 3D (applied per frame if object present).
    """
    layer = get_layer_data(viewer, layer_name)
    if layer is None:
        return

    data = layer.data.astype(np.uint8)

    if data.ndim == 2:
        # Single 2D object
        result = _apply_morpho_2d(data, operation, kernel_size)

    elif data.ndim == 3:
        # 3D stack (apply frame by frame)
        result = np.zeros_like(data)
        for i in range(data.shape[0]):
            frame = data[i]
            if np.any(frame):  # Only process if object exists
                result[i] = _apply_morpho_2d(frame, operation, kernel_size)
            else:
                result[i] = frame  # Keep empty
    else:
        raise ValueError(f"Unsupported data dimension: {data.ndim}")

    layer.data = result
