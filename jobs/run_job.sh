#!/bin/bash
#SBATCH -p performance
#SBATCH -t 01:00:00
#SBATCH --gpus=1
#SBATCH --job-name=singularity_pull
#SBATCH --out=out.log
#SBATCH --err=err.log

module load singularity

singularity exec blender.sif blender --background --python functions/renderer.py