import os
import pathlib
import subprocess

from dandi.upload import upload


def upload_to_dandi(
    data_directory: str,
    dandiset_id: str,
    staging: bool = True,
    working_directory: str = None,
    api_key: str = None,
    sync: bool = False,
    existing: str = "refresh",
    validation: str = "required",
    shell=True,  # without this param, subprocess interprets first arg as file/dir
):
    """Upload NWB files to DANDI Archive

    Args:
        data_directory (str): directory that contains source data
        dandiset_id (str): 6-digit zero-padded string
        staging (bool): If true, use staging server. If false, use production server.
        working_directory (str, optional): Dir in which to create symlinked dandiset.
            Must have write permissions to this directory. Default is current directory.
        api_key (str, optional): Provide the DANDI API key if not already in an
            environmental variable DANDI_API_KEY
        sync (str, optional): If True, delete all files in archive that are not present
            in the local directory.
        existing (str, optional): see full description from `dandi upload --help`
        validation (str, optional): [require|skip|ignore] see full description from `dandi upload --help`
    """

    working_directory = working_directory or "."

    if api_key is not None:
        os.environ["DANDI_API_KEY"] = api_key

    dandiset_directory = (
        pathlib.Path(working_directory) / str(dandiset_id)
    ).as_posix()

    dandiset_url = (
        f"https://gui-staging.dandiarchive.org/#/dandiset/{dandiset_id}"
        if staging
        else f"https://dandiarchive.org/dandiset/{dandiset_id}/draft"
    )

    subprocess.run(
        [
            "dandi",
            "download",
            "--download",
            "dandiset.yaml",
            "-o",
            working_directory,
            dandiset_url,
        ],
        shell=shell,
    )

    subprocess.run(
        [
            "dandi",
            "organize",
            "-d",
            dandiset_directory,
            data_directory,
            "--required-field",
            "subject_id",
            "--required-field",
            "session_id",
        ],
        shell=shell,
    )

    subprocess.run(["dandi", "validate", dandiset_directory], shell=shell)

    upload(
        paths=[dandiset_directory],
        dandi_instance="dandi-staging" if staging else "dandi",
        existing=existing,
        sync=sync,
        validation=validation,
    )
