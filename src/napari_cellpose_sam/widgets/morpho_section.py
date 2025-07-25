from qtpy.QtWidgets import QComboBox, QFormLayout, QGroupBox, QPushButton


class MorphologyWidget(QGroupBox):
    def __init__(self, viewer):
        super().__init__("4. Others")
        self.viewer = viewer
        layout = QFormLayout()

        # Select label layer
        self.label_select = QComboBox()
        layout.addRow("Select Label Layer:", self.label_select)

        # Morphological operations
        self.rename_btn = QPushButton("Rename into committed_objects")
        self.erode_btn = QPushButton("Erode")
        self.dilate_btn = QPushButton("Dilate")
        self.open_btn = QPushButton("Open")
        self.close_btn = QPushButton("Close")

        layout.addRow(self.rename_btn)
        layout.addRow(self.erode_btn)
        layout.addRow(self.dilate_btn)
        layout.addRow(self.open_btn)
        layout.addRow(self.close_btn)

        self.setLayout(layout)
        self.refresh_label_layers()

    def refresh_label_layers(self):
        self.label_select.clear()
        label_layers = [
            layer.name
            for layer in self.viewer.layers
            if layer._type_string == "labels"
        ]
        self.label_select.addItems(label_layers)
