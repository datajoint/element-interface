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


+ Suite2p wrapper functions for triggering analysis

     Each step of Suite2p (registration, segmentation and deconvolution) 
     can be run independently for single plane tiff files. The functions in this
     package will facilitate this process. Requirements include the [ops dictionary](
     https://suite2p.readthedocs.io/en/latest/settings.html) and db dictionary.
     These wrapper functions were developed primarily because `run_s2p` cannot 
     individually run deconvolution using the `spikedetect` flag 
     ([Suite2p Issue #718](https://github.com/MouseLand/suite2p/issues/718)).

     ```python
     from element_data_loader.suite2p_trigger import motion_correction_suite2p,
     segmentation_suite2p, deconvolution_suite2p
     from suite2p import default_ops

     ops = dict(default_ops(), nonrigid=False, two_step_registration=False)
     ```
     Details of db dictionary can be found [here](https://github.com/MouseLand/suite2p/blob/4b6c3a95b53e5581dbab1feb26d67878db866068/jupyter/run_pipeline_tiffs_or_batch.ipynb)

     ```python
     db = {
          'h5py': [], # single h5 file path
          'h5py_key': 'data',
          'look_one_level_down': False, # search for TIFFs in all subfolders 
          'data_path': ['/test_data'], # list of folders with tiffs                                    
          'subfolders': [], # choose subfolders of 'data_path'
          'fast-disk': '/test_data' # string path for storing binary file 
          }

     ops.update(do_registration=1, roidetect=False, spikedetect=False)
     registration_ops = motion_registration_suite2p(ops, db)

     registration_ops.update(do_registration=0, roidetect=True, spikedetect=False)
     segmentation_ops = segmentation_suite2p(registration_ops, db)

     segmentation_ops.update(do_registration=0, roidetect=False, spikedetect=True)
     spikes = deconvolution_suite2p(segmentation_ops, db)
     ```


+ CaImAn
     ```python
     from element_data_loader import caiman_loader

     # Directory containing CaImAn output
     output_dir = '<imaging_root_data_dir>/subject1/session0/caiman'

     loaded_dataset = caiman_loader.CaImAn(output_dir)
     ```