#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_git_handler_local
    # for specific
    python -m unittest tests.test_git_handler_local.TestGitHandlerLocal.test_git_url_parsed
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import tempfile
import unittest
from pathlib import Path
from shutil import rmtree

# 3rd party
from dulwich.errors import NotGitRepository
from dulwich.repo import Repo
from git import Repo as GitPythonRepo

# package
from qgis_deployment_toolbelt.profiles.local_git_handler import LocalGitHandler


# #############################################################################
# ########## Classes ###############
# ##################################


class TestGitHandlerLocal(unittest.TestCase):
    """Test module."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.remote_repo_url = "https://github.com/geotribu/profils-qgis.git"
        cls.source_git_path_source = Path("tests/fixtures/tmp/git_handler_local_source")
        cls.local_git_path_target = Path("tests/fixtures/tmp/git_handler_local_target")
        cls.source_local_repository_obj = GitPythonRepo.clone_from(
            url=cls.remote_repo_url, to_path=cls.source_git_path_source
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Executed before module is shutdown after every test."""
        cls.source_local_repository_obj.git.clear_cache()
        cls.source_local_repository_obj.git = None
        rmtree(path=cls.source_git_path_source, ignore_errors=True)
        rmtree(path=cls.local_git_path_target, ignore_errors=True)

    # -- TESTS ---------------------------------------------------------
    def test_initialization(self):
        """Test module instanciation."""
        # OK - with pathlib.Path
        local_git_handler = LocalGitHandler(
            source_repository_path_or_uri=self.source_git_path_source,
            branch_to_use="main",
        )

        self.assertIsInstance(local_git_handler.SOURCE_REPOSITORY_PATH_OR_URL, Path)
        self.assertEqual(local_git_handler.SOURCE_REPOSITORY_TYPE, "git_local")
        self.assertEqual(
            local_git_handler.SOURCE_REPOSITORY_PATH_OR_URL,
            self.source_git_path_source.resolve(),
        )
        self.assertEqual(local_git_handler.SOURCE_REPOSITORY_ACTIVE_BRANCH, "main")

        # OK - with str
        local_git_handler = LocalGitHandler(
            source_repository_path_or_uri=f"{self.source_git_path_source.resolve()}",
            branch_to_use="main",
        )
        self.assertEqual(
            local_git_handler.SOURCE_REPOSITORY_PATH_OR_URL,
            self.source_git_path_source.resolve(),
        )
        self.assertEqual(local_git_handler.SOURCE_REPOSITORY_ACTIVE_BRANCH, "main")

        # OK - with str but no branch
        local_git_handler = LocalGitHandler(
            source_repository_path_or_uri=f"{self.source_git_path_source.resolve()}",
        )
        self.assertEqual(
            local_git_handler.SOURCE_REPOSITORY_PATH_OR_URL,
            self.source_git_path_source.resolve(),
        )
        self.assertEqual(local_git_handler.SOURCE_REPOSITORY_ACTIVE_BRANCH, "main")
        self.assertIsInstance(local_git_handler.SOURCE_REPOSITORY_PATH_OR_URL, Path)

        # KO
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_local_git_", ignore_cleanup_errors=True
        ) as tmpdirname:
            with self.assertRaises(NotGitRepository):
                LocalGitHandler(source_repository_path_or_uri=tmpdirname)

    def test_clone_with_specified_branch_existing(self):
        """Test clone with specified branch."""
        local_git_handler = LocalGitHandler(
            source_repository_path_or_uri=self.source_git_path_source,
            branch_to_use="main",
        )

        self.assertEqual(local_git_handler.SOURCE_REPOSITORY_TYPE, "git_local")

        with tempfile.TemporaryDirectory(
            prefix="QDT_test_local_git_",
            ignore_cleanup_errors=True,
            suffix="_specified_branch_existing",
        ) as tmpdirname:
            target_repo = local_git_handler.download(
                destination_local_path=Path(tmpdirname)
            )
            self.assertIsInstance(target_repo, Repo)

    def test_clone_with_specified_branch_not_existing(self):
        """Test clone with specified branch."""
        local_git_handler = LocalGitHandler(
            source_repository_path_or_uri=self.source_git_path_source,
            branch_to_use="no_existing_branch",
        )

        self.assertEqual(local_git_handler.SOURCE_REPOSITORY_TYPE, "git_local")
        self.assertEqual(local_git_handler.DESTINATION_BRANCH_TO_USE, "main")

        local_git_handler.download(
            destination_local_path=self.local_git_path_target.resolve()
        )

        with tempfile.TemporaryDirectory(
            prefix="QDT_test_local_git_",
            ignore_cleanup_errors=True,
            suffix="_specified_branch_not_existing",
        ) as tmpdirname:
            target_repo = local_git_handler.download(
                destination_local_path=Path(tmpdirname)
            )
            self.assertIsInstance(target_repo, Repo)

    def test_clone_then_fetch_pull(self):
        """Test clone with specified branch."""
        local_git_handler = LocalGitHandler(
            source_repository_path_or_uri=self.source_git_path_source,
            branch_to_use="main",
        )

        self.assertEqual(local_git_handler.SOURCE_REPOSITORY_TYPE, "git_local")

        with tempfile.TemporaryDirectory(
            prefix="QDT_test_local_git_",
            ignore_cleanup_errors=True,
            suffix="_clone_the_pull",
        ) as tmpdirname:
            repo_in_temporary_folder = Path(tmpdirname)

            target_repo = local_git_handler.download(
                destination_local_path=repo_in_temporary_folder
            )
            self.assertIsInstance(target_repo, Repo)
            self.assertTrue(repo_in_temporary_folder.joinpath(".git").is_dir())

            target_repo = local_git_handler.download(
                destination_local_path=repo_in_temporary_folder
            )
