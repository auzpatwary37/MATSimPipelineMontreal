#!/bin/bash 
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10
#SBATCH --mem-per-cpu=1G
#SBATCH --time=00:15:00
#SBATCH --account=def-fciari
cd $SLURM_SUBMIT_DIR

module load python/2.7

source /home/omanout/projects/def-fciari/omanout/popgen_montreal/virEnv/bin/activate

python /home/omanout/projects/def-fciari/omanout/popgen_montreal/seed_code/collect_results.py
