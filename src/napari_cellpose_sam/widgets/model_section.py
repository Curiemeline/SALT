from qtpy.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)


class ModelParamWidget(QGroupBox):
    def __init__(self):
        super().__init__("1. Model Parametrization")
        layout = QFormLayout()

        # Select Model
        self.model_select = QComboBox()
        self.model_select.addItems(["cpsam", "custom model"])
        layout.addRow("Select Model:", self.model_select)

        # Custom model path
        model_path_layout = QHBoxLayout()
        self.custom_model_path = QLineEdit()
        self.browse_model_btn = QPushButton("Browse")
        model_path_layout.addWidget(self.custom_model_path)
        model_path_layout.addWidget(self.browse_model_btn)
        layout.addRow("Custom Model Path:", model_path_layout)

        # Flow threshold
        self.flow_thresh = QDoubleSpinBox()
        self.flow_thresh.setDecimals(2)
        self.flow_thresh.setRange(-10.0, 10.0)
        self.flow_thresh.setValue(0.4)
        layout.addRow("Flow Threshold:", self.flow_thresh)

        # Cellprobs threshold
        self.cellprob_thresh = QDoubleSpinBox()
        self.cellprob_thresh.setDecimals(2)
        self.cellprob_thresh.setRange(-10.0, 10.0)
        self.cellprob_thresh.setValue(0.0)
        layout.addRow("Cellprobs Threshold:", self.cellprob_thresh)

        self.setLayout(layout)

    def get_model_params(self):
        """
        Retourne un dict avec tous les paramètres actuels du widget.
        """
        return {
            "model": self.model_select.currentText(),
            "custom_model_path": self.custom_model_path.text().strip(),
            "flow_threshold": self.flow_thresh.value(),
            "cellprob_threshold": self.cellprob_thresh.value(),
        }
