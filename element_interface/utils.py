import pathlib
import uuid
import hashlib
import csv


def find_full_path(root_directories, relative_path):
    """
    Given a relative path, search and return the full-path
     from provided potential root directories (in the given order)
        :param root_directories: potential root directories
        :param relative_path: the relative path to find the valid root directory
        :return: full-path (pathlib.Path object)
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


def find_root_directory(root_directories, full_path):
    """
    Given multiple potential root directories and a full-path,
    search and return one directory that is the parent of the given path
        :param root_directories: potential root directories
        :param full_path: the full path to search the root directory
        :return: root_directory (pathlib.Path object)
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


def _to_Path(path):
    """
    Convert the input "path" into a pathlib.Path object
    Handles one odd Windows/Linux incompatibility of the "\\"
    """
    return pathlib.Path(str(path).replace("\\", "/"))


def dict_to_uuid(key):
    """
    Given a dictionary `key`, returns a hash string as UUID
    """
    hashed = hashlib.md5()
    for k, v in sorted(key.items()):
        hashed.update(str(k).encode())
        hashed.update(str(v).encode())
    return uuid.UUID(hex=hashed.hexdigest())


def ingest_csv_to_table(
    csvs,
    tables,
    verbose=True,
    skip_duplicates=True,
    ignore_extra_fields=True,
    allow_direct_insert=False,
):
    """
    Inserts data from a series of csvs into their corresponding table:
        e.g., ingest_csv_to_table(['./lab_data.csv', './proj_data.csv'],
                                 [lab.Lab(),lab.Project()]
    ingest_csv_to_table(csvs, tables, skip_duplicates=True)
        :param csvs: list of relative paths to CSV files.  CSV are delimited by commas.
        :param tables: list of datajoint tables with ()
        :param verbose: print number inserted (i.e., table length change)
        :param skip_duplicates: skip duplicate entries
        :param ignore_extra_fields: if a csv feeds multiple tables, the subset of
                                    columns not applicable to a table will be ignored
        :param allow_direct_insert: permit insertion into Imported and Computed tables
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


def recursive_search(key, dictionary):
    """
    Search through a nested dictionary for a key and returns its value.  If there are
    more than one key with the same name at different depths, the algorithm returns the
    value of the least nested key.

    recursive_search(key, dictionary)
        :param key: key used to search through a nested dictionary
        :param dictionary: nested dictionary
        :return a: value of the input argument `key`
    """
    if key in dictionary:
        return dictionary[key]
    for value in dictionary.values():
        if isinstance(value, dict):
            a = recursive_search(key, value)
            if a is not None:
                return a
    return None
