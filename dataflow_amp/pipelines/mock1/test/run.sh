#!/bin/bash -xe

clear

OPTS="$OPTS --clean_dst_dir --no_confirm"
OPTS="$OPTS --num_threads serial"
#OPTS="$OPTS --num_threads 3"
#OPTS="$OPTS --num_threads 2"
#OPTS="$OPTS --skip_on_error"
#OPTS="$OPTS --dry_run"
OPTS="$OPTS $*"

tag="mock1"
backtest_config="example1_v1-top2.1T.Jan2000"
config_builder="dataflow_amp.system.mock1.mock1_tile_config_builders.build_Mock1_tile_config_list(\"${backtest_config}\")"

dst_dir="build_Mock1_tile_config_list.${tag}.${backtest_config}.run1"

# TODO(gp): -> run_configs.py
./amp/dataflow/backtest/run_config_list.py \
    --experiment_builder "amp.dataflow.backtest.master_backtest.run_tiled_backtest" \
    --config_builder $config_builder \
    --dst_dir $dst_dir \
    $OPTS 2>&1 | tee run_config_list.txt
