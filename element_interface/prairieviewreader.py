import os
import glob
import xml.etree.ElementTree as ET
import numpy as np
from datetime import datetime




def get_pv_metadata(pvfile):
    
    xml_file = glob.glob1(os.path.split(pvfile)[0], "*.xml")[0]  # Returns 3 xml files. Only need one that contains scan metadata.

    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    bidirectional_scan = False  # Does not support bidirectional
    
    nfields = 1  # Always contains 1 field
    
    # Get all channels and find unique values
    channel_list = []
    channels = root.iterfind(".//Sequence/Frame/File/[@channel]")
    for channel in channels:
        channel_list.append(int(channel.attrib.get('channel')))
    nchannels = np.unique(channel_list).shape[0]
    
    # One "Frame" per depth. Gets number of frames in first sequence
    planes_list = []
    planes = root.findall(".//Sequence/[@cycle='1']/Frame")
    for plane in planes:
        planes_list.append(int(plane.attrib.get('index')))
    ndepths = np.unique(planes_list).shape[0]
    
    # Total frames are displayed as number of "cycles"
    nframes = int(root.findall('.//Sequence')[-1].attrib.get('cycle'))
    
    roi = 1
    
    x_coordinate = float(root.find(".//PVStateValue/[@key='currentScanCenter']/IndexedValue/[@index='XAxis']").attrib.get('value'))
    y_coordinate = float(root.find(".//PVStateValue/[@key='currentScanCenter']/IndexedValue/[@index='YAxis']").attrib.get('value'))
    z_coordinate = float(root.find(".//PVStateValue/[@key='positionCurrent']/SubindexedValues/[@index='ZAxis']/SubindexedValue/[@subindex='0']").attrib.get('value'))

    framerate = np.divide(1, float(root.findall('.//PVStateValue/[@key="framePeriod"]')[0].attrib.get('value')))   # rate = 1/framePeriod

    usec_per_line = float(root.findall(".//PVStateValue/[@key='scanLinePeriod']")[0].attrib.get('value')) * 1000

    scan_datetime = datetime.strptime(root.attrib.get('date'), "%m/%d/%Y %I:%M:%S %p")

    total_duration = float(root.findall(".//Sequence/Frame")[-1].attrib.get('relativeTime'))

    bidirectionalZ = bool(root.find(".//Sequence").attrib.get('bidirectionalZ'))

    px_height = int(root.findall(".//PVStateValue/[@key='pixelsPerLine']")[0].attrib.get('value'))
    px_width = px_height    # All PrairieView-acquired images have square dimensions (512 x 512; 1024 x 1024)
    
    um_per_pixel = float(root.find(".//PVStateValue/[@key='micronsPerPixel']/IndexedValue/[@index='XAxis']").attrib.get('value'))
    um_height = float(px_height) * um_per_pixel
    um_width = um_height    # All PrairieView-acquired images have square dimensions (512 x 512

    metainfo = dict(
        num_fields = nfields,
        num_channels = nchannels,
        num_planes = ndepths,
        num_frames = nframes,
        num_rois = roi,
        x_pos = x_coordinate,
        y_pos = y_coordinate,
        z_pos = z_coordinate,
        frame_rate = framerate,
        bidirectional = bidirectional_scan,
        bidirectional_z = bidirectionalZ,
        scan_datetime = scan_datetime,
        usecs_per_line = usec_per_line,
        scan_duration = total_duration, 
        height_in_pixels = px_height,
        width_in_pixels = px_width,
        height_in_um = um_height,
        width_in_um = um_width,
    )

    return metainfo