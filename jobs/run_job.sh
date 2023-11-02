#!/bin/bash
#SBATCH -p performance
#SBATCH -t 01:00:00
#SBATCH --gpus=4
#SBATCH --job-name=blender_render
#SBATCH --out=out.log
#SBATCH --err=err.log

module load singularity



singularity exec --nv blender.sif blender --background --python functions/renderer.py