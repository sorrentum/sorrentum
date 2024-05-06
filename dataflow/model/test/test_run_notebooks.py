import datetime
import os
from typing import Any

import pytest

import core.config as cconfig
import dev_scripts.notebooks.run_notebook_test_case as dsnrnteca
import helpers.hgit as hgit
import helpers.hio as hio
import helpers.hsystem as hsystem


def build_config() -> cconfig.ConfigList:
    """
    Simple config builder for the test.
    """
    # We want to execute the notebook as it is, but config builder needs
    # a config from the caller, which we ignore for now.
    config = {}
    config = cconfig.Config()
    config_list = cconfig.ConfigList([config])
    return config_list


def build_test_master_research_backtest_analyzer_config(
    sweep_param: bool, output_dir_name: str
) -> cconfig.ConfigList:
    """
    Default config builder for testing the Master_research_backtest_analyzer
    notebook.

    :return: config list
    """
    amp_dir = hgit.get_amp_abs_path()
    dir_name = os.path.join(
        amp_dir,
        "dataflow/model/test/outcomes/Test_run_master_research_backtest_analyzer/input/tiled_results",
    )
    config_dict = {
        "dir_name": dir_name,
        "output_dir_name": output_dir_name,
        "start_date": datetime.date(2024, 1, 1),
        "end_date": datetime.date(2024, 1, 31),
        "asset_id_col": "asset_id",
        "pnl_resampling_frequency": "D",
        "rule": "6T",
        "annotate_forecasts_kwargs": {
            "style": "longitudinal",
            "quantization": 30,
            "liquidate_at_end_of_day": False,
            "initialize_beginning_of_day_trades_to_zero": False,
            "burn_in_bars": 3,
            "compute_extended_stats": True,
            "target_dollar_risk_per_name": 1.0,
            "modulate_using_prediction_magnitude": False,
            "prediction_abs_threshold": 0.3,
        },
        "im_client_config": {
            "vendor": "ccxt",
            "universe_version": "v7.5",
            "root_dir": "s3://cryptokaizen-unit-test/v3",
            "partition_mode": "by_year_month",
            "dataset": "ohlcv",
            "contract_type": "futures",
            "data_snapshot": "",
            "aws_profile": "ck",
            "version": "v1_0_0",
            "download_universe_version": "v8",
            "tag": "downloaded_1min",
            "download_mode": "periodic_daily",
            "downloading_entity": "airflow",
            "resample_1min": False,
        },
        "column_names": {
            "price_col": "open",
            "volatility_col": "garman_klass_vol",
            "prediction_col": "feature",
        },
        "bin_annotated_portfolio_df_kwargs": {
            "proportion_of_data_per_bin": 0.2,
            "normalize_prediction_col_values": False,
        },
        "load_all_tiles_in_memory": True,
    }
    if sweep_param:
        config_dict["sweep_param"] = {
            "keys": (
                "column_names",
                "price_col",
            ),
            "values": [
                "open",
            ],
        }
    config = cconfig.Config().from_dict(config_dict)
    config_list = cconfig.ConfigList([config])
    return config_list


def _test_save_data(self: Any) -> None:
    """
    Save test data.
    """
    # Specify params to run the script.
    amp_dir = hgit.get_amp_abs_path()
    script_path = "dataflow/backtest/run_config_list.py"
    script_path = os.path.join(amp_dir, script_path)
    backtest_config = "mock1_v1-top2.5T.2000-01-01_2000-01-02"
    config_builder = f"'dataflow_amp.system.mock1.mock1_tile_config_builders.build_Mock1_tile_config_list(\"{backtest_config}\")'"
    # Save results to a scratch dir to copy only `tiled_results` dir
    # further.
    scratch_dir = self.get_scratch_space()
    cmd = [
        script_path,
        "--experiment_builder 'dataflow.backtest.master_backtest.run_in_sample_tiled_backtest'",
        f"--config_builder {config_builder}",
        f"--dst_dir {scratch_dir}",
        "--num_threads 'serial'",
    ]
    cmd = " ".join(cmd)
    # Run tiled flow to get data.
    hsystem.system(cmd, suppress_output=False)
    # Copy `tiled_results` dir to the input dir.
    tiled_results_dir = os.path.join(scratch_dir, "tiled_results")
    use_only_test_class = True
    dst_dir = self.get_input_dir(use_only_test_class)
    hio.create_dir(dst_dir, incremental=True)
    cmd = f"cp -r {tiled_results_dir} {dst_dir}"
    hsystem.system(cmd, suppress_output=False)


