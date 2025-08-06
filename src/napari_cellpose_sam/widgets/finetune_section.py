import os
from qtpy.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QGroupBox, QHBoxLayout,
    QLineEdit, QPushButton, QSpinBox
)
from napari.utils.notifications import show_info
from napari_cellpose_sam.utils import browse_folder, save_img_masks
from tifffile import imwrite
from napari_cellpose_sam.finetuning import save_loss_curve, split_train_test, finetune_cellpose

from pathlib import Path

class FinetuneWidget(QGroupBox):
    def __init__(self, viewer, new_analysis_widget=None):
        super().__init__("3. Finetuning")
        self.viewer = viewer
        self.new_analysis_widget = new_analysis_widget
        layout = QFormLayout()

        # Folder path + browse
        folder_layout = QHBoxLayout()
        self.finetune_folder = QLineEdit()
        self.browse_finetune = QPushButton("Browse")
        folder_layout.addWidget(self.finetune_folder)
        folder_layout.addWidget(self.browse_finetune)
        layout.addRow("Finetune Folder (optional):", folder_layout)
        self.browse_finetune.clicked.connect(
            lambda: browse_folder(self.finetune_folder)
        )

        # Select image and label layers
        self.image_layer = QComboBox()
        layout.addRow("Select Image Layer:", self.image_layer)

        self.label_layer = QComboBox()
        layout.addRow("Select Label Layer:", self.label_layer)

        # Frame range
        self.frames = QLineEdit()
        layout.addRow("Frames (e.g. 1-8):", self.frames)

        # Save masks button
        self.save_masks_btn = QPushButton("Save Masks")
        layout.addRow(self.save_masks_btn)
        self.save_masks_btn.clicked.connect(self.save_masks)

        # Epochs
        self.epochs = QSpinBox()
        self.epochs.setRange(1, 1000)
        self.epochs.setValue(100)
        layout.addRow("Epochs:", self.epochs)

        # Learning rate
        self.lr = QDoubleSpinBox()
        self.lr.setDecimals(5)
        self.lr.setRange(0.00001, 1.0)
        self.lr.setValue(0.001)
        layout.addRow("Learning Rate:", self.lr)

        # Model name
        self.model_name = QLineEdit()
        layout.addRow("Model Name:", self.model_name)

        # Finetune button
        self.finetune_btn = QPushButton("Finetune")
        layout.addRow(self.finetune_btn)
        self.finetune_btn.clicked.connect(self.launch_finetuning)

        self.setLayout(layout)
        self.refresh_layer_lists()

        # Auto-refresh layer lists
        self.viewer.layers.events.inserted.connect(self.refresh_layer_lists)
        self.viewer.layers.events.removed.connect(self.refresh_layer_lists)

    def refresh_layer_lists(self, event=None):
        self.image_layer.clear()
        self.label_layer.clear()

        for layer in self.viewer.layers:
            if layer._type_string == "image":
                self.image_layer.addItem(layer.name, userData=layer)
            elif layer._type_string == "labels":
                self.label_layer.addItem(layer.name, userData=layer)

    def parse_frames(self):
        """Parse text like '1-4' and return [1, 2, 3, 4]."""
        text = self.frames.text().strip()
        if not text:
            return None  # No restriction
        try:
            start, end = map(int, text.split('-'))
            return list(range(start, end + 1))
        except Exception as e:
            print(f"Invalid frame format '{text}': {e}")
            return None

    def get_finetune_dir(self):
        folder = self.finetune_folder.text().strip()
        if folder:
            return Path(folder)

        # Si pas de chemin explicite, essayer de récupérer depuis le root folder
        if self.new_analysis_widget and self.new_analysis_widget.analysis_dir:
            return self.new_analysis_widget.analysis_dir / "finetune"

        return None

    def save_masks(self):
        save_path = self.get_finetune_dir()
        if not save_path:
            show_info("No valid finetune path found.")
            return

        img_layer = self.image_layer.currentData()
        label_layer = self.label_layer.currentData()

        if img_layer is None or label_layer is None:
            show_info("Please select both image and label layers.")
            return

        frame_indices = self.parse_frames()
        save_img_masks(self.viewer, img_layer, label_layer, save_path, frame_indices)
        
    def split_dataset(self):
        folder = self.get_finetune_dir()
        if not folder:
            show_info("Please specify a finetune folder or create a new analysis.")
            return

        train_dir, test_dir = split_train_test(folder)
        show_info(f"Dataset split into:\nTrain: {train_dir}\nTest: {test_dir}")

    def launch_finetuning(self):
        folder = self.get_finetune_dir()
        model_name = self.model_name.text().strip()

        if folder is None:
            show_info("Please specify a finetune folder or create a new analysis.")
            return

        if not model_name:
            show_info("Please enter a model name.")
            return

        epochs = self.epochs.value()
        learning_rate = self.lr.value()
        frames = self.parse_frames()

        print("Launching finetuning with parameters:")
        print(f"  Folder: {folder}")
        print(f"  Model Name: {model_name}")
        print(f"  Epochs: {epochs}")
        print(f"  Learning Rate: {learning_rate}")
        print(f"  Frames: {frames if frames else 'All'}")

        self.split_dataset()

        model_path, train_losses, test_losses = finetune_cellpose(
            output_path=folder,
            epochs=epochs,
            lr=learning_rate,
            model_name=model_name
        )
        print("curve saved to: ",folder.parent / "models")
        save_loss_curve(folder.parent / "models", train_losses, test_losses, model_name)
        show_info(f"Finetuning completed. Model saved to {folder.parent}/models")
        print("Model saved to:", f"{folder.parent}/models")
















