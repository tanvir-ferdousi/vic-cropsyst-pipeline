from pathlib import Path
from sys import exit
import os, shutil
import geopandas as gpd
import argparse

from lib.dataprocessing import readFile

def readClas():
    """
    Reads the command line arguments
    :return:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--splitSize', type=int, dest='splitSize', required=False, default=5)
    parser.add_argument('--runId', type=int, dest='runId', required=False)
    parser.add_argument('--coordListFile', type=str, dest='coordListFile', required=True)
    parser.add_argument('--resultDir', type=str, dest='resultDir', required=True)



    args = parser.parse_args()

    return args


def getWatershedCoords(file_path, target_watershed):
    all_watershed_df = gpd.read_file(file_path)
    watershed_df = all_watershed_df[all_watershed_df.watershed == target_watershed]
    watershed_coords = watershed_df.Latitude.values + '_' +  watershed_df.Longitude.values
    return watershed_coords

def clearDir(dir_path):

    for file_name in os.listdir(dir_path):

        file_path = os.path.join(dir_path, file_name)

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def checkAndClearDir(dir_path, clear_dir):
    if not Path(dir_path).is_dir():
        print(f'Error: the directory {dir_path} does not exist')
        exit(1)
    else:
        if clear_dir:
            clearDir(dir_path)


def checkMakeAndClearDir(dir_path, clear_dir):
    if not Path(dir_path).is_dir():
        print(f'The directory {dir_path} does not exist')
        os.makedirs(dir_path)
    else:
        print(f'The directory {dir_path} exists')
        if clear_dir:
            print('Clearing data')
            clearDir(dir_path)

def replaceText(old_data, old_txt, new_txt):
    new_data = []
    for line in old_data:
        line = line.replace(old_txt, new_txt)
        new_data.append(line)
    return new_data

# def readFile(file_path):
#
#     file_path_obj = Path(file_path)
#
#     file_data = []
#     if file_path_obj.is_file():
#         with open(file_path) as file:
#             for line in file:
#                 line = line.rstrip()
#                 file_data.append(line)
#     else:
#         print(f"Error: file {file_path} not found")
#         exit(1)
#
#     return file_data


# def readFile(file_path, replace_txt=False, old_txt='', new_txt=''):
#
#     file_path_obj = Path(file_path)
#
#     file_data = []
#     if file_path_obj.is_file():
#         with open(file_path) as file:
#             for line in file:
#                 line = line.rstrip()
#                 if replace_txt:
#                     line = line.replace(old_txt, new_txt)
#                     # line = line.replace() <REPLACE_RUNID>
#                 file_data.append(line)
#                 # print(f'Line {count}: {line.rstrip().split(" ")}\n')
#     else:
#         print(f"Error: file {file_path} not found")
#         exit(1)
#
#     return file_data


def writeFile(out_file, file_data, replace_txt = False, old_txt = '', new_txt = ''):

    with open(out_file, 'w') as file_handle:

        for line in file_data:
            if replace_txt:
                line = line.replace(old_txt, new_txt)

            file_handle.write(line + '\n')

def writeSubSoilFiles(soil_path_prefix, soil_data, split_size):
    fileIdx = 0
    for idx in range(0, len(soil_data), split_size):
        fileName = soil_path_prefix + str(fileIdx) + '.txt'
        writeFile(fileName, soil_data[idx:idx+split_size])
        fileIdx += 1

    return fileIdx

def writeSubControlFiles(control_path_prefix, soil_path_prefix, control_data, n_segments):

    for fileIdx in range(0, n_segments):
        fileName = control_path_prefix + str(fileIdx) + '.txt'
        old_txt = '<REPLACE_SOILFILE>'
        new_txt = soil_path_prefix + str(fileIdx) + '.txt'

        writeFile(fileName, control_data, True, old_txt, new_txt)

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

def getCoordinatesFromSingleGrid(soil_line):
    lat = soil_line.split()[2]
    lon = soil_line.split()[3]
    return lat+'_'+lon

def getSoilCoords(soil_data):
    coord_list = []
    for grid_line in soil_data:
        lat = grid_line.split()[2]
        lon = grid_line.split()[3]
        coord_list.append(lat+'_'+lon)
    return coord_list

def getCoordinatesFromForcingFiles(file_names, file_prefix, file_suffix):

    coord = []
    for file in file_names:
        # print(file)
        try:
            file = removePrefix(file, file_prefix)
            file = removeSuffix(file, file_suffix)
            # lat, lon = file.split('_')
            # coord.append([float(lon), float(lat)])
            coord.append(file)
        except:
            print(file)

    return coord

def getForcingCoords(forcing_list_path):
    forcing_file_names = readFile(forcing_list_path)
    forcing_coords = getCoordinatesFromForcingFiles(forcing_file_names, 'data_', '')
    return forcing_coords

def prepare_input_data(target_coords, forcing_coords, split_size, soil_file_in, soil_dir_out, control_file_in, control_dir_out, forcing_dir, result_dir):

    soil_file_prefix = 'segment_'
    soil_path_prefix = soil_dir_out + soil_file_prefix

    control_file_prefix = 'vic_control_segment_'
    control_path_prefix = control_dir_out + control_file_prefix

    print('Check and clear soil/control directories')
    # pre-run checks
    checkMakeAndClearDir(soil_dir_out, True)
    checkMakeAndClearDir(control_dir_out, True)

    # read soil file
    print('Read soil files')
    soil_data = readFile(soil_file_in)
    soil_coord = getSoilCoords(soil_data)

    common_grids = list(set(target_coords) & set(soil_coord) & set(forcing_coords))

    filtered_soil_data = [soil_line for soil_line in soil_data if getCoordinatesFromSingleGrid(soil_line) in common_grids]

    print('Write sub-soil files')
    n_segments = writeSubSoilFiles(soil_path_prefix, filtered_soil_data, split_size)

    control_data = readFile(control_file_in)

    old_txt = '<REPLACE_RESULTS_PATH>'
    new_txt = result_dir
    control_data = replaceText(control_data, old_txt, new_txt)

    old_txt = '<REPLACE_FORCING>'
    new_txt = forcing_dir
    control_data = replaceText(control_data, old_txt, new_txt)

    print('Write sub-control files')
    writeSubControlFiles(control_path_prefix, soil_path_prefix, control_data, n_segments)


def main():

    args = readClas()

    split_size = args.splitSize

    # watershed_list_file = args.watershedListFile
    coord_list_file = args.coordListFile
    result_dir = args.resultDir

    # run_id = args.runId

    print(f'Split size: {split_size}')
    # print(f'Run id: {run_id}')

    forcing_list_path = '../../input_files/static/forcing_file_list.txt'
    # watershed_data_file = 'data/VIC_gridcode_latlong_area_watershed.csv'

    soil_file_in = '/project/nssac_agaid/vic_cropsyst/data/ForVirginia/for_run_VIC_CropSyst/VIC-CropSyst/Simulation/Database/Soil/all_calibrated_plus_uncalibrated_soil_210106.txt'
    soil_dir_out = '../../input_files/dynamic/basic_run/SoilSplits'

    control_file_in = '../../input_files/static/vic_control.txt'
    control_dir_out = '../../input_files/dynamic/basic_run/SimSplits'

    # forcing_dir = '/scratch/jcr5wj/agaid/forcing/input_data_mod/' + 'run' + str(run_id) + '/data_'
    forcing_dir = '/project/nssac_agaid/vic_cropsyst/data/ForVirginia/for_run_VIC_CropSyst/VIC_Binary_CONUS_1979_to_2019_20200721/data_'

    # watershed_list = readFile(watershed_list_file)
    # target_coords = getMultiWsCoords(watershed_data_file, watershed_list)
    target_coords = readFile(coord_list_file)
    forcing_coords = getForcingCoords(forcing_list_path)

    prepare_input_data(target_coords, forcing_coords, split_size, soil_file_in, soil_dir_out, control_file_in, control_dir_out, forcing_dir, result_dir)

    # clear results directory
    checkMakeAndClearDir(result_dir, True)
    print(f'Result dir: {result_dir}')

if __name__ == '__main__':
    main()
