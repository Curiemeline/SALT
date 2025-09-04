# napari-cellpose-sam

[![License BSD-3](https://img.shields.io/pypi/l/napari-cellpose-sam.svg?color=green)](https://github.com/Curiemeline/napari-cellpose-sam/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-cellpose-sam.svg?color=green)](https://pypi.org/project/napari-cellpose-sam)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-cellpose-sam.svg?color=green)](https://python.org)
[![tests](https://github.com/Curiemeline/napari-cellpose-sam/workflows/tests/badge.svg)](https://github.com/Curiemeline/napari-cellpose-sam/actions)
[![codecov](https://codecov.io/gh/Curiemeline/napari-cellpose-sam/branch/main/graph/badge.svg)](https://codecov.io/gh/Curiemeline/napari-cellpose-sam)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-cellpose-sam)](https://napari-hub.org/plugins/napari-cellpose-sam)
[![npe2](https://img.shields.io/badge/plugin-npe2-blue?link=https://napari.org/stable/plugins/index.html)](https://napari.org/stable/plugins/index.html)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json)](https://github.com/copier-org/copier)

A simple plugin to segment your data using Cellpose-SAM and finetune it as you wish ! 

----------------------------------

This [napari] plugin was generated with [copier] using the [napari-plugin-template].

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/napari-plugin-template#getting-started

and review the napari docs for plugin developers:
https://napari.org/stable/plugins/index.html
-->
# Introduction

This Napari plugin was developed to simplify annotation, segmentation, and finetuning of Cellpose models directly within a graphical interface.
Combining strengths of Cellpose-SAM and SAM for Microscopy (microsam), it is designed for biologists, imaging engineers, and data scientists who want to unify their analysis pipeline without relying on the command line.

## Installation
### Local installation

1. Create a conda environment on python 3.10:

````
conda create -n cellpose-sam python=3.10
conda activate cellpose-sam
````

2. Fetch the code from this repository and move to the directory:

````
git clone https://github.com/Curiemeline/napari-cellpose-sam.git
cd napari-cellpose-sam
````

3. Install the plugin locally:

````
pip install -e ".[all]"
````
-e installs in dev mode, allowing modification in the code without needing to reinstall everytime.
.[all] installs dependencies defined in ```pyproject.toml```

4. Microsam install (done separately because only available on conda, refer to their document here) :

````
conda install -c conda-forge micro_sam
````

### Online installation (when plugin published on PyPi)

You can install `napari-cellpose-sam` via [pip]:

```
pip install napari-cellpose-sam
```

If napari is not already installed, you can install `napari-cellpose-sam` with napari and Qt via:

```
pip install "napari-cellpose-sam[all]"
```

To install latest development version :

```
pip install git+https://github.com/Curiemeline/napari-cellpose-sam.git
```

## Key Features

1. Create New Analysis
* Generates a tree structure given a root folder (raw/, segmented_frames/, segmented_stack/, finetune/).

2. 2D and 3D visualization
* Load images (single frame or 3D stack),
* Smooth navigation across z-stacks.

3. Segmentation
* Uses Cellpose-SAM or user's custom model,
* Segments 2D/3D images,
* Parameters adjustable through interface,
* Automatically saves masks into a clean directory structure,
* Automatically uses GPU if available.

4. Interactive Annotation
* Uses SAM for Microscopy (microsam),
* Adds rectangles, squares, circles, points, etc. to define regions of interest,
* Erases wrong labels,
* Saves each image/mask into finetune/ folder by default (custom path can be provided).

5. Finetuning
* Selects your annotations to finetune a Cellpose model,
* Parameters (epochs, learning rate, name) adjustable through interface,
* Launch training directly from Napari,
* Automatically uses GPU if available.


## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"napari-cellpose-sam" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[copier]: https://copier.readthedocs.io/en/stable/
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[napari-plugin-template]: https://github.com/napari/napari-plugin-template

[file an issue]: https://github.com/Curiemeline/napari-cellpose-sam/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
