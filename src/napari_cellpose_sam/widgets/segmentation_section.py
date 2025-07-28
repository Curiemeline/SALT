import os

import numpy as np
from cellpose.utils import masks_to_outlines
from napari.layers import Image
from napari.utils.events import Event
from napari.utils.notifications import show_info
from qtpy.QtCore import QTimer
from qtpy.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)
from tifffile import imwrite

from napari_cellpose_sam.segmentation import (
    segment_single_slice,
)
from napari_cellpose_sam.utils import browse_folder


class SegmentationWidget(QGroupBox):
    def __init__(self, viewer, model_tab):
        super().__init__("2. Segmentation")
        self.viewer = viewer
        self.model_tab = model_tab
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
        self.browse_input.clicked.connect(
            lambda: browse_folder(self.input_folder)
        )  # You need lambda: to call another function with arguments. If we don't use it, it will immediately execute browse_folder() when the widget is created, before clicking the button.
        # It creates an anonymous wrapper function that calls browse_folder with the input_folder as an argument.

        # Save Path
        save_layout = QHBoxLayout()
        self.save_path = QLineEdit()
        self.browse_save = QPushButton("Browse")
        save_layout.addWidget(self.save_path)
        save_layout.addWidget(self.browse_save)
        layout.addRow("Save Path:", save_layout)
        self.browse_save.clicked.connect(lambda: browse_folder(self.save_path))

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

        # Connect segmentation buttons
        self.segment_current_btn.clicked.connect(
            self.segment_current_slice
        )  # You don't need to pass a lambda because we pass the reference to a method of the class with NO ARGUMENTS.
        self.segment_all_btn.clicked.connect(
            self.segment_all_slices
        )  # Qt knows that when the button is clicked, just call this method.

        # Refresh layer list when layers change
        self.viewer.layers.events.inserted.connect(self.refresh_layer_list)
        self.viewer.layers.events.removed.connect(self.refresh_layer_list)

        # Initial refresh
        QTimer.singleShot(200, self.refresh_layer_list)

    def refresh_layer_list(self, event: Event = None):
        self.layer_select.clear()
        layers = [
            layer.name
            for layer in self.viewer.layers
            if isinstance(layer, Image)
        ]
        self.layer_select.addItems(layers)

    def segment_current_slice(self):
        if self.layer_select.currentText() == "":
            show_info("No image layer selected.")
            return

        output_dir = self.save_path.text().strip()
        if not output_dir:
            show_info("Please select a save path before segmenting.")
            return
        os.makedirs(output_dir, exist_ok=True)

        image_layer = self.viewer.layers[self.layer_select.currentText()]
        image = image_layer.data

        if image.ndim != 2:
            show_info(
                "Selected image is not a 2D slice. Use 'segment all slices' for 3D stacks."
            )
            return

        model_params = self.model_tab.get_model_params()

        masks, flows = segment_single_slice(
            image,
            model_type=model_params["model"],
            model_path=model_params["custom_model_path"] or None,
            flow_threshold=model_params["flow_threshold"],
            cellprob_threshold=model_params["cellprob_threshold"],
        )

        if self.out_flows.isChecked():
            imwrite(os.path.join(output_dir, "grads.tif"), flows[0])
            self.viewer.add_image(flows[0], name="Flow")

        if self.out_probs.isChecked():
            imwrite(os.path.join(output_dir, "cellprob.tif"), flows[2])
            self.viewer.add_image(flows[1], name="CellProb")

        self.viewer.add_labels(masks, name="mask")
        imwrite(os.path.join(output_dir, "mask.tif"), masks.astype(np.uint16))

        if self.out_outlines.isChecked():
            outlines = masks_to_outlines(masks)
            imwrite(
                os.path.join(output_dir, "outlines.tif"),
                outlines.astype(np.uint8) * 255,
            )
            self.viewer.add_labels(outlines, name="Outlines")

    def segment_all_slices(self):
        if self.layer_select.currentText() == "":
            show_info("No image layer selected.")
            return

        output_dir = self.save_path.text().strip()
        if not output_dir:
            show_info("Please select a save path before segmenting.")
            return
        os.makedirs(output_dir, exist_ok=True)

        image_layer = self.viewer.layers[self.layer_select.currentText()]
        image_stack = image_layer.data

        if image_stack.ndim != 3:
            show_info(
                "Selected image is not a stack. Use 'segment current slice' for 2D images."
            )
            return

        model_params = self.model_tab.get_model_params()

        masks_list = []
        flows_list = [] if self.out_flows.isChecked() else None
        outlines_list = [] if self.out_outlines.isChecked() else None
        probs_list = [] if self.out_probs.isChecked() else None

        from cellpose.utils import masks_to_outlines

        for idx in range(image_stack.shape[0]):
            masks, flows = segment_single_slice(
                image_stack[idx],
                model_type=model_params["model"],
                model_path=model_params["custom_model_path"] or None,
                flow_threshold=model_params["flow_threshold"],
                cellprob_threshold=model_params["cellprob_threshold"],
            )

            # Sauvegarde slice par slice
            imwrite(
                os.path.join(output_dir, f"mask_{idx:03d}.tif"),
                masks.astype(np.uint16),
            )
            masks_list.append(masks)

            if self.out_flows.isChecked():
                flows_list.append(flows[0])
                imwrite(
                    os.path.join(output_dir, f"flow_{idx:03d}.tif"), flows[0]
                )

            if self.out_outlines.isChecked():
                outline = masks_to_outlines(masks)
                outlines_list.append(outline.astype(np.uint8) * 255)
                imwrite(
                    os.path.join(output_dir, f"outline_{idx:03d}.tif"),
                    outline.astype(np.uint8) * 255,
                )

            if self.out_probs.isChecked():
                probs_list.append(flows[2])  # cell probability map
                imwrite(
                    os.path.join(output_dir, f"cellprob_{idx:03d}.tif"),
                    flows[2],
                )

        # Affichage empilé (1 seul slider Napari par type de donnée)

        if self.out_probs.isChecked():
            self.viewer.add_image(np.stack(probs_list), name="CellProb Stack")

        if self.out_flows.isChecked():
            self.viewer.add_image(np.stack(flows_list), name="Flow Stack")

        masks_stack = np.stack(
            masks_list
        )  # I put it here so that we see it above cellprob and flow stacks in napari. Purely visual.
        self.viewer.add_labels(masks_stack, name="Mask Stack")

        if self.out_outlines.isChecked():
            self.viewer.add_labels(
                np.stack(outlines_list).astype(np.uint8), name="Outlines Stack"
            )
