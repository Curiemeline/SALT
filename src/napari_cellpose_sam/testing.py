import torch
from cellpose import models

print("CUDA available:", torch.cuda.is_available())
print("CUDA device count:", torch.cuda.device_count())
print("Current device:", torch.cuda.current_device())
print(
    "Device name:",
    torch.cuda.get_device_name(0) if torch.cuda.is_available() else "No GPU",
)

model = models.CellposeModel(gpu=True)

print("Model uses GPU:", model.gpu)
