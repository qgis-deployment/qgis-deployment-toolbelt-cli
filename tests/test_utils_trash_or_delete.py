#! python3  # noqa: E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_trash_or_delete
    # for specific test
    python -m unittest tests.test_utils_trash_or_delete.TestUtilsTrashOrDelete.test_force_delete_folder
"""

# standard library
import tempfile
import unittest
from os import environ
from pathlib import Path
from unittest.mock import patch

# 3rd party library
from send2trash import TrashPermissionError

# project
from qgis_deployment_toolbelt.utils.trash_or_delete import (
    get_deletion_policy,
    move_files_to_trash_or_delete,
)


# -- Globals
ENV_VAR_DELETION_POLICY = "QDT_DELETION_POLICY"

# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsTrashOrDelete(unittest.TestCase):
    """Test deletion policies of the autocleaner."""

    def setUp(self):
        """Fixtures prepared before each test."""
        environ.pop(ENV_VAR_DELETION_POLICY, None)

    def tearDown(self):
        """Executed after each test."""
        environ.pop(ENV_VAR_DELETION_POLICY, None)

    # -- policy resolution ----------------------------------------------------
    def test_policy_from_environment_default(self):
        """No env var set -> default is 'trash_or_delete'."""
        self.assertEqual(get_deletion_policy(), "trash_or_delete")

    def test_policy_from_environment_valid(self):
        """Valid env var value is honored."""
        environ[ENV_VAR_DELETION_POLICY] = "force_delete"
        self.assertEqual(get_deletion_policy(), "force_delete")

    def test_policy_from_environment_case_insensitive(self):
        """Env var value is normalized (case, surrounding spaces)."""
        environ[ENV_VAR_DELETION_POLICY] = "  Trash_Only  "
        self.assertEqual(get_deletion_policy(), "trash_only")

    def test_policy_from_environment_invalid_fallback(self):
        """Invalid env var value falls back to default."""
        environ[ENV_VAR_DELETION_POLICY] = "not_a_policy"
        self.assertEqual(get_deletion_policy(), "trash_or_delete")

    # -- force_delete -----------------------------------------------------------
    def test_force_delete_folder(self):
        """FORCE_DELETE removes a non-empty folder without going through the trash."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_force_delete_", ignore_cleanup_errors=True
        ) as tmpdirname:
            folder_to_delete = Path(tmpdirname) / "profile_to_remove"
            folder_to_delete.mkdir(parents=True, exist_ok=True)
            (folder_to_delete / "file.txt").write_text(
                "je ne suis paaaas un artiiiiiiste"
            )

            with patch(
                "qgis_deployment_toolbelt.utils.trash_or_delete.send2trash"
            ) as mocked_send2trash:
                move_files_to_trash_or_delete(
                    files_to_trash=folder_to_delete,
                    policy="force_delete",
                )
                mocked_send2trash.assert_not_called()

            self.assertFalse(folder_to_delete.exists())

    def test_force_delete_file(self):
        """FORCE_DELETE removes a single file without going through the trash."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_force_delete_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            file_to_delete = Path(tmpdirname) / "file_to_remove.txt"
            file_to_delete.write_text("content")

            with patch(
                "qgis_deployment_toolbelt.utils.trash_or_delete.send2trash"
            ) as mocked_send2trash:
                move_files_to_trash_or_delete(
                    files_to_trash=file_to_delete,
                    policy="force_delete",
                )
                mocked_send2trash.assert_not_called()

            self.assertFalse(file_to_delete.exists())

    def test_force_delete_error_is_logged_not_raised(self):
        """An OSError during force_delete is caught and logged, not propagated."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_force_delete_error_", ignore_cleanup_errors=True
        ) as tmpdirname:
            fake_path = Path(tmpdirname) / "does_not_matter.txt"

            with patch(
                "qgis_deployment_toolbelt.utils.trash_or_delete._permanently_delete",
                side_effect=OSError("simulated permission error"),
            ):
                try:
                    move_files_to_trash_or_delete(
                        files_to_trash=fake_path,
                        policy="force_delete",
                    )
                except OSError:
                    self.fail("OSError should be caught and logged, not raised.")

    # -- trash_only ---------------------------------------------------------
    def test_trash_only_keeps_file_on_error(self):
        """TRASH_ONLY leaves the file untouched if trash fails."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_trash_only_", ignore_cleanup_errors=True
        ) as tmpdirname:
            file_to_keep = Path(tmpdirname) / "leave_me_alone.txt"
            file_to_keep.write_text("content")

            with patch(
                "qgis_deployment_toolbelt.utils.trash_or_delete.send2trash",
                side_effect=TrashPermissionError("simulated trash failure"),
            ):
                move_files_to_trash_or_delete(
                    files_to_trash=file_to_keep,
                    policy="trash_only",
                )

            self.assertTrue(file_to_keep.exists())

    def test_trash_only_succeeds(self):
        """TRASH_ONLY calls send2trash and does not fall back to deletion."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_trash_only_ok_", ignore_cleanup_errors=True
        ) as tmpdirname:
            file_to_trash = Path(tmpdirname) / "trash_me.txt"
            file_to_trash.write_text("content")

            with patch(
                "qgis_deployment_toolbelt.utils.trash_or_delete.send2trash"
            ) as mocked_send2trash:
                move_files_to_trash_or_delete(
                    files_to_trash=file_to_trash,
                    policy="trash_only",
                )
                mocked_send2trash.assert_called_once()

    # -- trash_or_delete (default) -------------------------------------------
    def test_trash_or_delete_falls_back_on_folder(self):
        """TRASH_OR_DELETE (default) permanently removes a folder if trash fails.

        This specifically covers a bug in the previous implementation where
        Path.unlink() was called on a non-empty folder, raising
        IsADirectoryError which was not caught by the (too narrow)
        TrashPermissionError handler, silently leaving the folder on disk.
        """
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_trash_or_delete_", ignore_cleanup_errors=True
        ) as tmpdirname:
            folder_to_delete = Path(tmpdirname) / "profile_to_remove"
            folder_to_delete.mkdir(parents=True, exist_ok=True)
            (folder_to_delete / "file.txt").write_text("content")

            with patch(
                "qgis_deployment_toolbelt.utils.trash_or_delete.send2trash",
                side_effect=OSError("simulated no trash support"),
            ):
                move_files_to_trash_or_delete(
                    files_to_trash=folder_to_delete,
                    delete_file_per_file=True,
                )

            self.assertFalse(folder_to_delete.exists())

    def test_trash_or_delete_falls_back_on_file(self):
        """TRASH_OR_DELETE permanently deletes a single file if trash fails."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_trash_or_delete_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            file_to_delete = Path(tmpdirname) / "file_to_remove.txt"
            file_to_delete.write_text("content")

            with patch(
                "qgis_deployment_toolbelt.utils.trash_or_delete.send2trash",
                side_effect=TrashPermissionError("simulated trash permission error"),
            ):
                move_files_to_trash_or_delete(
                    files_to_trash=file_to_delete,
                    delete_file_per_file=True,
                )

            self.assertFalse(file_to_delete.exists())

    def test_trash_or_delete_batch_then_single_fallback(self):
        """Batch send2trash failure triggers the file-per-file retry path."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_trash_or_delete_batch_", ignore_cleanup_errors=True
        ) as tmpdirname:
            file_a = Path(tmpdirname) / "a.txt"
            file_b = Path(tmpdirname) / "b.txt"
            file_a.write_text("a")
            file_b.write_text("b")

            call_count = {"n": 0}

            def _side_effect(paths):
                call_count["n"] += 1
                if call_count["n"] == 1:
                    # first call: batch, must fail to trigger retry
                    raise OSError("simulated batch trash failure")
                # subsequent calls: per-file, let them "succeed" (no-op)

            with patch(
                "qgis_deployment_toolbelt.utils.trash_or_delete.send2trash",
                side_effect=_side_effect,
            ):
                move_files_to_trash_or_delete(files_to_trash=[file_a, file_b])

            # files were "trashed" (mocked), not deleted, since the per-file
            # calls succeeded (no exception raised on 2nd/3rd calls)
            self.assertEqual(call_count["n"], 3)

    # -- misc -----------------------------------------------------------------
    def test_empty_list_is_a_no_op(self):
        """Passing an empty list does nothing and does not raise."""
        with patch(
            "qgis_deployment_toolbelt.utils.trash_or_delete.send2trash"
        ) as mocked_send2trash:
            move_files_to_trash_or_delete(files_to_trash=[])
            mocked_send2trash.assert_not_called()


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
