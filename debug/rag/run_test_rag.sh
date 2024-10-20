#!/usr/bin/env bash
#SBATCH --job-name=test_rag_PAI
#SBATCH --output=/trinity/home/n.semenov/sbatch_logs/%x@%A_%a.out
#SBATCH --error=/trinity/home/n.semenov/sbatch_logs/%x@%A_%a.err
#SBATCH --time=36:00:00
#SBATCH --partition=ais-gpu
#SBATCH --gpus-per-task=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=8
#SBATCH --nodes=1
#SBATCH --mem=100G

set -ex

SINGULARITY_SHELL=/bin/bash \
srun singularity exec --nv \
    --bind /gpfs/gpfs0/n.semenov \
    --bind /trinity/home/n.semenov \
    /trinity/home/n.semenov/llm.sif python /trinity/home/n.semenov/PersonalAI/test_rag.py << EOF


EOF
