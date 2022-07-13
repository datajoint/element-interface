# Changelog

Observes [Semantic Versioning](https://semver.org/spec/v2.0.0.html) standard and [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) convention.

## 0.2.1 - 2022-07-13
+ Add - Adopt `black` formatting
+ Add - Code of Conduct

## 0.2.0 - 2022-07-06
+ First release of `element-interface`.
+ Bugfix - Fix for `tifffile` import.
+ Add - Function `run_caiman` to trigger CNMF algorithm.
+ Add - Function `ingest_csv_to_table` to insert data from CSV files into tables.
+ Add - Function `recursive_search` to search through nested dictionary for a key.
+ Add - Function `upload_to_dandi` to upload Neurodata Without Borders file to the DANDI platform.
+ Update - Remove `extras_require` feature to allow this package to be published to PyPI.

## 0.1.0a1 - 2022-01-12
+ Change - Rename the package `element-data-loader` to `element-interface`.

## 0.1.0a0 - 2021-06-21
+ Add - Readers for: `ScanImage`, `Suite2p`, `CaImAn`.