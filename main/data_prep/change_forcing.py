import numpy as np
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
import os, shutil
from pathlib import Path
import argparse
from lib.dataprocessing import getMultiWsCoords, readFile

def readClas():
    """
    Reads the command line arguments
    :return:
    """
    parser = argparse.ArgumentParser()

    #
    parser.add_argument('--delPrec', type=float, dest='delPrec', required=False, default=0)
    parser.add_argument('--delTmax', type=float, dest='delTmax', required=False, default=0)
    parser.add_argument('--delTmin', type=float, dest='delTmin', required=False, default=0)
    parser.add_argument('--delWind', type=float, dest='delWind', required=False, default=0)
    parser.add_argument('--delQair', type=float, dest='delQair', required=False, default=0)
    parser.add_argument('--delSwave', type=float, dest='delSwave', required=False, default=0)
    parser.add_argument('--delRhmax', type=float, dest='delRhmax', required=False, default=0)
    parser.add_argument('--delRhmin', type=float, dest='delRhmin', required=False, default=0)

    # parser.add_argument('--targetWatershed', type=str, dest='targetWatershed', required=True)
    # parser.add_argument('--watershedListFile', type=str, dest='watershedListFile', required=True)
    parser.add_argument('--coordListFile', type=str, dest='coordListFile', required=True)

    parser.add_argument('--runId', type=int, dest='runId', required=True)

    args = parser.parse_args()

    return args

def getWatershedCoords(file_path, target_watershed):
    all_watershed_df = gpd.read_file(file_path)
    watershed_df = all_watershed_df[all_watershed_df.watershed == target_watershed]
    watershed_coords = watershed_df.Latitude.values + '_' +  watershed_df.Longitude.values
    return watershed_coords

def readForcingDataToFrame(file_path, dt_def, start_date, scale_factor):
    np_data = np.fromfile(file_path, dtype=dt_def)
    force_df = pd.DataFrame(np_data)/scale_factor
    force_df.index = pd.date_range(start_date, periods=len(force_df))
    return force_df

def readForcingData(file_path, dt_def):
    return np.fromfile(file_path, dtype=dt_def)

def writeForcingFile(file_path, np_data):
    np_data.tofile(file_path)

# def changeForcingData(in_file, out_file, dt_def, scale_factor, change_dict):
#     np_data = readForcingData(in_file, dt_def)
#
#     for chg_var in change_dict.keys():
#         # print(f'Changing {chg_var} by {change_dict[chg_var]}')
#         np_data[chg_var] = np_data[chg_var] + change_dict[chg_var]*scale_factor[chg_var]
#
#     writeForcingFile(out_file, np_data)

def changeForcingData(in_file, out_file, dt_def, scale_factor, change_dict):
    np_data = readForcingData(in_file, dt_def)

    for chg_var in change_dict.keys():
        if chg_var == 'prec':
            if change_dict[chg_var] < -1:
                print('Warning: invalid value for fraction change in precipitation! No change done.')
            else:
                np_data[chg_var] = np_data[chg_var]*(1+change_dict[chg_var])
        else:
            np_data[chg_var] = np_data[chg_var] + change_dict[chg_var]*scale_factor[chg_var]

    writeForcingFile(out_file, np_data)

# Misc functions
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

def checkDir(dir_path):
    if not Path(dir_path).is_dir():
        print(f'Error: the directory {dir_path} does not exist')
        exit(1)

def checkMakeAndClearDir(dir_path, clear_dir):
    if not Path(dir_path).is_dir():
        print(f'The directory {dir_path} does not exist')
        os.makedirs(dir_path)
    else:
        print(f'The directory {dir_path} exists')
        if clear_dir:
            print('Clearing data')
            clearDir(dir_path)

def buildChangeDict(args):
    change_dict = {}

    if args.delTmax != 0:
        change_dict['tmax'] = args.delTmax

    if args.delTmin != 0:
        change_dict['tmin'] = args.delTmin

    if args.delPrec != 0:
        change_dict['prec'] = args.delPrec


    return change_dict


def main():

    args = readClas()

    # watershed_data_file = 'data/VIC_gridcode_latlong_area_watershed.csv'
    # watershed_list_file = args.watershedListFile
    coord_list_file = args.coordListFile
    run_id = args.runId

    in_path = '/project/nssac_agaid/vic_cropsyst/data/ForVirginia/for_run_VIC_CropSyst/VIC_Binary_CONUS_1979_to_2019_20200721/'
    out_path = '/scratch/jcr5wj/agaid/forcing/input_data_mod/' + 'run' + str(run_id) + '/'

    # Check if directories exist
    checkDir(in_path)
    # checkDir(out_path)

    # Check, create and clear the out directory
    # clearDir(out_path)
    checkMakeAndClearDir(out_path, True)

    dt_def = np.dtype([
        ('prec', '<u2'),
        ('tmax', '<i2'),
        ('tmin', '<i2'),
        ('wind', '<i2'),
        ('qair', '<i2'),
        ('swave', '<i2'),
        ('rhum_max', '<i2'),
        ('rhum_min', '<i2'),
    ])

    scale_factor = {}
    scale_factor['prec'] = 40
    scale_factor['tmax'] = 100
    scale_factor['tmin'] = 100
    scale_factor['wind'] = 100
    scale_factor['qair'] = 10000
    scale_factor['swave'] = 40
    scale_factor['rhum_max'] = 100
    scale_factor['rhum_min'] = 100

    # target_coords = getWatershedCoords(watershed_file_path, target_watershed)
    # watershed_list = readFile(watershed_list_file)
    # target_coords = getMultiWsCoords(watershed_data_file, watershed_list)
    target_coords = readFile(coord_list_file)

    change_dict = buildChangeDict(args)

    for chg_var in change_dict.keys():
        print(f'Changing {chg_var} by {change_dict[chg_var]}')

    for coord in tqdm(target_coords):
        file = 'data_' + coord
        in_file = in_path + file
        out_file = out_path + file
        changeForcingData(in_file, out_file, dt_def, scale_factor, change_dict)

    print(f'Forcing data change complete for run id {run_id}')


if __name__ == '__main__':
    main()
