Files=/scratch/omanout/popgen_montreal_output_OD2016/batch_code/popgen_non_mp_*

for f in $Files
do
 sbatch $f
done
