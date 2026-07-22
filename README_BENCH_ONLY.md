# It-Taketwo Bench-Only Split

This directory is a bench-focused split from `/local_nvme/zhanglechao/It-Taketwo`.
It keeps the benchmark runner, task data, datapacks, rollout helpers, adapter code,
project YAML/config files, and the base Minecraft instance needed to create train instances.

Included:
- `bench/`: benchmark runner, YAMLs, task data, scripts, tests, world templates
- `mc_rollout/`, `verl_adapter/`: runtime imports used by `bench/training_style_bench.py`
- `scripts/`: instance preparation and prewarm helpers
- `yaml/`, `configs/`: rollout and adapter configs
- `env/instance-test-01`: base Minecraft instance copied by `scripts/prepare_train_instances.sh`
- `assert/`: Minecraft libraries/mod assets referenced by the base instance symlinks

Not included:
- historical `bench/runs/` outputs
- `bench/portable/dist/` model/runtime tarballs
- old generated train/eval instance directories

Example:

```bash
cd /local_nvme/zhanglechao/It-Taketwo-bench
/home/azvm/miniconda3/envs/verl/bin/python bench/scripts/bench.py validate \
  --config bench/yaml/serial_qwen25_truck_1time_fast16.yaml
```
