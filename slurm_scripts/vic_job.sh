#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=01:00:00
#SBATCH --mem-per-cpu=4096
#SBATCH --output=log/vic_job_%A_%a.out
#SBATCH --account=nssac_agaid
#SBATCH --partition=bii

echo Running on `hostname`

~/dev/VIC_CropSyst/build/gcc/Release/VIC_CropSyst -g input_files/dynamic/basic_run/SimSplits/vic_control_segment_${SLURM_ARRAY_TASK_ID}.txt
