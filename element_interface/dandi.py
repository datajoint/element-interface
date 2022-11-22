import os
import subprocess
from dandi.download import download
from dandi.upload import upload


def upload_to_dandi(
    data_directory: str,
    dandiset_id: str,
    staging: bool = True,
    working_directory: str = None,
    api_key: str = None,
    sync: bool = False,
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
    """

    working_directory = working_directory or os.path.curdir

    if api_key is not None:
        os.environ["DANDI_API_KEY"] = api_key

    dandiset_directory = os.path.join(
        working_directory, str(dandiset_id)
    )  # enforce str


    dandiset_url = f"https://gui-staging.dandiarchive.org/#/dandiset/{dandiset_id}" if staging else f"https://dandiarchive.org/dandiset/{dandiset_id}/draft"

    download(dandiset_url, output_dir=working_directory)

    subprocess.run(
        ["nwbinspector", dandiset_directory, "--config", "dandi", "--report-file-path", os.path.join(dandiset_directory, 'nwbinspector.txt')], shell=True
    )

    subprocess.run(
        ["dandi", "organize", "-d", dandiset_directory, data_directory, "-f", "dry"],
        shell=True,  # without this param, subprocess interprets first arg as file/dir
    )

    subprocess.run(
        ["dandi", "organize", "-d", dandiset_directory, data_directory], shell=True
    )

    print(
        f"work_dir: {working_directory}\ndata_dir: {data_directory}\n"
        + f"dand_dir: {dandiset_directory}"
    )

    upload(
        paths=[dandiset_directory],
        dandi_instance="dandi-staging" if staging else "dandi",
        sync=sync,
    )
