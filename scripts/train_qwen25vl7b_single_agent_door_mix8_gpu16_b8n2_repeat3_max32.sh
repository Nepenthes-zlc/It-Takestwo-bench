#!/usr/bin/env sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "${SCRIPT_DIR}/.." && pwd)
CONFIG_PATH="${ROOT_DIR}/yaml/train_qwen25vl7b_single_agent_door_mix8_gpu16_b8n2_repeat3_max32.yaml"
PYTHON_BIN=${PYTHON_BIN:-/home/azvm/miniconda3/envs/verl/bin/python}
DATA_DIR="${ROOT_DIR}/data/verl_minecraft/single_agent/elevator_door/door_agentb_mix8_2easy4medium2hard_20260702"
DIFFICULTY_RUN_DIR=${DIFFICULTY_RUN_DIR:-${ROOT_DIR}/runs/2026-06-30/singleagent/Agent-b/qwen25vl7b_single_agent_door_b8n4_24inst_2chunk_200step_grpo_512x288_r6144_20260630_113131}

if [ ! -f "${DATA_DIR}/train.parquet" ] || [ ! -f "${DATA_DIR}/val.parquet" ]; then
  "${PYTHON_BIN}" "${ROOT_DIR}/scripts/build_difficulty_mix8_dataset.py" \
    --output-dir "${DATA_DIR}" \
    --run-dir "${DIFFICULTY_RUN_DIR}" \
    --easy-count 2 \
    --medium-count 4 \
    --hard-count 2 \
    --train-instance-count 24
fi

# The shared wrapper lets existing shell env override YAML. Force the important
# knobs here so this dedicated script is reproducible even in a dirty shell.
export CONFIG_PATH
export RUN_GROUP=single_agent/elevator_door
export TOTAL_EPOCHS=3
export TOTAL_TRAINING_STEPS=3
export SAVE_FREQ=999
export ROLLOUT_N=2
export TRAIN_INSTANCE_COUNT=16
export AGENT_WORKERS=16
export PREWARM_PARALLEL=4
export IT_TAKETWO_GEN_CHUNKS=1
export IT_TAKETWO_IMAGE_MAX_WIDTH=384
export IT_TAKETWO_IMAGE_MAX_HEIGHT=216
export AGENT_LOOP_CONFIG="${ROOT_DIR}/configs/verl_minecraft_agent_loop_7b_n4_single_agent_max32.yaml"
exec sh "${SCRIPT_DIR}/train_qwen25vl7b_n4_100step.sh"
