import os
import pathlib
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime
import numpy as np
import tifffile


class PrairieViewMeta:
    def __init__(self, prairieview_dir: str):
        """Initialize PrairieViewMeta loader class

        Args:
            prairieview_dir (str): string, absolute file path to directory containing PrairieView dataset
        """
        # ---- Search and verify CaImAn output file exists ----
        # May return multiple xml files. Only need one that contains scan metadata.
        self.prairieview_dir = Path(prairieview_dir)

        for file in self.prairieview_dir.glob("*.xml"):
            xml_tree = ET.parse(file)
            xml_root = xml_tree.getroot()
            if xml_root.find(".//Sequence"):
                self.xml_file = file
                self._xml_root = xml_root
                break
        else:
            raise FileNotFoundError(
                f"No PrarieView metadata .xml file found at {prairieview_dir}"
            )

        self._meta = None

    @property
    def meta(self):
        if self._meta is None:
            self._meta = _extract_prairieview_metadata(self.xml_file)
            # adjust for the different definition of "frames"
            # from the ome meta - "frame" refers to an image at a given scanning depth, time step combination
            # in the imaging pipeline - "frame" refers to video frames - i.e. time steps
            num_frames = self._meta.pop("num_frames") / self._meta["num_planes"]

            self._meta["num_frames"] = int(num_frames)

        return self._meta

    def get_prairieview_filenames(
        self, plane_idx=None, channel=None, return_pln_chn=False
    ):
        """
        Extract from metadata the set of tiff files specific to the specified "plane_idx" and "channel"
        Args:
            plane_idx: int - plane index
            channel: int - channel
            return_pln_chn: bool - if True, returns (filenames, plane_idx, channel), else returns `filenames`

        Returns: List[str] - the set of tiff files specific to the specified "plane_idx" and "channel"
        """
        if plane_idx is None:
            if self.meta["num_planes"] > 1:
                raise ValueError(
                    f"Please specify 'plane_idx' - Plane indices: {self.meta['plane_indices']}"
                )
            else:
                plane_idx = self.meta["plane_indices"][0]
        else:
            assert (
                plane_idx in self.meta["plane_indices"]
            ), f"Invalid 'plane_idx' - Plane indices: {self.meta['plane_indices']}"

        if channel is None:
            if self.meta["num_channels"] > 1:
                raise ValueError(
                    f"Please specify 'channel' - Channels: {self.meta['channels']}"
                )
            else:
                channel = self.meta["channels"][0]
        else:
            assert (
                channel in self.meta["channels"]
            ), f"Invalid 'channel' - Channels: {self.meta['channels']}"

        # single-plane ome.tif does not have "@index" under Frame to search for
        plane_search = f"/[@index='{plane_idx}']" if self.meta["num_planes"] > 1 else ""
        # ome.tif does have "@channel" under File regardless of single or multi channel
        channel_search = f"/[@channel='{channel}']"

        frames = self._xml_root.findall(
            f".//Sequence/Frame{plane_search}/File{channel_search}"
        )

        fnames = [f.attrib["filename"] for f in frames]
        return fnames if not return_pln_chn else (fnames, plane_idx, channel)

    def write_single_bigtiff(
        self,
        plane_idx=None,
        channel=None,
        output_prefix=None,
        output_dir="./",
        caiman_compatible=False,  # if True, save the movie as a single page (frame x height x width)
        overwrite=False,
    ):
        tiff_names, plane_idx, channel = self.get_prairieview_filenames(
            plane_idx=plane_idx, channel=channel, return_pln_chn=True
        )
        if output_prefix is None:
            output_prefix = os.path.commonprefix(tiff_names)
        output_tiff_fullpath = (
            Path(output_dir)
            / f"{output_prefix}_pln{plane_idx}_chn{channel}{'.ome' if not caiman_compatible else ''}.tif"
        )
        if output_tiff_fullpath.exists() and not overwrite:
            return output_tiff_fullpath

        if not caiman_compatible:
            with tifffile.TiffWriter(
                output_tiff_fullpath,
                bigtiff=True,
            ) as tiff_writer:
                try:
                    for input_file in tiff_names:
                        with tifffile.TiffFile(
                            self.prairieview_dir / input_file
                        ) as tffl:
                            assert len(tffl.pages) == 1
                            tiff_writer.write(
                                tffl.pages[0].asarray(),
                                metadata={
                                    "axes": "YX",
                                    "'fps'": self.meta["frame_rate"],
                                },
                            )
                except Exception as e:
                    raise Exception(f"Error in processing tiff file {input_file}: {e}")
        else:
            combined_data = []
            try:
                for input_file in tiff_names:
                    with tifffile.TiffFile(self.prairieview_dir / input_file) as tffl:
                        assert len(tffl.pages) == 1
                        combined_data.append(tffl.pages[0].asarray())
            except Exception as e:
                raise Exception(f"Error in processing tiff file {input_file}: {e}")

            combined_data = np.dstack(combined_data).transpose(
                2, 0, 1
            )  # (frame x height x width)

            tifffile.imwrite(
                output_tiff_fullpath,
                combined_data,
                metadata={"axes": "TYX", "'fps'": self.meta["frame_rate"]},
                bigtiff=True,
            )

        return output_tiff_fullpath


