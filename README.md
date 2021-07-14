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

```
pip install git+https://github.com/datajoint/element-data-loader.git
```

# Usage

+ See the [workflow-calcium-imaging](https://github.com/datajoint/workflow-calcium-imaging) 
and [element-calcium-imaging](https://github.com/datajoint/element-calcium-imaging) 
repositories for example usage of `element-data-loader`.

+ ScanImage
     ```python
     import scanreader
     from element_data_loader import scanimage_utils

     scan_filepath = '<imaging_root_data_dir>/subject1/session0/<scan_filename>.tif' # ScanImage file path
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
