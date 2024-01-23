from pathlib import Path
import os
import pandas as pd
import argparse
from tqdm import tqdm
from lib.dataprocessing import getMultiWsData, readFile
import pickle


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
    # parser.add_argument('--outPath', type=str, dest='outPath', required=True)

    args = parser.parse_args()

    return args

def processCropData(file_prefix, watershed_df, results_path):
    crop_dict = {}
    crop_list = {}
    for idx, row in tqdm(watershed_df.iterrows()):
        grid_area_m2 = float(row['VIC_AREA (m2)'])
        file = file_prefix+row.Latitude + '_' + row.Longitude+'.asc'
        file_path = results_path + file
        file_path_obj = Path(file_path)

        if file_path_obj.is_file() and os.path.getsize(file_path) > 0:
            crop_df = pd.read_csv(file_path)

            if crop_df.shape[0] < 1:
                continue

            crop_df.set_index(pd.to_datetime(crop_df[['Year','Month','Day']]), inplace=True)
            crop_df = crop_df.loc[crop_df['Yield_kg_m2'] > 0][['Crop_name', 'CroppingSyst_code', 'Cell_fract', 'Yield_kg_m2']]
            crop_df['Yield_kg'] = crop_df['Yield_kg_m2']*crop_df['Cell_fract']*grid_area_m2

            for crop_idx, crop_row in crop_df.iterrows():
                year = crop_idx.year
                yield_kg = crop_row.Yield_kg
                crop_code = crop_row.CroppingSyst_code
                crop_name = crop_row.Crop_name

                crop_list[crop_code] = crop_name

                if crop_code in crop_dict:
                    if year in crop_dict[crop_code]:
                        crop_dict[crop_code][year] += yield_kg
                    else:
                        crop_dict[crop_code][year] = yield_kg
                else:
                    yield_dict = {}
                    yield_dict[year] = yield_kg
                    crop_dict[crop_code] = yield_dict

    return pd.DataFrame(crop_dict), crop_list



def main():
    args = readClas()

    watershed_data_file = 'data/VIC_gridcode_latlong_area_watershed.csv'

    watershed_list_file = args.watershedListFile
    run_id = args.runId

    # result_dir_prefix = args.resultDirPrefix
    result_dir = args.resultDir
    out_dir_prefix = args.outDirPrefix

    # result_dir = result_dir_prefix + 'run' + str(run_id) + '/'

    crop_code_file = out_dir_prefix + 'crop_code_map_' + str(run_id) + '.pkl'
    crop_yield_file = out_dir_prefix + 'crop_yield_'+ str(run_id) + '.csv'

    print(f'Run id: {run_id}')
    print(f'Result path: {result_dir}')

    watershed_list = readFile(watershed_list_file)
    watershed_df = getMultiWsData(watershed_data_file, watershed_list)


    all_crop_df, crop_list = processCropData('vic_crop_daily.csv_', watershed_df, result_dir)

    with open(crop_code_file, 'wb') as f:
        pickle.dump(crop_list, f)
    print(f'Crop list dictionary: {crop_code_file}')

    all_crop_df.to_csv(crop_yield_file)
    print(f'Crop yield file: {crop_yield_file}')


if __name__ == '__main__':
    main()
