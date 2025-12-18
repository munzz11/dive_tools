import json
import os
from PIL import Image



def convert_dive2yolo(bounds, img_h, img_w):
    # Dive convention is x1, y1, x2, y2 (top left, bottom right)
    # Yolo convention is center x, center y, box width, box height,
    # all normalized by the image height and width
    x1, y1, x2, y2 = bounds

    bb_w = (x2 - x1)
    bb_h = (y2 - y1)

    cx = (x1 + bb_w/2)/img_w
    cy = (y1 + bb_h/2)/img_h
    bb_w = bb_w/img_w
    bb_h = bb_h/img_h

    return(cx, cy, bb_w, bb_h)

#### for json

class Feature:
    def __init__(self,feature_data):
        self.frame = feature_data['frame']
        self.flick = feature_data['flick']
        self.bounds = feature_data['bounds']
        self.attributes = feature_data['attributes']
        self.interpolate = feature_data['interpolate']
        self.keyframe = feature_data['keyframe']


class Track:
    def __init__(self,track_data):
        self.begin = track_data['begin']
        self.end = track_data['end']
        self.id = track_data['id']
        self.confPairs = track_data['confidencePairs']
        self.attributes = track_data['attributes']
        self.meta = track_data['meta']
        self.features = [Feature(f) for f in track_data["features"]]

class JSONData:
    def __init__(self, json_data):
        self.tracks = {str(k): Track(v) for k, v in json_data["tracks"].items()}
        self.groups = json_data.get("groups", {})
        self.version = json_data["version"]

    def get_track(self, track_num):
        return self.tracks.get(str(track_num))
    

    def make_labelfiles(self, path2oneimg, labels_path, frame_name_convtn):

        # get frame dimensions (assumed constant across video)
        img = Image.open(path2oneimg)
        img_w, img_h = img.size

        # parse json data
        for i in range(0,len(self.tracks)):

            # for every track in the video
            track = self.get_track(i)
            class_id = track.id
            class_name = track.confPairs[0][0]

            # for every feature in each track
            for j in track.features:
                # make path to label file
                frame = str(j.frame + 1).rjust(5,'0')
                filename = frame_name_convtn + frame + '.txt'
                fullpath = labels_path + filename

                try:
                    with open(fullpath, 'a+') as file:
                        cx, cy, bb_w, bb_h = convert_dive2yolo(j.bounds, img_h, img_w)
                        formatted_str = f"{class_id} {cx:.6f} {cy:.6f} {bb_w:.6f} {bb_h:.6f} \n"
                        file.write(formatted_str)
                except Exception as e:
                    print(f"There was an error writing to {fullpath} --> Error: {e}")

#### for csv


class CSVData:
    def __init__(self,csvData):
        csvData = csvData.strip()
        csvData = csvData.split(',')

        self.class_id = int(csvData[0])
        self.img_timestamp = csvData[1]
        self.frame = int(csvData[2])
        self.bounds = [int(csvData[3]), int(csvData[4]), int(csvData[5]), int(csvData[6])]
        self.conf = float(csvData[7])
        self.target_length = int(csvData[8])
        self.confPairs = csvData[-2:]


    def make_labelfiles(self, path2oneimg, labels_path, frame_name_convtn=None):

        # get frame dimensions (assumed constant across video)
        try:
            img = Image.open(path2oneimg)
            img_w, img_h = img.size
        except Exception as e:
            print(e)
            print("Couldn't open image to pull height and width")
            return  # Exit early if image can't be opened

        # make labels file path
        # If frame_name_convtn is None, use the image filename directly
        if frame_name_convtn is None:
            img_basename = os.path.splitext(os.path.basename(path2oneimg))[0]
            filename = img_basename + '.txt'
        else:
            frame = str(self.frame + 1).rjust(5,'0')
            filename = frame_name_convtn + frame + '.txt'
        fullpath = labels_path + filename

        try:
            with open(fullpath, 'a+') as file:
                cx, cy, bb_w, bb_h = convert_dive2yolo(self.bounds, img_h, img_w)
                formatted_str = f"{self.class_id} {cx:.6f} {cy:.6f} {bb_w:.6f} {bb_h:.6f} \n"
                file.write(formatted_str)
        except Exception as e:
            print(f"There was an error writing to {fullpath} --> Error: {e}")



