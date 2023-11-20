#!/bin/bash 
#SBATCH --nodes=1
#SBATCH --cpus-per-task=30
#SBATCH --mem-per-cpu=1500M
#SBATCH --ntasks=1
#SBATCH --time=10:00:00
#SBATCH --job-name 10per
#SBATCH --account=def-fciari

# Geopandas dependencies
module load gdal geos proj
export LD_LIBRARY_PATH=$EBROOTGEOS/lib # Add the path to GEOS libraries
export SPATIALINDEX_C_LIBRARY="/cvmfs/soft.computecanada.ca/easybuild/software/2017/avx2/Compiler/gcc7.3/libspatialindex/1.8.5/lib/libspatialindex_c.so.4"

# Java
module load java/1.8.0_192 maven


echo "Prepare running environment"
#bash matsim_setup.sh
source /scratch/omanout/matsim_input/matsim_python_env/bin/activate

echo "Prepare the git code"

cd /scratch/omanout/matsim_input/matsim_quebec_province
# git checkout montreal_EOD_2018

# Run matsim
echo "Running MATSIM"
python run.py
