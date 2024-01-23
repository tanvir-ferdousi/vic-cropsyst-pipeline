from pathlib import Path
from sys import exit
import geopandas as gpd
import pandas as pd
import argparse
from tqdm import tqdm
from lib.dataprocessing import getMultiWsData, readFile

def readClas():
    """
    Reads the command line arguments
    :return:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--watershedListFile', type=str, dest='watershedListFile', required=True)
    # parser.add_argument('--resultDirPrefix', type=str, dest='resultDirPrefix', required=True)
    parser.add_argument('--resultDir', type=str, dest='resultDir', required=True)
    parser.add_argument('--outDirPrefix', type=str, dest='outDirPrefix', required=True)
    parser.add_argument('--runId', type=int, dest='runId', required=True)

    args = parser.parse_args()

    return args

def getRawWatershedDf(file_path, target_watershed):
    all_watershed_df = gpd.read_file(file_path)
    watershed_df = all_watershed_df[all_watershed_df.watershed == target_watershed]
    return watershed_df

def processFlux(file_path, flux_vars, area):
    file_path_obj = Path(file_path)

    if file_path_obj.is_file():
        flux_df = pd.read_table(file_path, sep='\t', header=None, names=flux_vars)
        flux_df.set_index(pd.to_datetime(flux_df[['year','month','day']]), inplace=True)
        flux_df = flux_df[['OUT_RUNOFF', 'OUT_BASEFLOW']]

        flux_df['RUNOFF'] = flux_df['OUT_RUNOFF'] + flux_df['OUT_BASEFLOW']
        flux_df['DAILY_FLOW'] = ((flux_df['RUNOFF']/1000)*area)/(24*60*60)
    else:
        print(f"Error: file {file_path} not found")
        exit(1)

    return flux_df['DAILY_FLOW']

def processRunoffData(file_prefix, watershed_df, results_path, flux_vars):

    flow_dict = {}
    for index, row in tqdm(watershed_df.iterrows()):
        file = file_prefix+row.Latitude + '_' + row.Longitude
        area = float(row['VIC_AREA (m2)'])
        grid_code = row['GRID_CODE']
        daily_flow = processFlux(results_path + file, flux_vars, area)
        flow_dict[grid_code] = daily_flow

    return pd.DataFrame(flow_dict)

def main():
    args = readClas()

    watershed_list_file = args.watershedListFile

    # result_dir_prefix = args.resultDirPrefix
    result_dir = args.resultDir
    out_dir_prefix = args.outDirPrefix

    run_id = args.runId
    watershed_data_file = 'data/VIC_gridcode_latlong_area_watershed.csv'

    flux_vars = ['year','month','day', 'OUT_RUNOFF', 'OUT_BASEFLOW']

    # result_dir = result_dir_prefix + 'run' + str(run_id) + '/'
    out_file = out_dir_prefix + 'hydro_res_' + str(run_id) + '.csv'

    print(f'Run id: {run_id}')
    print(f'Result dir: {result_dir}')


    watershed_list = readFile(watershed_list_file)
    watershed_df = getMultiWsData(watershed_data_file, watershed_list)

    flow_df = processRunoffData('runoff_vic_cropsyst_', watershed_df, result_dir, flux_vars)
    daily_flow = flow_df.sum(axis=1)


    daily_flow.to_csv(out_file)
    print(f'Out file: {out_file}')


if __name__ == '__main__':
    main()
