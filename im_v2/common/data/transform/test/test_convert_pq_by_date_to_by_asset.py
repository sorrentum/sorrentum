import os

import helpers.git as hgit
import helpers.system_interaction as hsysinte
import helpers.unit_test as hunitest


# TODO(Nikola): Add one test for the command line and other tests testing directly _run
#  to get coverage.

class TestPqByDateToByAsset1(hunitest.TestCase):

    def test_daily_data1(self) -> None:
        """
        Generate daily data for 3 days in a by-date format and then convert
        it to by-asset.
        """
        test_dir = self.get_scratch_space()
        by_date_dir = os.path.join(test_dir, "by_date")
        # Generate some data.
        cmd = []
        file_path = os.path.join(
            hgit.get_amp_abs_path(),
            "im_v2/common/data/transform/test/generate_pq_example_data.py"
        )
        cmd.append(file_path)
        cmd.append("--start_date 2021-12-30")
        cmd.append("--end_date 2022-01-02")
        cmd.append("--assets A,B,C")
        cmd.append(f"--dst_dir {by_date_dir}")
        cmd = " ".join(cmd)
        hsysinte.system(cmd)
        # Build command line to convert the data.
        cmd = []
        file_path = os.path.join(
            hgit.get_amp_abs_path(),
            "im_v2/common/data/transform/convert_pq_by_date_to_by_asset.py"
        )
        cmd.append(file_path)
        cmd.append(f"--src_dir {by_date_dir}")
        by_asset_dir = os.path.join(test_dir, "by_asset")
        cmd.append(f"--dst_dir {by_asset_dir}")
        cmd.append("--num_threads 2")
        cmd = " ".join(cmd)
        hsysinte.system(cmd)
        # Check directory structure with file contents.
        include_file_content = True
        by_date_signature = hunitest.get_dir_signature(
            by_date_dir, include_file_content
        )
        act = []
        act.append("# by_date=")
        act.append(by_date_signature)
        by_asset_signature = hunitest.get_dir_signature(
            by_asset_dir, include_file_content
        )
        act.append("# by_asset=")
        act.append(by_asset_signature)
        act = "\n".join(act)
        purify_text = True
        self.check_string(act, purify_text=purify_text)


# TODO(Nikola): Add unit test for --transform reindex_on_unix_epoch
# The input looks like:
# ```
#   vendor_date  interval  start_time    end_time ticker currency  open         id
# 0  2021-11-24        60  1637762400  1637762460      A      USD   100         1
# 1  2021-11-24        60  1637762400  1637762460      A      USD   200         1
# ```
# We need another function to generate this format.
