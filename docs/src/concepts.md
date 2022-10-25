# Concepts

## Software interoperability

While software versioning helps researchers keep track of changes over time, it often
makes sense to separate the interface from the pipeline itself. By collecting utilities
here in Element Interface, maintainers can keep up to date with the latest developments
across other packages, without causing issues in the respective Element.

## Element Features

### General utilities

`utils.find_full_path` and `utils.find_root_directory` are used 
across many Elements and Workflows to allow for the flexibility of providing 
one or more root directories in the user's config, and extrapolating from a relative
path at runtime.

`utils.ingest_csv_to_table` is used across didactic workflows to ingest from example
local CSV files into sets of manual tables. While researchers may wish to manually 
insert for day-to-day operations, it helps to have a more complete dataset when learning
how to use various Elements.

### Suite2p

This Element provides functions to independently run Suite2p's motion correction,
segmentation, and deconvolution steps. These functions currently work for single plane
tiff files. If running all Suite2p pre-processing steps concurrently, these functions
are not required and one can run `suite2p.run_s2p()`.

These wrapper functions were developed primarily because `run_s2p` cannot individually
run deconvolution using the `spikedetect` flag (
[Suite2p Issue #718](https://github.com/MouseLand/suite2p/issues/718)).

**Requirements**
+ [ops dictionary](https://suite2p.readthedocs.io/en/latest/settings.html)
+ [db dictionary](https://github.com/MouseLand/suite2p/blob/4b6c3a95b53e5581dbab1feb26d67878db866068/jupyter/run_pipeline_tiffs_or_batch.ipynb)

**Note:** The ops dictionary returned from the `motion_correction_suite2p` and
`segmentation_suite2p` functions is only a subset of the keys generated with the
`suite2p.default_ops()` function.

## Element Architecture

The functions for each acquisition and analysis package are stored within a separate
module.

- Acquisition packages: `scanimage_utils.py`
- Analysis packages:
  
    + `suite2p_loader.py`
  
    + `suite2p_trigger.py`
    
    + `caiman_loader.py`
    
    + `run_caiman.py`

- Data upload: `dandi.py` 

## Roadmap

Further development of this Element is community driven.  Upon user requests and based
on guidance from the Scientific Steering Group we will additional features to
this Element.