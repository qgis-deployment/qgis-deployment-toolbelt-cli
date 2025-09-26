#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_check_path
    # for specific test
    python -m unittest tests.test_utils_check_path.TestUtilsCheckPath.test_check_path_as_str_ok
"""

# standard library
import platform
import stat
import tempfile
import unittest
from os import getenv
from pathlib import Path

# project
from qgis_deployment_toolbelt.utils.check_path import (
    check_folder_is_empty,
    check_path,
    check_path_exists,
    check_path_is_readable,
    check_path_is_writable,
    check_var_can_be_path,
)


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsCheckPath(unittest.TestCase):
    """Test package metadata."""

    @classmethod
    def tearDownClass(cls) -> None:
        file_no_readable = Path("tests/fixtures/tmp_file_no_readable.txt")
        file_no_writable = Path("tests/fixtures/tmp_file_no_writable.txt")
        if file_no_readable.exists():
            file_no_readable.chmod(0o666)
            file_no_readable.unlink()
        if file_no_writable.exists():
            file_no_writable.chmod(0o666)
            file_no_writable.unlink()
        return super().tearDownClass()

    def test_check_path_as_str_ok(self):
        """Test filepath as str is converted into Path."""
        self.assertTrue(
            check_var_can_be_path(input_var="/this/is/an/imaginary/file.imaginary")
        )

        self.assertTrue(
            check_var_can_be_path(input_var="%PROGRAMFILES%/QGIS/3_22/bin/qgis-bin.exe")
        )

    def test_check_path_as_str_ko(self):
        """Test filepath from int can't be converted into Path."""
        with self.assertRaises(TypeError):
            check_var_can_be_path(input_var=1000)
        # no exception but False
        self.assertFalse(check_var_can_be_path(input_var=1000, raise_error=False))

    def test_check_path_exists_ok(self):
        """Test path exists."""
        # a valid Path instance pointing to an existing file
        self.assertTrue(check_path_exists(input_path=Path("pyproject.toml")))
        # str is valid and point to an existing file
        self.assertTrue(check_path_exists(input_path="pyproject.toml"))
        # str with user expand is valid and point to an existing folder
        self.assertTrue(check_path_exists(input_path="~"))

    def test_check_path_exists_ko(self):
        """Test path exists fail cases."""
        # str is not valid
        with self.assertRaises(TypeError):
            check_path_exists(input_path=1000)
        self.assertFalse(check_path_exists(input_path=1000, raise_error=False))
        # str is valid but not an existing file
        with self.assertRaises(FileExistsError):
            check_path_exists(input_path="/this/is/an/imaginary/file.imaginary")
        # no exception but False
        self.assertFalse(
            check_path_exists(
                input_path="/this/is/an/imaginary/file.imaginary", raise_error=False
            )
        )

    def test_check_path_readable_ok(self):
        """Test path is readable."""
        # a valid Path instance pointing to an existing file which is readable
        self.assertTrue(check_path_is_readable(input_path=Path("pyproject.toml")))
        # str is valid and point to an existing file which is readable
        self.assertTrue(check_path_is_readable(input_path="pyproject.toml"))

    def test_check_path_readable_ko(self):
        """Test path is readable fail cases."""
        # str is not valid
        with self.assertRaises(TypeError):
            check_path_is_readable(input_path=1000)
        self.assertFalse(check_path_is_readable(input_path=1000, raise_error=False))

    @unittest.skipIf(
        getenv("CI") or platform.system() == "Windows",
        "Skip on CI or Windows - file permission tests not reliable",
    )
    def test_check_path_readable_ko_specific(self):
        """Test path is readable fail cases."""
        # temporary fixture
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_check_path",
            ignore_cleanup_errors=True,
        ) as tmpdirname:
            unreadable_file = Path(tmpdirname).joinpath("tmp_file_no_readable.txt")
            unreadable_file.touch(mode=0o333, exist_ok=True)

            # no exception but False
            self.assertFalse(
                check_path_is_readable(input_path=unreadable_file, raise_error=False)
            )

    def test_check_path_writable_ok(self):
        """Test path is writable."""
        # a valid Path instance pointing to an existing file which is writable
        self.assertTrue(check_path_is_writable(input_path=Path("pyproject.toml")))
        # str is valid and point to an existing file which is writable
        self.assertTrue(check_path_is_writable(input_path="pyproject.toml"))

    def test_check_path_writable_ko(self):
        """Test path is writable fail cases."""
        # str is not valid
        with self.assertRaises(TypeError):
            check_path_exists(input_path=1000)
        self.assertFalse(check_path_is_writable(input_path=1000, raise_error=False))

    def test_check_path_writable_ko_specific(self):
        """Test path is writable fail cases (specific)."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_check_path",
            ignore_cleanup_errors=True,
        ) as tmpdirname:
            unwritable_file = Path(tmpdirname).joinpath("tmp_file_no_writable.txt")
            unwritable_file.touch(exist_ok=True)
            unwritable_file.write_text("this content is the last to be written here")

            unwritable_file.chmod(stat.S_IROTH)

            # str not valid, an existing file but not writable
            with self.assertRaises(IOError):
                check_path_is_writable(input_path=unwritable_file)

            # no exception but False
            self.assertFalse(
                check_path_is_writable(input_path=unwritable_file, raise_error=False)
            )

    def test_check_path_meta_ok(self):
        """Test meta check path."""
        # an existing file
        check_path(
            input_path="pyproject.toml",
            must_be_a_file=True,
            must_be_a_folder=False,
        )
        check_path(
            input_path=Path("pyproject.toml"),
            must_be_a_file=True,
            must_be_a_folder=False,
        )

        # an existing folder
        check_path(
            input_path=Path(__file__).parent,
            must_be_a_file=False,
            must_be_a_folder=True,
        )

    def test_check_path_meta_ko(self):
        """Test meta check path fail cases."""
        # invalid path
        with self.assertRaises(TypeError):
            check_path(
                input_path=1000,
            )
        self.assertFalse(check_path(input_path=1000, raise_error=False))

        # mutual exclusive options
        with self.assertRaises(ValueError):
            check_path(
                input_path="pyproject.toml",
                must_be_a_file=True,
                must_be_a_folder=True,
            )

        # must exist
        self.assertFalse(
            check_path(
                input_path="imaginary/path", raise_error=False, must_exists=False
            )
        )
        self.assertFalse(
            check_path(input_path="imaginary/path", raise_error=False, must_exists=True)
        )
        with self.assertRaises(FileExistsError):
            check_path(input_path="imaginary/path", must_exists=True)

        # must be readable
        self.assertTrue(
            check_path(
                input_path="imaginary/path",
                raise_error=False,
                must_exists=False,
                must_be_readable=False,
            )
        )
        self.assertTrue(
            check_path(
                input_path="pyproject.toml",
                raise_error=False,
                must_exists=False,
                must_be_readable=True,
            )
        )

        # must be writable
        self.assertFalse(
            check_path(
                input_path="imaginary/path",
                raise_error=False,
                must_exists=False,
                must_be_readable=False,
                must_be_writable=True,
            )
        )
        self.assertTrue(
            check_path(
                input_path=f"tests/{Path(__file__).name}",
                raise_error=True,
                must_exists=False,
                must_be_readable=False,
                must_be_writable=True,
            )
        )

        # must be a file
        self.assertFalse(
            check_path(
                input_path=Path(__file__).parent,
                raise_error=False,
                must_exists=True,
                must_be_a_file=True,
            )
        )
        with self.assertRaises(FileNotFoundError):
            check_path(
                input_path=Path(__file__).parent,
                raise_error=True,
                must_exists=True,
                must_be_a_file=True,
            )

        # must be a folder
        self.assertFalse(
            check_path(
                input_path=Path(__file__),
                raise_error=False,
                must_exists=True,
                must_be_a_folder=True,
            )
        )
        with self.assertRaises(NotADirectoryError):
            check_path(
                input_path=Path(__file__),
                raise_error=True,
                must_exists=True,
                must_be_a_folder=True,
            )

    @unittest.skipIf(
        getenv("CI"), "Creating file on CI with specific rights is not working."
    )
    def test_check_path_meta_ko_specific(self):
        """Test meta check path is readbale / writable fail cases (specific)."""
        # temporary fixture
        not_writable_file = Path("tests/fixtures/tmp_file_no_writable.txt")
        not_writable_file.touch()
        not_writable_file.chmod(stat.S_IREAD | stat.S_IROTH)

        # str not valid, an existing file but not writable
        with self.assertRaises(IOError):
            check_path(
                input_path=not_writable_file, must_be_a_file=True, must_be_writable=True
            )

        # no exception but False
        self.assertFalse(
            check_path(
                input_path=not_writable_file,
                must_be_a_file=True,
                must_be_writable=True,
                raise_error=False,
            )
        )

    def test_check_folder_is_empty(self):
        """Test empty folder recognition."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_check_path_",
            ignore_cleanup_errors=True,
            suffix="_empty_folder",
        ) as tmpdirname:
            self.assertTrue(check_folder_is_empty(Path(tmpdirname)))

        with tempfile.TemporaryDirectory(
            prefix="QDT_test_check_path_",
            ignore_cleanup_errors=True,
            suffix="_not_empty_folder",
        ) as tmpdirname:
            Path(tmpdirname).joinpath(".gitkeep").touch()
            self.assertFalse(check_folder_is_empty(Path(tmpdirname)))

        with self.assertRaises(TypeError):
            check_folder_is_empty(input_var=1000)
        # no exception but False
        self.assertFalse(check_folder_is_empty(input_var=1000, raise_error=False))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
