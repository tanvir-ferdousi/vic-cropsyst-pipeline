#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --time=12:00:00
#SBATCH --output=../log/mean_cropyield_%A_%a.out
#SBATCH --account=nssac_agaid
#SBATCH --partition=bii


python ../compute_mean_crop_yields.py --runId ${SLURM_ARRAY_TASK_ID} --watershedDataFile '../data/VIC_gridcode_latlong_area_watershed.csv' --targetCropType 'annual_grain' --cropCodeFile '../data/crop_types.json' --resultDirPrefix '/scratch/jcr5wj/agaid/test_results/w2_apr_23/' --outDir '/scratch/jcr5wj/agaid/agg_results/w5_oct_23/mean_cropyield/'
