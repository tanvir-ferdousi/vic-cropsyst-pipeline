import subprocess
from pathlib import Path
import os, sys, shutil, inspect

# from .context import lib
cur_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
par_dir = os.path.dirname(cur_dir)
sys.path.insert(0, par_dir)
from lib.dataprocessing import readFile

SLEEP_TIME_SECONDS = 100

RUN_SUFFIX = 'w4_jan_24'
RESULT_DIR_PREFIX = '/scratch/jcr5wj/agaid/test_results/'+RUN_SUFFIX+'/'

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

def run_hydro_sim(coord_list_file, split_size, n_segments):

    # ACTIVE_JOB_ID_LIST = []


    # result_dir = RESULT_DIR_PREFIX
    # print(f'In sim_runner_basic.py. CWD: {os.getcwd()}')

    # prepare data
    print("preparing data")
    python_script = 'main/data_prep/setup_inputs.py'
    status = subprocess.run(['python', python_script, '--coordListFile', coord_list_file, '--splitSize', str(split_size), '--resultDir', RESULT_DIR_PREFIX], stdout=subprocess.PIPE).stdout.decode("utf-8")
    print("Setup input stdout: " + status)

    # # submit job
    # print("Submitting job")
    # arry_arg = '--array=0-' + str(n_segments-1)
    # slurm_script = WORK_DIR + 'slurm_scripts/vic_job_basic.sh'
    # status = subprocess.run(['sbatch', arry_arg, slurm_script], stdout=subprocess.PIPE).stdout.decode("utf-8")
    # ACTIVE_JOB_ID_LIST.append(status.split()[-1])
    #
    # # wait for finish
    # print("Checking for job status")
    # status = subprocess.run(['squeue', '-u', 'jcr5wj'], stdout=subprocess.PIPE).stdout.decode("utf-8")
    # while any(job_id in status for job_id in ACTIVE_JOB_ID_LIST):
    #     print("Waiting for " + str(SLEEP_TIME_SECONDS) + " seconds.")
    #     time.sleep(SLEEP_TIME_SECONDS)
    #     status = subprocess.run(['squeue', '-u', 'jcr5wj'], stdout=subprocess.PIPE).stdout.decode("utf-8")
    #     print("status: " + status)
    #
    # print("All jobs finished")


def main():

    coord_list_file = os.getcwd()+'/input_files/static/coord_list_small_test.txt'
    split_size = 5

    target_coords = readFile(coord_list_file)
    n_segments = len(range(0, len(target_coords), split_size))

    run_hydro_sim(coord_list_file, split_size, n_segments)

if __name__ == '__main__':
    main()
