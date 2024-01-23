#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=01:00:00
#SBATCH --mem-per-cpu=4096
#SBATCH --output=log/result_%A_%a.out
#SBATCH --account=nssac_agaid
#SBATCH --partition=bii

echo Running on `hostname`

while getopts ":r:" opt; do
  case $opt in
    r) runId="$OPTARG";;
  esac
done

~/dev/VIC_CropSyst/build/gcc/Release/VIC_CropSyst -g SimSplits/run${runId}/vic_control_segment_${SLURM_ARRAY_TASK_ID}.txt
