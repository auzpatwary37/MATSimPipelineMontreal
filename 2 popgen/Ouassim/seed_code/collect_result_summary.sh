#!/bin/bash 
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=5G
#SBATCH --time=00:05:00

cd $SLURM_SUBMIT_DIR

module load python/2.7.14

source ../envs/popg/bin/activate

python collect_result_summary.py
