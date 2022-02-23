"""
Import as:

import dataflow.pipelines.features.pipeline as dtfpifepip
"""

import datetime
import logging

import core.config as cconfig
import core.features as cofeatur
import core.finance as cofinanc
import core.signal_processing as csigproc
import dataflow.core as dtfcore
import dataflow.system as dtfsys

_LOG = logging.getLogger(__name__)


class FeaturePipeline(dtfcore.DagBuilder):
    def get_config_template(self) -> cconfig.Config:
        dict_ = {
            self.get_nid("load_data"): {
                cconfig.DUMMY: None,
            },
            self.get_nid("filter_weekends"): {
                "col_mode": "replace_all",
            },
            self.get_nid("filter_ath"): {
                "col_mode": "replace_all",
                "transformer_kwargs": {
                    "start_time": datetime.time(9, 30),
                    "end_time": datetime.time(16, 00),
                },
            },
            self.get_nid("perform_col_arithmetic"): {
                "func_kwargs": {
                    cconfig.DUMMY: None,
                }
            },
            self.get_nid("add_diffs"): {
                "col_mode": "merge_all",
            },
            self.get_nid("zscore"): {
                "col_mode": "replace_all",
                "nan_mode": "drop",
            },
            self.get_nid("compress_tails"): {
                "col_mode": "replace_all",
            },
            self.get_nid("cross_feature_pairs"): {
                "func_kwargs": {
                    cconfig.DUMMY: None,
                },
            },
        }
        config = cconfig.get_config_from_nested_dict(dict_)
        return config

    def _get_dag(
        self, config: cconfig.Config, mode: str = "strict"
    ) -> dtfcore.DAG:
        dag = dtfcore.DAG(mode=mode)
        _LOG.debug("%s", config)
        tail_nid = None
        #
        stage = "load_data"
        nid = self.get_nid(stage)
        node = dtfsys.data_source_node_factory(nid, **config[nid].to_dict())
        tail_nid = self._append(dag, tail_nid, node)
        #
        stage = "filter_weekends"
        nid = self.get_nid(stage)
        node = dtfcore.ColumnTransformer(
            nid,
            transformer_func=cofinanc.set_weekends_to_nan,
            **config[nid].to_dict(),
        )
        tail_nid = self._append(dag, tail_nid, node)
        #
        stage = "filter_ath"
        nid = self.get_nid(stage)
        node = dtfcore.ColumnTransformer(
            nid,
            transformer_func=cofinanc.set_non_ath_to_nan,
            **config[nid].to_dict(),
        )
        tail_nid = self._append(dag, tail_nid, node)
        #
        stage = "perform_col_arithmetic"
        nid = self.get_nid(stage)
        node = dtfcore.FunctionWrapper(
            nid,
            func=cofeatur.perform_col_arithmetic,
            **config[nid].to_dict(),
        )
        tail_nid = self._append(dag, tail_nid, node)
        #
        stage = "add_diffs"
        nid = self.get_nid(stage)
        node = dtfcore.ColumnTransformer(
            nid,
            transformer_func=lambda x: x.diff(),
            col_rename_func=lambda x: x + ".diff",
            **config[nid].to_dict(),
        )
        tail_nid = self._append(dag, tail_nid, node)
        #
        stage = "zscore"
        nid = self.get_nid(stage)
        node = dtfcore.SeriesTransformer(
            nid,
            transformer_func=csigproc.compute_fir_zscore,
            **config[nid].to_dict(),
        )
        tail_nid = self._append(dag, tail_nid, node)
        #
        stage = "compress_tails"
        nid = self.get_nid(stage)
        node = dtfcore.SeriesTransformer(
            nid,
            transformer_func=csigproc.compress_tails,
            **config[nid].to_dict(),
        )
        tail_nid = self._append(dag, tail_nid, node)
        #
        stage = "cross_feature_pairs"
        nid = self.get_nid(stage)
        node = dtfcore.FunctionWrapper(
            nid,
            func=cofeatur.cross_feature_pairs,
            **config[nid].to_dict(),
        )
        tail_nid = self._append(dag, tail_nid, node)
        #
        _ = tail_nid
        return dag
