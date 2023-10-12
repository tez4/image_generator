#!/bin/bash
#SBATCH -p performance
#SBATCH -t 01:00:00
#SBATCH --gpus=1
#SBATCH --job-name=python_test
#SBATCH --out=out.log
#SBATCH --err=err.log

python3 functions/test_slurm.py