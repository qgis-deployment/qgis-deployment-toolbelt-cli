#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_git_handler_remote
    # for specific
    python -m unittest tests.test_git_handler_remote.TestGitHandlerRemote.test_git_url_parsed
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import tempfile
import unittest
from pathlib import Path

# 3rd party
from dulwich.errors import NotGitRepository
from git import Repo as GitPythonRepo
from giturlparse import GitUrlParsed

# package
from qgis_deployment_toolbelt.profiles.remote_git_handler import RemoteGitHandler

# #############################################################################
# ########## Classes ###############
# ##################################


class TestGitHandlerRemote(unittest.TestCase):
    """Test module."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.good_git_url = "https://github.com/geotribu/profils-qgis.git"

    # -- TESTS ---------------------------------------------------------
    def test_initialization(self):
        """Test remote git repo identifier"""
        # OK
        remote_git_handler = RemoteGitHandler(source_repository_url=self.good_git_url)

        self.assertEqual(remote_git_handler.SOURCE_REPOSITORY_TYPE, "git_remote")
        self.assertTrue(remote_git_handler.is_valid_git_repository())

        # KO
        bad_git_url = "https://oslandia.com"
        with self.assertRaises(NotGitRepository):
            RemoteGitHandler(bad_git_url)

    def test_is_local_git_repo(self):
        """Test local git repo identifier"""
        good_git_url = "https://github.com/octocat/Hello-World"
        git_handler = RemoteGitHandler(source_repository_url=self.good_git_url)

        with tempfile.TemporaryDirectory(
            prefix="QDT_test_remote_git_",
            ignore_cleanup_errors=True,
            suffix="_is_local_git_repo",
        ) as tmpdirname:
            GitPythonRepo.clone_from(url=good_git_url, to_path=Path(tmpdirname))
            # OK
            self.assertTrue(
                git_handler._is_local_path_git_repository(
                    local_path=Path(tmpdirname), raise_error=False
                )
            )
        # KO
        self.assertFalse(git_handler._is_local_path_git_repository(Path("./tests")))

    def test_git_url_parsed(self):
        """Test git parsed URL"""
        git_handler = RemoteGitHandler(source_repository_url=self.good_git_url)
        git_url_parsed = git_handler.url_parsed(self.good_git_url)

        # type
        self.assertIsInstance(git_url_parsed, GitUrlParsed)

        # keys
        self.assertIn("branch", git_url_parsed.data)
        self.assertIn("domain", git_url_parsed.data)
        self.assertIn("groups_path", git_url_parsed.data)
        self.assertIn("owner", git_url_parsed.data)
        self.assertIn("path", git_url_parsed.data)
        self.assertIn("path_raw", git_url_parsed.data)
        self.assertIn("pathname", git_url_parsed.data)
        self.assertIn("platform", git_url_parsed.data)
        self.assertIn("port", git_url_parsed.data)
        self.assertIn("protocol", git_url_parsed.data)
        self.assertIn("protocols", git_url_parsed.data)
        self.assertIn("repo", git_url_parsed.data)
        self.assertIn("url", git_url_parsed.data)

        # values
        self.assertIn("github.com", git_url_parsed.domain)
        self.assertIn("github.com", git_url_parsed.host)
        self.assertEqual("", git_url_parsed.groups_path)
        self.assertEqual("geotribu", git_url_parsed.owner)
        self.assertEqual("github", git_url_parsed.platform)
        self.assertEqual("profils-qgis", git_url_parsed.repo)

    def test_git_clone_remote_url(self):
        """Test git parsed URL."""
        git_handler = RemoteGitHandler(source_repository_url=self.good_git_url)

        with tempfile.TemporaryDirectory(
            prefix="QDT_test_remote_git_",
            ignore_cleanup_errors=True,
            suffix="_git_clone",
        ) as tmpdirname:
            # clone
            git_handler.download(destination_local_path=Path(tmpdirname))
            # check if clone worked and new folder is a local git repo
            self.assertTrue(git_handler._is_local_path_git_repository(Path(tmpdirname)))

            # check pull is working
            git_handler.clone_or_pull(to_local_destination_path=Path(tmpdirname))

    def test_change_remote_branch(self):
        """Test git parsed URL."""
        git_handler = RemoteGitHandler(
            source_repository_url=self.good_git_url,
            branch_to_use="main",
        )

        with tempfile.TemporaryDirectory(
            prefix="QDT_test_remote_git_",
            ignore_cleanup_errors=True,
            suffix="_change_remote_branch",
        ) as tmpdirname:
            # clone
            git_handler.download(destination_local_path=Path(tmpdirname))
            # check if clone worked and new folder is a local git repo
            self.assertTrue(git_handler._is_local_path_git_repository(Path(tmpdirname)))

            git_handler = RemoteGitHandler(
                source_repository_url=self.good_git_url,
                branch_to_use="another_branch",
            )
            git_handler.download(destination_local_path=Path(tmpdirname))
            self.assertTrue(git_handler._is_local_path_git_repository(Path(tmpdirname)))