def _test_run_notebook(
    self: Any, notebook_name: str, config_builder: str
) -> None:
    """
    Run notebook end-to-end without errors.
    """
    amp_dir = hgit.get_amp_abs_path()
    notebook_path = os.path.join(
        amp_dir,
        "dataflow",
        "model",
        "notebooks",
        f"{notebook_name}.ipynb",
    )
    self._test_run_notebook(notebook_path, config_builder)


class Test_run_master_feature_analyzer(dsnrnteca.Test_Run_Notebook_TestCase):
    @pytest.mark.superslow("~45 sec.")
    def test_run_notebook(self) -> None:
        """
        Test that notebook runs end-to-end without errors.
        """
        notebook_name = "Master_feature_analyzer"
        config_builder = "dataflow.model.test.test_run_notebooks.build_config()"
        _test_run_notebook(self, notebook_name, config_builder)

    @pytest.mark.skip("Run manually.")
    @pytest.mark.requires_ck_infra
    @pytest.mark.slow("~15 sec.")
    def test_save_data(self) -> None:
        """
        Save test data.
        """
        _test_save_data(self)


class Test_run_master_research_backtest_analyzer(
    dsnrnteca.Test_Run_Notebook_TestCase
):
    @pytest.mark.superslow("~80 sec.")
    def test_run_notebook1(self) -> None:
        """
        Test that notebook runs end-to-end without errors.

        `sweep_param` is not exposed, use only default config.
        """
        notebook_name = "Master_research_backtest_analyzer"
        output_dir_name = self.get_scratch_space()
        config_builder = f'dataflow.model.test.test_run_notebooks.build_test_master_research_backtest_analyzer_config(True, "{output_dir_name}")'
        _test_run_notebook(self, notebook_name, config_builder)

    @pytest.mark.skip("Run manually.")
    @pytest.mark.requires_ck_infra
    @pytest.mark.slow("~17 sec.")
    def test_save_data(self) -> None:
        """
        Save test data.
        """
        _test_save_data(self)


class Test_toy_research_backtest_analyzer(dsnrnteca.Test_Run_Notebook_TestCase):
    @pytest.mark.superslow("~60 sec.")
    def test_run_notebook1(self) -> None:
        """
        Test that notebook runs end-to-end without errors.

        `sweep_param` is not exposed, use only default config.
        """
        notebook_name = "Toy_research_backtest_analyzer"
        output_dir_name = self.get_scratch_space()
        config_builder = f'dataflow.model.test.test_run_notebooks.build_test_master_research_backtest_analyzer_config(False, "{output_dir_name}")'
        _test_run_notebook(self, notebook_name, config_builder)

    @pytest.mark.superslow("~60 sec.")
    def test_run_notebook2(self) -> None:
        """
        Test that notebook runs end-to-end without errors.

        `sweep_param` is exposed, multiple configs are used.
        """
        notebook_name = "Toy_research_backtest_analyzer"
        output_dir_name = self.get_scratch_space()
        config_builder = f'dataflow.model.test.test_run_notebooks.build_test_master_research_backtest_analyzer_config(True, "{output_dir_name}")'
        _test_run_notebook(self, notebook_name, config_builder)

    @pytest.mark.skip("Run manually.")
    @pytest.mark.requires_ck_infra
    @pytest.mark.slow("~17 sec.")
    def test_save_data(self) -> None:
        """
        Save test data.
        """
        _test_save_data(self)
