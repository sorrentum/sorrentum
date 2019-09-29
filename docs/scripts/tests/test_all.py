import logging

import helpers.env as env
import helpers.git as git
import helpers.printing as prnt
import helpers.unit_test as ut
import helpers.user_credentials as usc
import helpers.system_interaction as si

_LOG = logging.getLogger(__name__)

import helpers.dbg as dbg
import helpers.io_ as io_

import os

# class Test_preprocess1(ut.TestCase):
#
#     def _helper(self):
#         git_dir = git.get_client_root(super_module=False)
#         exec_path = git_dir + "/docs/scripts/remove_md_empty_lines.py"
#         dbg.dassert_exists(exec_path)
#         #
#         in_file = self.get_input_dir() + "/input1.txt"
#         out_file = self.get_scratch_space() + "/output.txt"
#         cmd = exec_path + " --input %s --output %s" % (in_file, out_file)
#         si.system(cmd)
#         # Check.
#         act = io_.from_file(out_file, split=False)
#         self.check_string(act)
#
#     def test1(self):
#         self._helper()
#
#     def test2(self):
#         self._helper()
