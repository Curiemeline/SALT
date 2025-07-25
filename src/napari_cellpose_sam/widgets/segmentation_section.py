from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)


class SegmentationWidget(QGroupBox):
    def __init__(self, viewer):
        super().__init__("2. Segmentation")
        self.viewer = viewer
        layout = QFormLayout()

        # Select Layer
        self.layer_select = QComboBox()
        layout.addRow("Select Layer:", self.layer_select)

        # Input folder
        input_layout = QHBoxLayout()
        self.input_folder = QLineEdit()
        self.browse_input = QPushButton("Browse")
        input_layout.addWidget(self.input_folder)
        input_layout.addWidget(self.browse_input)
        layout.addRow("Input Folder:", input_layout)

        # Save Path
        save_layout = QHBoxLayout()
        self.save_path = QLineEdit()
        self.browse_save = QPushButton("Browse")
        save_layout.addWidget(self.save_path)
        save_layout.addWidget(self.browse_save)
        layout.addRow("Save Path:", save_layout)

        # Output checkboxes
        self.out_flows = QCheckBox("Output cell flows")
        self.out_outlines = QCheckBox("Output outlines")
        self.out_probs = QCheckBox("Output cell probabilities")
        layout.addRow(self.out_flows)
        layout.addRow(self.out_outlines)
        layout.addRow(self.out_probs)

        # Segmentation buttons
        self.segment_current_btn = QPushButton("Segment current slice")
        self.segment_all_btn = QPushButton("Segment all slices")
        layout.addRow(self.segment_current_btn)
        layout.addRow(self.segment_all_btn)

        self.setLayout(layout)
        self.refresh_layer_list()

    def refresh_layer_list(self):
        self.layer_select.clear()
        layers = [
            layer.name
            for layer in self.viewer.layers
            if hasattr(layer, "data") and layer._type_string == "image"
        ]
        self.layer_select.addItems(layers)
