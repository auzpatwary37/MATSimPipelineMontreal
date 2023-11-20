nodes=$1
nb_regions=$2

path=/scratch/omanout/popgen_montreal_output_OD2016/batch_code

size=$(($nb_regions / $nodes))
residual=$(($nb_regions %  $nodes))

mini=$i
maxi=$(($i + $size))

for i in $(seq $(($nodes)))
do

 if (($i == $nodes)); then
 maxi=$(($maxi + $residual))
 fi

 list=$(seq -s, $mini $maxi)

# Copy configuration file and change regions
 cp ./configuration_one_region.yaml $path/configuration_$i.yaml

 sed -i s/'ids: \[1\]'/'ids: ['$list']'/ $path/configuration_$i.yaml
 sed -i s/'Server test'/test_$i/ $path/configuration_$i.yaml

# Copy python program and change its input data
 cp launch_popgen_non_multiprocessed.py $path/launch_popgen_non_multiprocessed_$i.py

 sed -i s/'.\/configuration.yaml'/'.\/configuration_'$i'.yaml'/ $path/launch_popgen_non_multiprocessed_$i.py

 cp popgen_non_mp.sh $path/popgen_non_mp_$i.sh
 sed -i s/synthpop_MTL/synthpop_MTL_$i/ $path/popgen_non_mp_$i.sh
 sed -i s/launch_popgen_non_multiprocessed.py/launch_popgen_non_multiprocessed_$i.py/ $path/popgen_non_mp_$i.sh

 mini=$(($maxi + 1))
 maxi=$(($maxi + $size))

done
