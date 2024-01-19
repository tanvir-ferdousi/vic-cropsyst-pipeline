# VIC-CropSyst Simulation Pipeline
This framework provides helper functions to parallelize VIC-CropSyst simulation runs on high performance computing (HPC) clusters. It also has scripts for input data preprocessing for running parameter scans, and output postprocessing to obtain certain aggregated statistics.

Features at a glance
- Automated job submission and monitoring using slurm commands.
- Automated input file handling for massive parallelization of VIC-CropSyst runs across grid cells.
- Supports forcing data modification to perform parameter scans.
- Supports post processing of generated data aggregate for certain target outputs (f_q,snow, crop yield)