# # from qtpy.QtWidgets import (
# #     QComboBox,
# #     QDoubleSpinBox,
# #     QFormLayout,
# #     QGroupBox,
# #     QHBoxLayout,
# #     QLineEdit,
# #     QPushButton,
# #     QSpinBox,
# # )
# # from napari.utils.events import Event
# # from napari.layers import Image, Labels

# # from napari_cellpose_sam.utils import browse_folder, save_masks


# # class FinetuneWidget(QGroupBox):
# #     def __init__(self, viewer):
# #         super().__init__("3. Finetuning")
# #         self.viewer = viewer
# #         layout = QFormLayout()

# #         # Finetune folder
# #         folder_layout = QHBoxLayout()
# #         self.finetune_folder = QLineEdit()
# #         self.browse_finetune = QPushButton("Browse")
# #         folder_layout.addWidget(self.finetune_folder)
# #         folder_layout.addWidget(self.browse_finetune)
# #         layout.addRow("Finetune Folder:", folder_layout)
# #         self.browse_finetune.clicked.connect(
# #             lambda: browse_folder(self.finetune_folder)
# #         )

# #         # Select image layer
# #         self.image_layer = QComboBox()
# #         layout.addRow("Select Image Layer:", self.image_layer)

# #         # Select label layer
# #         self.label_layer = QComboBox()
# #         layout.addRow("Select Label Layer:", self.label_layer)

# #         # Frame range
# #         self.frames = QLineEdit()
# #         layout.addRow("Frames (e.g. 1-8):", self.frames)

# #         # Save masks
# #         self.save_masks_btn = QPushButton("Save Masks")
# #         layout.addRow(self.save_masks_btn)
# #         self.save_masks_btn.clicked.connect(lambda: save_masks(self.viewer, self.image_layer, self.label_layer, self.finetune_folder, self.frames))
        
# #         # Epochs
# #         self.epochs = QSpinBox()
# #         self.epochs.setRange(1, 1000)
# #         self.epochs.setValue(100)
# #         layout.addRow("Epochs:", self.epochs)

# #         # Learning rate
# #         self.lr = QDoubleSpinBox()
# #         self.lr.setDecimals(5)
# #         self.lr.setRange(0.00001, 1.0)
# #         self.lr.setValue(0.001)
# #         layout.addRow("Learning Rate:", self.lr)

# #         # Finetune button
# #         self.finetune_btn = QPushButton("Finetune")
# #         layout.addRow(self.finetune_btn)

# #         self.setLayout(layout)
# #         self.refresh_layer_list()
        
# #         # Refresh when label layers are added or removed
# #         self.viewer.layers.events.inserted.connect(self.refresh_layer_list)
# #         self.viewer.layers.events.removed.connect(self.refresh_layer_list)
# #         self.viewer.layers.events.changed.connect(self.refresh_layer_list)

# #     # def refresh_label_layers(self, event=None):
# #     #     self.label_layer.clear()
# #     #     label_layers = [
# #     #         layer.name
# #     #         for layer in self.viewer.layers
# #     #         if layer._type_string == "labels"
# #     #     ]
# #     #     self.label_layer.addItems(label_layers)

# #     def refresh_layer_list(self, event: Event = None):
# #         self.image_layer.clear()
# #         self.label_layer.clear()
# #         img_layers = [
# #             layer.name
# #             for layer in self.viewer.layers
# #             if isinstance(layer, Image)
# #         ]
# #         lbl_layers = [
# #             layer.name
# #             for layer in self.viewer.layers
# #             if isinstance(layer, Labels)
# #         ]
# #         self.image_layer.addItems(img_layers)
# #         self.label_layer.addItems(lbl_layers)
