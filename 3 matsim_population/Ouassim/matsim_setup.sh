# Work with python 3.8
module load python/3.8

# New python environment
virtualenv matsim_python_env
source matsim_python_env/bin/activate

pip3 install -r requirements.txt

