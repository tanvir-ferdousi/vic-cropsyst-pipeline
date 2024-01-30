#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=01:00:00
#SBATCH --output=log/sim_runner_basic_%A.out
#SBATCH --account=nssac_agaid
#SBATCH --partition=bii

echo Running on `hostname`

DIR=~/.conda/envs/vic_pipeline
source activate vic_pipeline
export PATH=$DIR/bin:$PATH
export LD_LIBRARY_PATH=$DIR/lib:$PATH
export PYTHONPATH=$DIR/lib/python3.10/site-packages:$PATH


conda list
python --version

python main/sim_run/sim_runner_basic.py
