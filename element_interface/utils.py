import csv
import hashlib
import logging
import os
import pathlib
import sys
import uuid
import json
import pickle
from datetime import datetime
from datajoint.utils import to_camel_case

logger = logging.getLogger("datajoint")


def find_full_path(root_directories: list, relative_path: str) -> pathlib.PosixPath:
    """Given a list of roots and a relative path, search and return the full-path

    Root directories are searched in the provided order

    Args:
        root_directories (list): potential root directories
        relative_path (str): the relative path to find the valid root directory

    Returns:
        full-path (pathlib.Path object)

    Raises:
        FileNotFoundError: No valid full path
    """
    relative_path = _to_Path(relative_path)

    if relative_path.exists():
        return relative_path

    # Turn to list if only a single root directory is provided
    if isinstance(root_directories, (str, pathlib.Path)):
        root_directories = [_to_Path(root_directories)]

    for root_dir in root_directories:
        if (_to_Path(root_dir) / relative_path).exists():
            return _to_Path(root_dir) / relative_path

    raise FileNotFoundError(
        "No valid full-path found (from {})"
        " for {}".format(root_directories, relative_path)
    )


def find_root_directory(root_directories: list, full_path: str) -> pathlib.PosixPath:
    """Given multiple potential root directories and a full-path, return parent root.

    Search and return one directory that is the parent of the given path.

    Args:
        root_directories (list): potential root directories
        full_path (str): the full path to search the root directory

    Returns:
        root_directory (pathlib.Path object)

    Raises:
        FileNotFoundError: Full path does not exist
        FileNotFoundError: No valid root directory
    """
    full_path = _to_Path(full_path)

    if not full_path.exists():
        raise FileNotFoundError(f"{full_path} does not exist!")

    # Turn to list if only a single root directory is provided
    if isinstance(root_directories, (str, pathlib.Path)):
        root_directories = [_to_Path(root_directories)]

    try:
        return next(
            _to_Path(root_dir)
            for root_dir in root_directories
            if _to_Path(root_dir) in set(full_path.parents)
        )

    except StopIteration:
        raise FileNotFoundError(
            "No valid root directory found (from {})"
            " for {}".format(root_directories, full_path)
        )


def _to_Path(path: str) -> pathlib.Path:
    """Convert the input "path" into a pathlib.Path object

    Handles one odd Windows/Linux incompatibility of the "\\"

    Args:
        path (str or pathlib.Path): path on disk
    """
    return pathlib.Path(str(path).replace("\\", "/"))


def dict_to_uuid(key: dict):
    """Given a dictionary `key`, returns a hash string as UUID

    Args:
        key (dict): Any python dictionary"""
    hashed = hashlib.md5()
    for k, v in sorted(key.items()):
        hashed.update(str(k).encode())
        hashed.update(str(v).encode())
    return uuid.UUID(hex=hashed.hexdigest())


def ingest_csv_to_table(
    csvs: list,
    tables: list,
    verbose: bool = True,
    skip_duplicates: bool = True,
    ignore_extra_fields: bool = True,
    allow_direct_insert: bool = False,
):
    """Inserts data from a series of csvs into their corresponding table:

    Example:
        > ingest_csv_to_table(['./lab_data.csv', './proj_data.csv'],
                                 [lab.Lab(),lab.Project()]

    Args:
        csvs (list): list of paths to CSV files relative to current directory.
            CSV are delimited by commas.
        tables (list): list of datajoint tables with terminal `()`
        verbose (bool): print number inserted (i.e., table length change)
        skip_duplicates (bool): skip duplicate entries. See DataJoint's `insert`
        ignore_extra_fields (bool): if a csv feeds multiple tables, the subset of
            columns not applicable to a table will be ignored. See DataJoint's `insert`
        allow_direct_insert (bool): permit insertion into Imported and Computed tables
            See DataJoint's `insert`.
    """
    for csv_filepath, table in zip(csvs, tables):
        with open(csv_filepath, newline="") as f:
            data = list(csv.DictReader(f, delimiter=","))
        if verbose:
            prev_len = len(table)
        table.insert(
            data,
            skip_duplicates=skip_duplicates,
            # Ignore extra fields because some CSVs feed multiple tables
            ignore_extra_fields=ignore_extra_fields,
            # Allow direct bc element-event uses dj.Imported w/o `make` funcs
            allow_direct_insert=allow_direct_insert,
        )
        if verbose:
            insert_len = len(table) - prev_len
            logger.info(
                f"\n---- Inserting {insert_len} entry(s) "
                + f"into {to_camel_case(table.table_name)} ----"
            )


