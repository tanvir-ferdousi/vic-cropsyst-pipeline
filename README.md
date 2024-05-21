# VIC-CropSyst Simulation Pipeline
This framework provides helper functions to parallelize VIC-CropSyst simulation runs on high performance computing (HPC) clusters. It also has scripts for input data preprocessing for running parameter scans, and output postprocessing to obtain certain aggregated statistics.

### Features at a glance
- Automated job submission and monitoring using slurm commands.
- Automated input file handling for massive parallelization of VIC-CropSyst runs across grid cells.
- Supports forcing data modification to perform parameter scans.
- Supports post processing of generated data aggregate for certain target outputs (f_q,snow, crop yield)


### Environment setup
- Clone this repository into your HPC storage
- Enter the following command to activate Anaconda: `module load anaconda`
- Navigate to the root directory of the repository which contains the `conda_env.yml` file.
- Create a new python environment using the following command: `conda env create -f conda_env.yml`
- A new environment with the name `vic_pipeline` would be created in the default conda path.
- Make sure that the enviroment configuration (name and path) is correct in `slurm_scripts/basic_run.sh`.

### Pipeline Configuration
- Open `config.ini` from the root directory in a text editor.
- Update all necessary parameters. Use the correct computing id.
