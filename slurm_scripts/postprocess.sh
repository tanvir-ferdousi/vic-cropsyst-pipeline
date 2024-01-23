#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=12:00:00
#SBATCH --output=log/postprocess_%j.out
#SBATCH --account=bii_nssac
#SBATCH --partition=bii

while getopts ":r:" opt; do
  case $opt in
    r) runId="$OPTARG";;
  esac
done


python process_crop_results.py --watershedListFile data/watershed_names.txt --resultsPath /project/nssac_agaid/vic_cropsyst/test_results/w4_aug_22/run${runId}/ --outPath /project/nssac_agaid/vic_cropsyst/test_results/w4_aug_22/aggregate/run${runId}
