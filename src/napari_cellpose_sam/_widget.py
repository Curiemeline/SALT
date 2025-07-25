from qtpy.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from .widgets.finetune_section import FinetuneWidget
from .widgets.model_section import ModelParamWidget
from .widgets.morpho_section import MorphologyWidget
from .widgets.segmentation_section import SegmentationWidget


class CellposeSAM(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        layout = QVBoxLayout()
        tabs = QTabWidget()

        self.model_tab = ModelParamWidget()
        self.seg_tab = SegmentationWidget(self.viewer, self.model_tab)
        self.finetune_tab = FinetuneWidget(self.viewer)
        self.morpho_tab = MorphologyWidget(self.viewer)

        tabs.addTab(self.model_tab, "Model Parametrization")
        tabs.addTab(self.seg_tab, "Segmentation")
        tabs.addTab(self.finetune_tab, "Finetuning")
        tabs.addTab(self.morpho_tab, "Others")

        layout.addWidget(tabs)
        self.setLayout(layout)
