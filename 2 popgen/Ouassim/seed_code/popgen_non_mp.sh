#!/bin/bash 
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --mem-per-cpu=100M
#SBATCH --time=48:00:00
#SBATCH --job-name pop_MTL
#SBATCH --account=def-fciari

cd $SLURM_SUBMIT_DIR

module load python/2.7

source /home/omanout/projects/def-fciari/omanout/popgen_montreal/virEnv/bin/activate

cd /home/omanout/projects/def-fciari/omanout/popgen_montreal/multiprocess_popgen/
git checkout hpc_serial

cd /scratch/omanout/popgen_montreal_output_OD2016/batch_code/

python launch_popgen_non_multiprocessed.py
