#!/bin/bash
#SBATCH -p performance
#SBATCH -t 01:00:00
#SBATCH --gpus=1
#SBATCH --job-name=post_processing
#SBATCH --output=outerr.log
#SBATCH --error=outerr.log

module load python/3.10.12
module load cuda
module load nccl
pipenv run python functions/post_processing.py
