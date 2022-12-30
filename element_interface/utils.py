import pathlib
import uuid
import hashlib
import csv
from datajoint.table import Table
import logging

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
            print(
                f"\n---- Inserting {insert_len} entry(s) "
                + f"into {table.table_name} ----"
            )


def str_to_bool(value) -> bool:
    """Return whether the provided string represents true. Otherwise false.

    Args:
        value (any): Any input

    Returns:
        bool (bool): True if value in ("y", "yes", "t", "true", "on", "1")
    """
    # Due to distutils equivalent depreciation in 3.10
    # Adopted from github.com/PostHog/posthog/blob/master/posthog/utils.py
    if not value:
        return False
    return str(value).lower() in ("y", "yes", "t", "true", "on", "1")


def insert1_skip_full_duplicates(table: Table, entry: dict):
    """Insert one entry into a table, ignoring duplicates if all entries match.

    Duplicates on either primary or secondary attributes log existing entries. After
    validation, this functionality will be integrated into core DataJoint.

    Cases:
        0. New entry: insert as normal
        1. Entry has an exact match: return silently
        2. Same primary key, new secondary attributes: log warning with full entry
        3. New primary key, same secondary attributes: log warning with existing key

    Arguments:
        table (Table): datajoint Table object entry (dict): table entry as a dictionary
    """
    if table & entry:  # Test for 1. Return silently if exact match
        return

    existing_entry_via_secondary = table & {  # Test for Case 3
        k: v for k, v in entry.items() if k not in table.primary_key
    }
    if existing_entry_via_secondary:
        logger.warning(  # Log warning if secondary attribs already exist under diff key
            "Entry already exists with a different primary key:\n\t"
            + str(existing_entry_via_secondary.fetch1("KEY"))
        )
        return

    existing_entry_via_primary = table & {  # Test for 2, existing primary key
        k: v for k, v in entry.items() if k in table.primary_key
    }
    if existing_entry_via_primary:
        logger.warning(  # Log warning if existing primary key
            "Primary key already exists in the following entry:\n\t"
            + str(existing_entry_via_primary.fetch1())
        )
        return

    table.insert1(entry)  # Handles 0, full new entry