def value_to_bool(value) -> bool:
    """Return whether the provided value represents true. Otherwise false.

    Args:
        value (str, bool, int): Any input

    Returns:
        bool (bool): True if value in ("y", "yes", "t", "true", "on", "1")
    """
    if not value:
        return False
    return str(value).lower() in ("y", "yes", "t", "true", "on", "1")


class QuietStdOut:
    """Context for quieting standard output, and setting datajoint loglevel to warning

    Used in pytest functions to render clear output showing only pass/fail

    Example:
        with QuietStdOut():
            table.delete(safemode=False)
    """

    def __enter__(self):
        self.prev_log_level = logger.level
        logger.setLevel(30)  # set DataJoint logger to warning
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, *args):
        logger.setLevel(self.prev_log_level)
        sys.stdout.close()
        sys.stdout = self._original_stdout


def memoized_result(uniqueness_dict: dict, output_directory: str):
    """
    This is a decorator factory designed to cache the results of a function based on its input parameters and the state of the output directory.
     If the function is called with the same parameters and the output files in the directory remain unchanged,
      it returns the cached results; otherwise, it executes the function and caches the new results along with metadata.

    Args:
        uniqueness_dict: a dictionary that would identify a unique function call
        output_directory: directory location for the output files

    Returns: a decorator to enable a function call to memoize/cached the resulting files

    Conditions for robust usage:
        - the "output_directory" is to store exclusively the resulting files generated by this function call only, not a shared space with other functions/processes
        - the "parameters" passed to the decorator captures the true and uniqueness of the arguments to be used in the decorated function call
    """

    def decorator(func):
        def wrapped(*args, **kwargs):
            output_dir = _to_Path(output_directory)
            input_hash = dict_to_uuid(uniqueness_dict)
            input_hash_fp = output_dir / f".{input_hash}.json"
            # check if results already exist (from previous identical run)
            output_dir_files_hash = dict_to_uuid(
                {
                    f.relative_to(output_dir).as_posix(): f.stat().st_size
                    for f in output_dir.rglob("*")
                    if f.name != f".{input_hash}.json"
                }
            )
            if input_hash_fp.exists():
                with open(input_hash_fp, "r") as f:
                    meta = json.load(f)
                if str(output_dir_files_hash) == meta["output_dir_files_hash"]:
                    logger.info(f"Existing results found, skip '{func.__name__}'")
                    with open(output_dir / f".{input_hash}_results.pickle", "rb") as f:
                        results = pickle.load(f)
                    return results
            # no results - trigger the run
            logger.info(f"No existing results found, calling '{func.__name__}'")
            start_time = datetime.utcnow()
            results = func(*args, **kwargs)

            with open(output_dir / f".{input_hash}_results.pickle", "wb") as f:
                pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)

            meta = {
                "output_dir_files_hash": dict_to_uuid(
                    {
                        f.relative_to(output_dir).as_posix(): f.stat().st_size
                        for f in output_dir.rglob("*")
                        if f.name != f".{input_hash}.json"
                    }
                ),
                "start_time": start_time,
                "completion_time": datetime.utcnow(),
            }
            with open(input_hash_fp, "w") as f:
                json.dump(meta, f, default=str)

            return results

        return wrapped

    return decorator
