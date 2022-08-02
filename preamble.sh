#!/bin/bash
#SBATCH -o log_out.o%j       # output and error file name (%j expands to jobID)
#SBATCH -N 1              # total number of mpi tasks requested
#SBATCH -n 48              # total number of mpi tasks requested
#SBATCH -p skx-normal     # queue (partition) -- normal, development, etc.
#SBATCH -t 4:00:00        # run time (hh:mm:ss) - 24 hours
#SBATCH --mail-user=agurvich@u.northwestern.edu
#SBATCH -A TG-AST140023
