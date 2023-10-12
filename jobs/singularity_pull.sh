#!/bin/bash
#SBATCH -p performance
#SBATCH -t 01:00:00
#SBATCH --gpus=1
#SBATCH --job-name=singularity_pull
#SBATCH --out=out.log
#SBATCH --err=err.log

module load singularity

singularity pull shub://blender/blender:3.6