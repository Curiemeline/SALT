from qtpy.QtWidgets import QFileDialog


def browse_file(line_edit):
    path, _ = QFileDialog.getOpenFileName()
    if path:
        line_edit.setText(path)


def browse_folder(line_edit):
    folder = QFileDialog.getExistingDirectory()
    if folder:
        line_edit.setText(folder)


def parse_frame_range(frame_range_str):
    # Accept format like "1-5" or "3" or "1,2,4-6"
    frames = []
    for part in frame_range_str.split(","):
        if "-" in part:
            start, end = part.split("-")
            frames.extend(range(int(start), int(end) + 1))
        else:
            frames.append(int(part))
    return frames