def _extract_prairieview_metadata(xml_filepath: str):
    xml_filepath = Path(xml_filepath)
    if not xml_filepath.exists():
        raise FileNotFoundError(f"{xml_filepath} does not exist")
    xml_tree = ET.parse(xml_filepath)
    xml_root = xml_tree.getroot()

    bidirectional_scan = False  # Does not support bidirectional
    roi = 0
    recording_start_time = xml_root.find(".//Sequence/[@cycle='1']").attrib.get("time")

    # Get all channels and find unique values
    channel_list = [
        int(channel.attrib.get("channel"))
        for channel in xml_root.iterfind(".//Sequence/Frame/File/[@channel]")
    ]
    channels = set(channel_list)
    n_channels = len(channels)
    n_frames = len(xml_root.findall(".//Sequence/Frame"))
    framerate = 1 / float(
        xml_root.findall('.//PVStateValue/[@key="framePeriod"]')[0].attrib.get("value")
    )  # rate = 1/framePeriod

    usec_per_line = (
        float(
            xml_root.findall(".//PVStateValue/[@key='scanLinePeriod']")[0].attrib.get(
                "value"
            )
        )
        * 1e6
    )  # Convert from seconds to microseconds

    scan_datetime = datetime.strptime(
        xml_root.attrib.get("date"), "%m/%d/%Y %I:%M:%S %p"
    )

    total_scan_duration = float(
        xml_root.findall(".//Sequence/Frame")[-1].attrib.get("relativeTime")
    )

    pixel_height = int(
        xml_root.findall(".//PVStateValue/[@key='pixelsPerLine']")[0].attrib.get(
            "value"
        )
    )
    # All PrairieView-acquired images have square dimensions (512 x 512; 1024 x 1024)
    pixel_width = pixel_height

    um_per_pixel = float(
        xml_root.find(
            ".//PVStateValue/[@key='micronsPerPixel']/IndexedValue/[@index='XAxis']"
        ).attrib.get("value")
    )

    um_height = um_width = float(pixel_height) * um_per_pixel

    # x and y coordinate values for the center of the field
    x_field = float(
        xml_root.find(
            ".//PVStateValue/[@key='currentScanCenter']/IndexedValue/[@index='XAxis']"
        ).attrib.get("value")
    )
    y_field = float(
        xml_root.find(
            ".//PVStateValue/[@key='currentScanCenter']/IndexedValue/[@index='YAxis']"
        ).attrib.get("value")
    )

    if (
        xml_root.find(
            ".//Sequence/[@cycle='2']/Frame/PVStateShard/PVStateValue/[@key='positionCurrent']/SubindexedValues/[@index='ZAxis']"
        )
        is None
    ):
        z_fields = np.float64(
            xml_root.find(
                ".//PVStateValue/[@key='positionCurrent']/SubindexedValues/[@index='ZAxis']/SubindexedValue"
            ).attrib.get("value")
        )
        n_depths = 1
        plane_indices = {0}
        assert z_fields.size == n_depths
        bidirection_z = False
    else:
        bidirection_z = (
            xml_root.find(".//Sequence").attrib.get("bidirectionalZ") == "True"
        )

        # One "Frame" per depth in the .xml file. Gets number of frames in first sequence
        planes = [
            int(plane.attrib.get("index"))
            for plane in xml_root.findall(".//Sequence/[@cycle='1']/Frame")
        ]
        plane_indices = set(planes)
        n_depths = len(plane_indices)

        z_controllers = xml_root.findall(
            ".//Sequence/[@cycle='2']/Frame/[@index='1']/PVStateShard/PVStateValue/[@key='positionCurrent']/SubindexedValues/[@index='ZAxis']/SubindexedValue"
        )

        # If more than one Z-axis controllers are found,
        # check which controller is changing z_field depth. Only 1 controller
        # must change depths.
        if len(z_controllers) > 1:
            z_repeats = []
            for controller in xml_root.findall(
                ".//Sequence/[@cycle='2']/Frame/[@index='1']/PVStateShard/PVStateValue/[@key='positionCurrent']/SubindexedValues/[@index='ZAxis']/"
            ):
                z_repeats.append(
                    [
                        float(z.attrib.get("value"))
                        for z in xml_root.findall(
                            ".//Sequence/[@cycle='2']/Frame/PVStateShard/PVStateValue/[@key='positionCurrent']/SubindexedValues/[@index='ZAxis']/SubindexedValue/[@subindex='{0}']".format(
                                controller.attrib.get("subindex")
                            )
                        )
                    ]
                )
            controller_assert = [
                not all(z == z_controller[0] for z in z_controller)
                for z_controller in z_repeats
            ]
            assert (
                sum(controller_assert) == 1
            ), "Multiple controllers changing z depth is not supported"

            z_fields = z_repeats[controller_assert.index(True)]

        else:
            z_fields = [
                z.attrib.get("value")
                for z in xml_root.findall(
                    ".//Sequence/[@cycle='2']/Frame/PVStateShard/PVStateValue/[@key='positionCurrent']/SubindexedValues/[@index='ZAxis']/SubindexedValue/[@subindex='0']"
                )
            ]

        assert (
            len(z_fields) == n_depths
        ), "Number of z fields does not match number of depths."

    metainfo = dict(
        num_fields=n_depths,
        num_channels=n_channels,
        num_planes=n_depths,
        num_frames=n_frames,
        num_rois=roi,
        x_pos=None,
        y_pos=None,
        z_pos=None,
        frame_rate=framerate,
        bidirectional=bidirectional_scan,
        bidirectional_z=bidirection_z,
        scan_datetime=scan_datetime,
        usecs_per_line=usec_per_line,
        scan_duration=total_scan_duration,
        height_in_pixels=pixel_height,
        width_in_pixels=pixel_width,
        height_in_um=um_height,
        width_in_um=um_width,
        fieldX=x_field,
        fieldY=y_field,
        fieldZ=z_fields,
        recording_time=recording_start_time,
        channels=list(channels),
        plane_indices=list(plane_indices),
    )

    return metainfo


