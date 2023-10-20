#!/bin/bash
#SBATCH -p performance
#SBATCH -t 01:00:00
#SBATCH --gpus=1
#SBATCH --job-name=blender_render
#SBATCH --out=out.log
#SBATCH --err=err.log

module load singularity

singularity exec --nv blender_wo_gpu.sif blender --background --python functions/renderer.py