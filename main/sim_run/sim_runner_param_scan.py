import subprocess
import time
from pathlib import Path
import os, shutil
from lib.dataprocessing import getMultiWsCoords, readFile
import numpy as np

# run_id = 1
SLEEP_TIME_SECONDS = 100
WORK_DIR = '/scratch/jcr5wj/agaid/hydro-sim/'

RUN_SUFFIX = 'w2_apr_23'
# RESULT_DIR_PREFIX = '/project/nssac_agaid/vic_cropsyst/test_results/'+RUN_SUFFIX+'/'
RESULT_DIR_PREFIX = '/scratch/jcr5wj/agaid/test_results/'+RUN_SUFFIX+'/'
# OUT_DIR_PREFIX = '/project/nssac_agaid/vic_cropsyst/test_results/'+RUN_SUFFIX+'/'

def checkMakeAndClearDir(dir_path, clear_dir):
    if not Path(dir_path).is_dir():
        print(f'The directory {dir_path} does not exist')
        os.makedirs(dir_path)
    else:
        print(f'The directory {dir_path} exists')
        if clear_dir:
            print('Clearing data')
            clearDir(dir_path)

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

def run_hydro_sim(run_id, coord_list_file, split_size, n_segments, del_tmax, del_tmin, del_prec):
    # global run_id
    ACTIVE_JOB_ID_LIST = []

    print("run id: " + str(run_id))

    result_dir = RESULT_DIR_PREFIX + 'run' + str(run_id) + '/'

    # prepare data
    print("preparing data")

    python_script = WORK_DIR + 'change_forcing.py'
    status = subprocess.run(['python', python_script, '--coordListFile', coord_list_file, '--runId', str(run_id), '--delTmax', str(del_tmax), '--delTmin', str(del_tmin), '--delPrec', str(del_prec)], stdout=subprocess.PIPE).stdout.decode("utf-8")
    print("Change forcing stdout: " + status)

    python_script = WORK_DIR + 'setup_inputs.py'
    status = subprocess.run(['python', python_script, '--coordListFile', coord_list_file, '--runId', str(run_id), '--splitSize', str(split_size), '--resultDir', result_dir], stdout=subprocess.PIPE).stdout.decode("utf-8")
    print("Setup input stdout: " + status)

    # submit job
    print("Submitting job")
    arry_arg = '--array=0-' + str(n_segments-1)
    slurm_script = WORK_DIR + 'vicjob.sh'
    status = subprocess.run(['sbatch', arry_arg, slurm_script, '-r', str(run_id)], stdout=subprocess.PIPE).stdout.decode("utf-8")
    ACTIVE_JOB_ID_LIST.append(status.split()[-1])

    # wait for finish
    print("Checking for job status")
    status = subprocess.run(['squeue', '-u', 'jcr5wj'], stdout=subprocess.PIPE).stdout.decode("utf-8")
    while any(job_id in status for job_id in ACTIVE_JOB_ID_LIST):
        print("Waiting for " + str(SLEEP_TIME_SECONDS) + " seconds.")
        time.sleep(SLEEP_TIME_SECONDS)
        status = subprocess.run(['squeue', '-u', 'jcr5wj'], stdout=subprocess.PIPE).stdout.decode("utf-8")
        print("status: " + status)

    print("All jobs finished")


    # process results
    # print("Processing results")
    #
    # python_script = WORK_DIR + 'process_vic_results.py'
    # status = subprocess.run(['python', python_script, '--watershedListFile', watershed_list_file, '--resultDir', result_dir, '--outDirPrefix', vic_out_dir, '--runId', str(run_id)], stdout=subprocess.PIPE).stdout.decode("utf-8")
    # print("Process VIC results stdout: " + status)
    #
    # python_script = WORK_DIR + 'process_crop_results.py'
    # status = subprocess.run(['python', python_script, '--watershedListFile', watershed_list_file, '--resultDir', result_dir, '--outDirPrefix', cropsyst_out_dir, '--runId', str(run_id)], stdout=subprocess.PIPE).stdout.decode("utf-8")
    # print("Process CROP results stdout: " + status)



def main():
    # watershed_list_file = 'data/watershed_names.txt'
    # watershed_data_file = 'data/VIC_gridcode_latlong_area_watershed.csv'
    coord_list_file = 'data/coord_list.txt'
    split_size = 5

    # vic_out_dir = OUT_DIR_PREFIX + 'vic/'
    # cropsyst_out_dir = OUT_DIR_PREFIX + 'cropsyst/'
    # checkMakeAndClearDir(vic_out_dir, True)
    # checkMakeAndClearDir(cropsyst_out_dir, True)

    # watershed_list = readFile(watershed_list_file)
    # watershed_coords = getMultiWsCoords(watershed_data_file, watershed_list)

    target_coords = readFile(coord_list_file)
    n_segments = len(range(0, len(target_coords), split_size))

    # run_id = 1
    # del_tmax = 1
    # del_tmin = 1
    # run_hydro_sim(run_id, target_watershed, split_size, del_tmax, del_tmin)

    # for i in range(0,11):
    #     run_hydro_sim(i, watershed_list_file, split_size, n_segments, i, i)
    #
    # for i in range(11,21):
    #     run_hydro_sim(i, watershed_list_file, split_size, n_segments, 10-i, 10-i)

    temp_change_arr = np.arange(0,2.5,0.50)
    prec_change_arr = np.arange(0,-1.25,-0.25) #np.arange(0,1.25,0.25)

    run_id = 0
    var_grid = []
    for temp_chg in temp_change_arr:
        for prec_chg in prec_change_arr:
            var_grid.append([run_id, temp_chg, prec_chg])

            del_tmax = temp_chg
            del_tmin = temp_chg
            del_prec = prec_chg

            run_hydro_sim(run_id, coord_list_file, split_size, n_segments, del_tmax, del_tmin, del_prec)
            run_id = run_id + 1


    var_grid = np.array(var_grid)

    np.savetxt('temp/run_grid.csv', var_grid, delimiter=',', header='run_id,temp_chg,prec_chg', comments='')

    # for i in range(5,9):
    #     run_hydro_sim(i, watershed_list_file, split_size, n_segments, 2*(5-i-1), 2*(5-i-1))



if __name__ == '__main__':
    main()