def get_prairieview_metadata(ome_tif_filepath: str) -> dict:
    """Extract metadata for scans generated by Prairie View acquisition software.

    The Prairie View software generates one `.ome.tif` imaging file per frame
    acquired. The metadata for all frames is contained in one .xml file. This
    function locates the .xml file and generates a dictionary necessary to
    populate the DataJoint `ScanInfo` and `Field` tables. Prairie View works
    with resonance scanners with a single field. Prairie View does not support
    bidirectional x and y scanning. ROI information is not contained in the
    `.xml` file. All images generated using Prairie View have square dimensions(e.g. 512x512).

    Args:
        ome_tif_filepath: An absolute path to the .ome.tif image file.

    Raises:
        FileNotFoundError: No .xml file containing information about the acquired scan
            was found at path in parent directory at `ome_tif_filepath`.

    Returns:
        metainfo: A dict mapping keys to corresponding metadata values fetched from the
            .xml file.
    """

    # May return multiple xml files. Only need one that contains scan metadata.
    xml_files_list = pathlib.Path(ome_tif_filepath).parent.glob("*.xml")

    for file in xml_files_list:
        xml_tree = ET.parse(file)
        xml_file = xml_tree.getroot()
        if xml_file.find(".//Sequence"):
            break
    else:
        raise FileNotFoundError(
            f"No PrarieView metadata .xml file found at {pathlib.Path(ome_tif_filepath).parent}"
        )

    return _extract_prairieview_metadata(file)
