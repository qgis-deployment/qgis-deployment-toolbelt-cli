#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_rules_context
    # for specific test
    python -m unittest tests.test_rules_context.testQdtRulesContext.test_rules_export_to_json
"""

# standard library
import json
import tempfile
import unittest
from pathlib import Path

# project
from qgis_deployment_toolbelt.profiles.rules_context import QdtRulesContext


# ############################################################################
# ########## Classes #############
# ################################


class TestQdtRulesContext(unittest.TestCase):
    """Test QDT rules context."""

    def test_rules_export_to_json(self):
        """Test export to JSON."""

        rules_context = QdtRulesContext()

        with tempfile.TemporaryDirectory(
            prefix="qdt_test_rules_context"
        ) as tmp_dir_name:
            context_json_path = Path(tmp_dir_name).joinpath("qdt_rules_context.json")

            # write into the file passing extra parameters to json.dumps
            with context_json_path.open("w", encoding="UTF8") as wf:
                wf.write(rules_context.to_json(indent=4, sort_keys=True))

            # test reading
            with context_json_path.open(mode="r", encoding="utf8") as in_json:
                context_data = json.load(in_json)

        self.assertIsInstance(context_data, dict)
        self.assertIn("date", context_data)
        self.assertIn("env", context_data)
        self.assertIn("environment", context_data)
        self.assertIn("user", context_data)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
