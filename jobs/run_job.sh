#!/bin/bash
#SBATCH -p performance
#SBATCH -t 1-00:00:00
#SBATCH --gpus=4
#SBATCH --job-name=blender_render
#SBATCH --output=outerr.log
#SBATCH --error=outerr.log

module load singularity

singularity exec --nv blender.sif blender --background --python functions/renderer.py