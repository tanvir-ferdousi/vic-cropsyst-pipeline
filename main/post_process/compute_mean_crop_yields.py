from pathlib import Path
import os
import pandas as pd
import argparse
import glob
import json


def readClas():
    """
    Reads the command line arguments
    :return:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--watershedDataFile', type=str, dest='watershedDataFile', required=True)
    parser.add_argument('--resultDirPrefix', type=str, dest='resultDirPrefix', required=True)
    parser.add_argument('--outDir', type=str, dest='outDir', required=True)
    parser.add_argument('--runId', type=int, dest='runId', required=True)
    parser.add_argument('--targetCropType', type=str, dest='targetCropType', required=True)
    parser.add_argument('--cropCodeFile', type=str, dest='cropCodeFile', required=True)

    args = parser.parse_args()

    return args

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

def main():

    args = readClas()

    run_id = args.runId #1

    watershed_data_file = args.watershedDataFile #'data/VIC_gridcode_latlong_area_watershed.csv'

    result_dir = args.resultDirPrefix + 'run' + str(run_id) + '/'
    file_prefix = 'vic_crop_daily.csv_'
    out_dir = args.outDir #'../results/test_results/aggregate/'


    target_crop_type = args.targetCropType
    from_date = '1986-10-01'
    to_date = '2015-09-30'

    crop_code_file = args.cropCodeFile

    with open(crop_code_file, 'r') as file:
        crop_code_dict = json.load(file)

    crop_codes = crop_code_dict[target_crop_type]

    out_file = str(target_crop_type) + '_yield_'+str(run_id)+'.csv'

    out_file_path = out_dir + out_file

    idx_array = []
    yield_array = []

    # print('Reading watershed data')
    watershed_df = pd.read_csv(watershed_data_file)

    print(result_dir + file_prefix + "*")

    # For each cell
    for file_path in glob.glob(result_dir + file_prefix + "*"):
        print('For file: ' + file_path)

        file_path_obj = Path(file_path)

        if file_path_obj.is_file() and os.path.getsize(file_path) > 5000:

            crop_df = pd.read_csv(file_path)
            out_idx = removePrefix(file_path_obj.name, file_prefix)
            out_idx = removeSuffix(out_idx, '.asc')
            lat, lon = out_idx.split('_')
            cell_area_m2 = int(watershed_df[(watershed_df['Latitude'] == float(lat)) & (watershed_df['Longitude'] == float(lon))]['VIC_AREA (m2)'].values[0])

            if crop_df.shape[0] < 1:
                print('Empty crop file')
                continue

            # Nonempty crop file for a cell

            crop_df.set_index(pd.to_datetime(crop_df[['Year','Month','Day']]), inplace=True)
            crop_df = crop_df.loc[crop_df['Yield_kg_m2'] > 0][['Crop_name', 'CroppingSyst_code', 'Cell_fract', 'Yield_kg_m2']]
            crop_df['Yield_kg'] = crop_df['Yield_kg_m2']*crop_df['Cell_fract']*cell_area_m2

            crop_df = crop_df[crop_df['CroppingSyst_code'].isin(crop_codes)]

            crop_yields_arr = []
            for crop_code in crop_df['CroppingSyst_code'].unique():
                crop_yield = crop_df.loc[crop_df['CroppingSyst_code'] == crop_code].loc[from_date:to_date]['Yield_kg'].sum()
                cell_fract = crop_df.loc[crop_df['CroppingSyst_code'] == crop_code]['Cell_fract'].unique()[0]
                crop_yield_per_area = crop_yield/(cell_fract*cell_area_m2)
                crop_yields_arr.append(crop_yield_per_area)

            print(f'{len(crop_yields_arr)} crop types were detected.')
            if len(crop_yields_arr) == 0:
                continue

            mean_yield = sum(crop_yields_arr)/len(crop_yields_arr) # for a crop type

            idx_array.append(out_idx)
            yield_array.append(mean_yield)

    yield_df = pd.DataFrame({'cell': idx_array, 'yield': yield_array})

    print('Writing yield file: ' + out_file_path)
    yield_df.to_csv(out_file_path)


if __name__ == '__main__':
    main()
