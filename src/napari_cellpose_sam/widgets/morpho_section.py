from qtpy.QtWidgets import QComboBox, QFormLayout, QGroupBox, QPushButton
from qtpy.QtCore import QTimer
from napari.utils.notifications import show_info


class MorphologyWidget(QGroupBox):
    def __init__(self, viewer):
        super().__init__("4. Others")
        self.viewer = viewer
        layout = QFormLayout()

        # Select label layer
        self.label_layer = QComboBox()
        layout.addRow("Select Label Layer:", self.label_layer)

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

        self.rename_btn.clicked.connect(self.rename_layer)

        self.setLayout(layout)
        self.refresh_labels_layers()

        # Refresh layer list when layers change
        self.viewer.layers.events.inserted.connect(self.refresh_labels_layers)
        self.viewer.layers.events.removed.connect(self.refresh_labels_layers)
        self.viewer.layers.events.changed.connect(self.refresh_labels_layers)

        # Initial refresh
        QTimer.singleShot(200, self.refresh_labels_layers)
        
    def refresh_labels_layers(self, event=None):
        self.label_layer.clear()

        for layer in self.viewer.layers:

            if layer._type_string == "labels":
                self.label_layer.addItem(layer.name, userData=layer)

    def rename_layer(self):
        selected_layer_name = self.label_layer.currentText()
        if selected_layer_name:
            layer = self.viewer.layers[selected_layer_name]
            layer.name = "committed_objects"
            show_info("Layer renamed to 'committed_objects'")
