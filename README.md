# DataJoint Elements Interface for external analysis packages

+ This repository serves a few purposes:
     + Load neurophysiological data into the
 [DataJoint Elements](https://github.com/datajoint/datajoint-elements).
     + Trigger packages used for neurophysiological data processing.
     + Functions common to the DataJoint Elements (e.g. search directory tree for data files).

+ See [DataJoint Elements](https://github.com/datajoint/datajoint-elements) for descriptions
 of the `elements` and `workflows` developed as part of this initiative.

# Architecture

+ The functions for each acquisition and analysis package are stored within a separate module.

+ Acquisition packages
     + `scanimage_utils.py`

+ Analysis packages
     + `suite2p_loader.py`
     + `caiman_loader.py`
     + `run_caiman.py`

# Installation

+ Install `element-interface`:
     ```
     pip install element-interface
     ```

+ This package is to be used in combination with the other DataJoint Elements (e.g. `element-calcium-imaging`).  The installation of packages used for data processing (e.g. `Suite2p`) will be included within the respective DataJoint Element (e.g. `element-calcium-imaging`).

# Usage

+ See the [workflow-calcium-imaging](https://github.com/datajoint/workflow-calcium-imaging) 
and [element-calcium-imaging](https://github.com/datajoint/element-calcium-imaging) 
repositories for example usage of `element-interface`.

+ ScanImage
     ```python
     import scanreader
     from element_interface import scanimage_utils

     # ScanImage file path
     scan_filepath = '<imaging_root_data_dir>/subject1/session0/<scan_filename>.tif'

     loaded_scan = scanreader.read_scan(scan_filepath)

     recording_time = scanimage_utils.get_scanimage_acq_time(loaded_scan)
     header = scanimage_utils.parse_scanimage_header(loaded_scan)
     ```

+ Suite2p
     ```python
     from element_interface import suite2p_loader

     # Directory containing Suite2p output
     output_dir = '<imaging_root_data_dir>/subject1/session0/suite2p'

     loaded_dataset = suite2p_loader.Suite2p(output_dir)
     ```

+ CaImAn
     ```python
     from element_interface import caiman_loader

     # Directory containing CaImAn output
     output_dir = '<imaging_root_data_dir>/subject1/session0/caiman'

     loaded_dataset = caiman_loader.CaImAn(output_dir)
     ```
