from qtpy.QtWidgets import QTabWidget, QVBoxLayout, QWidget, QGroupBox

from .widgets.new_analysis_section import NewAnalysisWidget
from .widgets.finetune_section import FinetuneWidget
from .widgets.model_section import ModelParamWidget
from .widgets.morpho_section import MorphologyWidget
from .widgets.segmentation_section import SegmentationWidget


class CellposeSAM(QWidget):
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        outer_layout = QVBoxLayout()
        main_group = QGroupBox("CellposeSAM (Cellpose-SAM Segmentation and Finetuning)")
        main_layout = QVBoxLayout()

        # New Analysis Widget (en haut)
        self.new_analysis_tab = NewAnalysisWidget(self.viewer)
        main_layout.addWidget(self.new_analysis_tab)

        # Tabs
        tabs = QTabWidget()
        self.model_tab = ModelParamWidget()
        self.seg_tab = SegmentationWidget(self.viewer, self.model_tab, new_analysis_widget=self.new_analysis_tab)
        self.finetune_tab = FinetuneWidget(self.viewer, new_analysis_widget=self.new_analysis_tab)
        self.morpho_tab = MorphologyWidget(self.viewer)

        tabs.addTab(self.model_tab, "Model Parametrization")
        tabs.addTab(self.seg_tab, "Segmentation")
        tabs.addTab(self.finetune_tab, "Finetuning")
        tabs.addTab(self.morpho_tab, "Others")

        main_layout.addWidget(tabs)
        main_group.setLayout(main_layout)
        outer_layout.addWidget(main_group)
        self.setLayout(outer_layout)