import os
from pathlib import Path

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
from napari_cellpose_sam.utils import browse_file, browse_folder


class SegmentationWidget(QGroupBox):
    def __init__(self, viewer, model_tab, new_analysis_widget=None):
        super().__init__("2. Segmentation")
        self.viewer = viewer
        self.model_tab = model_tab
        self.new_analysis_widget = new_analysis_widget
        layout = QFormLayout()

        # Select Layer
        self.layer_select = QComboBox()
        layout.addRow("Select Layer:", self.layer_select)

        # Input file
        input_layout = QHBoxLayout()
        self.input_file = QLineEdit()
        self.browse_input = QPushButton("Browse")
        input_layout.addWidget(self.input_file)
        input_layout.addWidget(self.browse_input)
        layout.addRow("Input file:", input_layout)
        self.browse_input.clicked.connect(lambda: browse_file(self.input_file))

        # Save Path (optional)
        save_layout = QHBoxLayout()
        self.save_path = QLineEdit()
        self.browse_save = QPushButton("Browse")
        save_layout.addWidget(self.save_path)
        save_layout.addWidget(self.browse_save)
        layout.addRow("Save Path (optional):", save_layout)
        self.browse_save.clicked.connect(lambda: browse_folder(self.save_path))

        # Output checkboxes
        self.out_flows = QCheckBox("Output cell flows")
        self.out_outlines = QCheckBox("Output outlines")
        self.out_probs = QCheckBox("Output cell probabilities")
        layout.addRow(self.out_flows)
        layout.addRow(self.out_outlines)
        layout.addRow(self.out_probs)

        # Segmentation button
        self.segment_all_btn = QPushButton("Segment image")
        layout.addRow(self.segment_all_btn)
        self.setLayout(layout)

        self.segment_all_btn.clicked.connect(self.segment_image)
        self.viewer.layers.events.inserted.connect(self.refresh_layer_list)
        self.viewer.layers.events.removed.connect(self.refresh_layer_list)
        self.viewer.layers.events.changed.connect(self.refresh_layer_list)
        QTimer.singleShot(200, self.refresh_layer_list)

    def refresh_layer_list(self, event: Event = None):
        self.layer_select.clear()
        layers = [
            layer.name
            for layer in self.viewer.layers
            if isinstance(layer, Image)
        ]
        self.layer_select.addItems(layers)

    def segment_image(self):
        if self.layer_select.currentText() == "":
            show_info("No image layer selected.")
            return

        # Priorité : save_path > analysis_dir/segmented_frames/
        output_dir = self.save_path.text().strip()
        if not output_dir:
            if (
                self.new_analysis_widget
                and self.new_analysis_widget.get_analysis_dir()
            ):
                output_dir = (
                    Path(self.new_analysis_widget.get_analysis_dir())
                    / "segmented_frames"
                )
                os.makedirs(output_dir, exist_ok=True)
            else:
                show_info(
                    "No output path specified and no analysis initialized."
                )
                return

        layer_name = self.layer_select.currentText()
        base_name = os.path.splitext(layer_name)[0]

        image_layer = self.viewer.layers[layer_name]
        image = image_layer.data

        if image.ndim not in (2, 3):
            show_info(
                "Unsupported image format. Image must be 2D or 3D stack."
            )
            return

        model_params = self.model_tab.get_model_params()

        if image.ndim == 2:
            masks, flows = segment_single_slice(
                image,
                model_type=model_params["model"],
                model_path=model_params["custom_model_path"] or None,
                flow_threshold=model_params["flow_threshold"],
                cellprob_threshold=model_params["cellprob_threshold"],
            )
            # Conversion en niveaux de gris des flows
            flow_gray = np.dot(
                flows[0][..., :3], [0.2989, 0.5870, 0.1140]
            ).astype(np.uint8)

            imwrite(
                os.path.join(output_dir, f"{base_name}_masks.tif"),
                masks.astype(np.uint16),
            )
            self.viewer.add_labels(masks, name=f"{base_name}_Mask")

            if self.out_flows.isChecked():
                imwrite(
                    os.path.join(output_dir, f"{base_name}_flow.tif"), flows[0]
                )
                self.viewer.add_image(flow_gray, name=f"{base_name}_Flow")

            if self.out_probs.isChecked():
                imwrite(
                    os.path.join(output_dir, f"{base_name}_cellprob.tif"),
                    flows[2],
                )
                self.viewer.add_image(
                    flow_gray[2], name=f"{base_name}_CellProb"
                )

            if self.out_outlines.isChecked():
                outlines = masks_to_outlines(masks)
                imwrite(
                    os.path.join(output_dir, f"{base_name}_outlines.tif"),
                    outlines.astype(np.uint8) * 255,
                )
                self.viewer.add_labels(outlines, name=f"{base_name}_Outlines")

        else:
            # === 3D image ===
            # output_dir = os.path.join(output_dir, f"{base_name}_output")  # We don't wanna create a sub folder anymore as it is already created in the new alysis tree structure.
            # os.makedirs(output_dir, exist_ok=True)

            masks_list = []
            flows_list = [] if self.out_flows.isChecked() else None
            outlines_list = [] if self.out_outlines.isChecked() else None
            probs_list = [] if self.out_probs.isChecked() else None

            for idx in range(image.shape[0]):
                masks, flows = segment_single_slice(
                    image[idx],
                    model_type=model_params["model"],
                    model_path=model_params["custom_model_path"] or None,
                    flow_threshold=model_params["flow_threshold"],
                    cellprob_threshold=model_params["cellprob_threshold"],
                )

                # Conversion en niveaux de gris (pondération classique)
                flow_gray = np.dot(
                    flows[0][..., :3], [0.2989, 0.5870, 0.1140]
                ).astype(np.uint8)

                masks_list.append(masks)
                imwrite(
                    os.path.join(
                        output_dir, f"{base_name}_{idx:03d}_masks.tif"
                    ),
                    masks.astype(np.uint16),
                )

                if self.out_flows.isChecked():
                    flows_list.append(flow_gray)
                    print("flow gray", flow_gray.shape)
                    imwrite(
                        os.path.join(
                            output_dir, f"{base_name}_{idx:03d}_flow.tif"
                        ),
                        flow_gray,
                    )

                if self.out_outlines.isChecked():
                    outline = masks_to_outlines(masks)
                    outlines_list.append(outline.astype(np.uint8) * 255)
                    imwrite(
                        os.path.join(
                            output_dir, f"{base_name}_{idx:03d}_outlines.tif"
                        ),
                        outline.astype(np.uint8) * 255,
                    )

                if self.out_probs.isChecked():
                    probs_list.append(flows[2])
                    imwrite(
                        os.path.join(
                            output_dir, f"{base_name}_{idx:03d}_cellprob.tif"
                        ),
                        flows[2],
                    )

            # === Create 'stack' subfolder ===
            stack_dir = os.path.join(
                Path(output_dir).parent, "segmented_stacks"
            )
            os.makedirs(stack_dir, exist_ok=True)

            # === Save and display full stacks ===
            masks_stack = np.stack(masks_list)
            imwrite(
                os.path.join(stack_dir, f"{base_name}_mask_stack.tif"),
                masks_stack.astype(np.uint16),
            )
            self.viewer.add_labels(masks_stack, name=f"{base_name}_Mask")

            if self.out_flows.isChecked():
                flow_stack = np.stack(flows_list)
                imwrite(
                    os.path.join(stack_dir, f"{base_name}_flow_stack.tif"),
                    flow_stack,
                )
                self.viewer.add_image(flow_stack, name=f"{base_name}_Flow")

            if self.out_probs.isChecked():
                prob_stack = np.stack(probs_list)
                imwrite(
                    os.path.join(stack_dir, f"{base_name}_cellprob_stack.tif"),
                    prob_stack,
                )
                self.viewer.add_image(prob_stack, name=f"{base_name}_CellProb")

            if self.out_outlines.isChecked():
                outlines_stack = np.stack(outlines_list)
                imwrite(
                    os.path.join(stack_dir, f"{base_name}_outlines_stack.tif"),
                    outlines_stack.astype(np.uint8),
                )
                self.viewer.add_labels(
                    outlines_stack, name=f"{base_name}_Outlines"
                )
