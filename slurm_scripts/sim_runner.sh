#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=7-00:00:00
#SBATCH --output=log/sim_runner_%A.out
#SBATCH --account=nssac_agaid
#SBATCH --partition=bii

echo Running on `hostname`

python sim_runner.py
