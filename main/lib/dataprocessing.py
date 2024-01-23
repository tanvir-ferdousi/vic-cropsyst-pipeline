import geopandas as gpd
from pathlib import Path

def readFile(file_path):
    file_path_obj = Path(file_path)

    file_data = []
    if file_path_obj.is_file():
        with open(file_path) as file:
            for line in file:
                line = line.rstrip()
                file_data.append(line)
    else:
        print(f"Error: file {file_path} not found")
        exit(1)

    return file_data

def getMultiWsData(file_path, watershed_list):
    all_watershed_df = gpd.read_file(file_path)
    watershed_df = all_watershed_df[all_watershed_df['watershed'].isin(watershed_list)]
    return watershed_df

def getMultiWsCoords(file_path, watershed_list):
    all_watershed_df = gpd.read_file(file_path)
    watershed_df = all_watershed_df[all_watershed_df['watershed'].isin(watershed_list)]
    watershed_coords = watershed_df.Latitude.values + '_' +  watershed_df.Longitude.values
    return watershed_coords

def removePrefix(text, prefix):

    if len(prefix) == 0:
        return text

    if text.startswith(prefix):
        text = text[len(prefix):]

    return text

def removeSuffix(text, suffix):

    if len(suffix) == 0:
        return text

    if text.endswith(suffix):
        text = text[:-len(suffix)]

    return text
