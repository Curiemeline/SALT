from qtpy.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
)


class FinetuneWidget(QGroupBox):
    def __init__(self, viewer):
        super().__init__("3. Finetuning")
        self.viewer = viewer
        layout = QFormLayout()

        # Finetune folder
        folder_layout = QHBoxLayout()
        self.finetune_folder = QLineEdit()
        self.browse_finetune = QPushButton("Browse")
        folder_layout.addWidget(self.finetune_folder)
        folder_layout.addWidget(self.browse_finetune)
        layout.addRow("Finetune Folder:", folder_layout)

        # Select label layer
        self.label_layer = QComboBox()
        layout.addRow("Select Label Layer:", self.label_layer)

        # Frame range
        self.frames = QLineEdit()
        layout.addRow("Frames (e.g. 1-8):", self.frames)

        # Save masks
        self.save_masks_btn = QPushButton("Save Masks")
        layout.addRow(self.save_masks_btn)

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

        # Finetune button
        self.finetune_btn = QPushButton("Finetune")
        layout.addRow(self.finetune_btn)

        self.setLayout(layout)
        self.refresh_label_layers()

    def refresh_label_layers(self):
        self.label_layer.clear()
        label_layers = [
            layer.name
            for layer in self.viewer.layers
            if layer._type_string == "labels"
        ]
        self.label_layer.addItems(label_layers)
