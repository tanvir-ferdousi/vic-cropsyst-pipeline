#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=7-00:00:00
#SBATCH --output=log/sim_runner_basic_%A.out
#SBATCH --account=nssac_agaid
#SBATCH --partition=bii

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
WORK_DIR=$SCRIPT_DIR/..
cd "$WORK_DIR"

echo Running on `hostname`

module load anaconda
source activate vic_pipeline

python main/sim_run/sim_runner_basic.py
