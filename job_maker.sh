#!/bin/bash

## usually one of bash, less, sbatch, what to execute on the dummy script
this_command=$1 

## job preamble with allocation, etc...
preamble=${HOME}/ss/preamble.sh

## simulations we should loop over
names=(m09_res30 m10q_res30 m10v_res30 m11b_res2100 m11d_res7100 m11e_res7100 m11h_res7100 m11i_res7100 m11q_res880 m12m_res7100 m12z_res4200 m12b_res7100 m12c_res7100 m12f_res7100 m12_elvis_RomeoJuliet_res3500 m12_elvis_ThelmaLouise_res4000 m12i_res7100 m12r_res7100 m12w_res7100 m12_elvis_RomulusRemus_res4000)
names=(m12i_res57000)


snapnums=(600 277 172 120 88)

#for sim_dir in ${sim_path}/*
for name in "${names[@]}"
do
    for snapnum in "${snapnums[@]}"
    do
        cat ${preamble} > temp.sh 
        # don't need this because it's already in my preamble on Stampede2
        #echo "#SBATCH -t 48:00:00        # run time (hh:mm:ss) - 48 hours" >> temp.sh
        echo "#SBATCH -J ${name}_${snapnum}_chimes         # job name" >> temp.sh
        echo "python runner.py --savename=${name} --snapnum=${snapnum} --mps=None" >> temp.sh
        ${this_command} temp.sh
        rm temp.sh
        echo ----------------------
    done
done
