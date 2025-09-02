# # from qtpy.QtWidgets import QComboBox, QFormLayout, QGroupBox, QPushButton
# # from qtpy.QtCore import QTimer
# # from napari.utils.notifications import show_info


# # class MorphologyWidget(QGroupBox):
# #     def __init__(self, viewer):
# #         super().__init__("4. Others")
# #         self.viewer = viewer
# #         layout = QFormLayout()

# #         # Select label layer
# #         self.label_layer = QComboBox()
# #         layout.addRow("Select Label Layer:", self.label_layer)

# #         # Morphological operations
# #         self.rename_btn = QPushButton("Rename into committed_objects")
# #         self.erode_btn = QPushButton("Erode")
# #         self.dilate_btn = QPushButton("Dilate")
# #         self.open_btn = QPushButton("Open")
# #         self.close_btn = QPushButton("Close")

# #         layout.addRow(self.rename_btn)
# #         layout.addRow(self.erode_btn)
# #         layout.addRow(self.dilate_btn)
# #         layout.addRow(self.open_btn)
# #         layout.addRow(self.close_btn)

# #         self.rename_btn.clicked.connect(self.rename_layer)

# #         self.setLayout(layout)
# #         self.refresh_labels_layers()

# #         # Refresh layer list when layers change
# #         self.viewer.layers.events.inserted.connect(self.refresh_labels_layers)
# #         self.viewer.layers.events.removed.connect(self.refresh_labels_layers)
# #         self.viewer.layers.events.changed.connect(self.refresh_labels_layers)

# #         # Initial refresh
# #         QTimer.singleShot(200, self.refresh_labels_layers)

# #     def refresh_labels_layers(self, event=None):
# #         self.label_layer.clear()

# #         for layer in self.viewer.layers:

# #             if layer._type_string == "labels":
# #                 self.label_layer.addItem(layer.name, userData=layer)

# #     def rename_layer(self):
# #         selected_layer_name = self.label_layer.currentText()
# #         if selected_layer_name:
# #             layer = self.viewer.layers[selected_layer_name]
# #             layer.name = "committed_objects"
# #             show_info("Layer renamed to 'committed_objects'")

############## VERSION ADDING MORPHO OPERATION FOR REAL

from napari.utils.notifications import show_info
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QPushButton,
    QSpinBox,
)

from napari_cellpose_sam import morpho_ops


class MorphologyWidget(QGroupBox):
    def __init__(self, viewer):
        super().__init__("4. Others")
        self.viewer = viewer
        layout = QFormLayout()

        # Select label layer
        self.label_layer = QComboBox()
        layout.addRow("Select Label Layer:", self.label_layer)

        # Kernel size selector
        self.kernel_size_spin = QSpinBox()
        self.kernel_size_spin.setRange(1, 25)  # bornes raisonnables
        self.kernel_size_spin.setValue(3)  # valeur par défaut
        self.kernel_size_spin.setSingleStep(2)  # tailles impaires
        layout.addRow("Kernel size:", self.kernel_size_spin)

        # Morphological operations
        self.rename_btn = QPushButton("Rename into committed_objects")
        self.erode_btn = QPushButton("Erode (E)")
        self.dilate_btn = QPushButton("Dilate (D)")
        self.open_btn = QPushButton("Open (O)")
        self.close_btn = QPushButton("Close (L)")

        # Assign shortcuts
        self.erode_btn.setShortcut("E")
        self.dilate_btn.setShortcut("D")
        self.open_btn.setShortcut("O")
        self.close_btn.setShortcut("L")

        layout.addRow(self.rename_btn)
        layout.addRow(self.erode_btn)
        layout.addRow(self.dilate_btn)
        layout.addRow(self.open_btn)
        layout.addRow(self.close_btn)

        self.rename_btn.clicked.connect(self.rename_layer)
        self.erode_btn.clicked.connect(lambda: self.apply_morphology("erode"))
        self.dilate_btn.clicked.connect(
            lambda: self.apply_morphology("dilate")
        )
        self.open_btn.clicked.connect(lambda: self.apply_morphology("open"))
        self.close_btn.clicked.connect(lambda: self.apply_morphology("close"))

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
            morpho_ops.rename_layer(
                self.viewer, selected_layer_name, "committed_objects"
            )
            show_info("Layer renamed to 'committed_objects'")

    def apply_morphology(self, operation):
        selected_layer_name = self.label_layer.currentText()
        if not selected_layer_name:
            show_info("No label layer selected")
            return

        kernel_size = self.kernel_size_spin.value()
        morpho_ops.apply_opencv_morphology(
            self.viewer, selected_layer_name, operation, kernel_size
        )
        show_info(
            f"Applied {operation} (kernel={kernel_size}) to {selected_layer_name}"
        )
