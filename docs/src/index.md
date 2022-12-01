# Elements Interface for external analysis packages

DataJoint Element for interoperability with other software. DataJoint Elements
collectively standardize and automate data collection and analysis for neuroscience
experiments. Typical Elements are modular pipelines for data storage and processing with
corresponding database tables that can be combined with other Elements to assemble a
fully functional pipeline. Element Interface is home to a number of utilities that make
this possible. 

Element Interface provides a number of loaders and utility functions used across 
a number of other Elements.

- Calcium imaging loaders: Suite2p, CaImAn, PrairieView
  
- File management, see [`find_full_path` API](./api/element_interface/utils/#element_interface.utils.find_full_path)

- Data ingestion, see [`ingest_csv_to_table` API](./api/element_interface/utils/#element_interface.utils.ingest_csv_to_table)

Visit the [Concepts page](./concepts.md) for more information on these tools.
