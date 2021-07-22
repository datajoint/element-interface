# Data loaders for the DataJoint Elements 

+ This repository is a set of modules used for loading
 neurophyiological data into the
 [DataJoint Elements](https://github.com/datajoint/datajoint-elements).

+ See [DataJoint Elements](https://github.com/datajoint/datajoint-elements) for descriptions
 of the `elements` and `workflows` developed as part of this initiative.

# Architecture

+ The loaders for each acquisition and analysis package are stored within a separate module.

+ Acquisition packages
     + `scanimage_utils.py`

+ Analysis packages
     + `suite2p_loader.py`
     + `caiman_loader.py`

# Installation

+ Install `element-data-loader`
     ```
     pip install git+https://github.com/datajoint/element-data-loader.git
     ```

+ `element-data-loader` can also be used to install packages used for reading acquired data (e.g. `scanreader`) and running analysis (e.g. `CaImAn`).

+ If your workflow uses these packages, you should install them when you install `element-data-loader`.

+ Install `element-data-loader` with `scanreader`
     ```
     pip install "element-data-loader[scanreader] @ git+https://github.com/datajoint/element-data-loader"
     ```

+ Install `element-data-loader` with `sbxreader`
     ```
     pip install "element-data-loader[sbxreader] @ git+https://github.com/datajoint/element-data-loader"
     ```

+ Install `element-data-loader` with `Suite2p`
     ```
     pip install "element-data-loader[suite2p] @ git+https://github.com/datajoint/element-data-loader"
     ```

+ Install `element-data-loader` with `CaImAn` requires two separate commands
     ```
     pip install "element-data-loader[caiman_requirements] @ git+https://github.com/datajoint/element-data-loader"
     pip install "element-data-loader[caiman] @ git+https://github.com/datajoint/element-data-loader"
     ```

+ Install `element-data-loader` with multiple packages
     ```
     pip install "element-data-loader[caiman_requirements] @ git+https://github.com/datajoint/element-data-loader"
     pip install "element-data-loader[scanreader,sbxreader,suite2p,caiman] @ git+https://github.com/datajoint/element-data-loader"
     ```

# Usage

+ See the [workflow-calcium-imaging](https://github.com/datajoint/workflow-calcium-imaging) 
and [element-calcium-imaging](https://github.com/datajoint/element-calcium-imaging) 
repositories for example usage of `element-data-loader`.

+ ScanImage
     ```python
     import scanreader
     from element_data_loader import scanimage_utils

     # ScanImage file path
     scan_filepath = '<imaging_root_data_dir>/subject1/session0/<scan_filename>.tif'

     loaded_scan = scanreader.read_scan(scan_filepath)

     recording_time = scanimage_utils.get_scanimage_acq_time(loaded_scan)
     header = scanimage_utils.parse_scanimage_header(loaded_scan)
     ```

+ Suite2p
     ```python
     from element_data_loader import suite2p_loader

     # Directory containing Suite2p output
     output_dir = '<imaging_root_data_dir>/subject1/session0/suite2p'

     loaded_dataset = suite2p_loader.Suite2p(output_dir)
     ```

+ CaImAn
     ```python
     from element_data_loader import caiman_loader

     # Directory containing CaImAn output
     output_dir = '<imaging_root_data_dir>/subject1/session0/caiman'

     loaded_dataset = caiman_loader.CaImAn(output_dir)
     ```
