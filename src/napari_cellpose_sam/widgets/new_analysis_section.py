from pathlib import Path
import os
import shutil

from qtpy.QtWidgets import (
    QGroupBox,
    QVBoxLayout,
    QFormLayout,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
)
from napari.utils.notifications import show_info
from napari.layers import Image

from napari_cellpose_sam.utils import create_analysis_structure, browse_folder


class NewAnalysisWidget(QGroupBox):
    def __init__(self, viewer):
        super().__init__("0. New Analysis")
        self.viewer = viewer
        self.analysis_dir = None

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.base_dir_edit = QLineEdit()
        self.browse_base_btn = QPushButton("Browse")
        self.browse_base_btn.clicked.connect(lambda: browse_folder(self.base_dir_edit))

        base_layout = QHBoxLayout()
        base_layout.addWidget(self.base_dir_edit)
        base_layout.addWidget(self.browse_base_btn)

        form_layout.addRow("Analysis Root Folder:", base_layout)

        self.new_analysis_btn = QPushButton("Create New Analysis")
        self.new_analysis_btn.clicked.connect(self.create_new_analysis)

        layout.addLayout(form_layout)
        layout.addWidget(self.new_analysis_btn)
        self.setLayout(layout)

    def browse_base_folder(self):
        folder = QFileDialog.getExistingDirectory()
        if folder:
            self.base_dir_edit.setText(folder)

    def create_new_analysis(self):
        if not self.viewer.layers:
            show_info("Please load a new image before creating a new analysis.")
            return

        image_layer = self.viewer.layers.selection.active
        if not image_layer or not isinstance(image_layer, Image):
            show_info("Please select an Image Layer.")
            return

        base_path = Path(self.base_dir_edit.text().strip())
        if not base_path.exists():
            show_info("Specified folder does not exist.")
            return

        basename = Path(image_layer.name).stem
        analysis_dir = create_analysis_structure(base_path, basename)

        # Copy image to raw/
        if hasattr(image_layer, "source") and getattr(image_layer.source, "path", None):
            try:
                raw_image_path = analysis_dir / "raw" / f"{basename}.tif"
                shutil.copy(image_layer.source.path, raw_image_path)
            except Exception as e:
                show_info(f"Error when copying image: {e}")

        self.analysis_dir = analysis_dir
        show_info(f"New analysis initialized in folder:{analysis_dir}")

    def get_analysis_dir(self):
        return self.analysis_dir
