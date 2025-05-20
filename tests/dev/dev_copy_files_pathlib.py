#! python3  # noqa: E265

"""Also view https://gist.github.com/Guts/459ba5b9e48eb6457781fd8fbd5460a5
"""

# standard
import shutil
from pathlib import Path
from shutil import copy, copy2, copyfile, copytree

t = Path("pyproject.toml")
# move a file
# t.rename("tests/pyproject.toml")

# move and override
# t.replace("tests/pyproject.toml")

# copy using globbing
src = Path("tests")
dest = Path("/tmp/test/python-pathlib-copy")
dest.mkdir(parents=True, exist_ok=True)
for f in src.glob("**/*"):
    if f.is_dir():
        continue

    final_path = dest / f.relative_to(src)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    # keeping file stats - needs a folderpath
    # copy2(f, final_path.parent)
    # as fast as possible but stats not guarantees - needs a filepath
    copyfile(f, final_path)

# using copytree
dest = Path("/tmp/test/python-shutil-copytree")
# keeping file stats
shutil.copytree(src, dest, copy_function=copy2)
# as fast as possible but stats not guarantees
shutil.copytree(src, dest, copy_function=copyfile)
