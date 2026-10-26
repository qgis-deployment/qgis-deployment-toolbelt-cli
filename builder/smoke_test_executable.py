#! python3  # noqa: E265

"""
Run a deployment with the executable built by PyInstaller and check its output.

The unit and integration tests run QDT installed with pip, where every module is
available: they cannot detect a module that PyInstaller did not embed. QDT logs most
job failures and keeps going, still exiting with 0, so the output itself is checked.
Plain ERROR lines are not enough to fail: the scenario logs some on a bare runner
(missing QGIS3.ini, user-dirs.dirs...), whatever the packaging.

Usage: python builder/smoke_test_executable.py [path/to/scenario.qdt.yml]
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import re
import subprocess
import sys
from pathlib import Path


# #############################################################################
# ########### MAIN #################
# ##################################

# the executable built by PyInstaller (--onefile), next to the build reports
executables = [
    path for path in Path("dist").iterdir() if path.is_file() and path.suffix != ".txt"
]
if len(executables) != 1:
    sys.exit(f"Expected one executable in dist/, found: {executables}")

scenario = Path(sys.argv[1] if len(sys.argv) > 1 else "scenario.qdt.yml")

completed = subprocess.run(  # noqa: S603  # nosec B603
    [
        str(executables[0].resolve()),
        "--no-logfile",
        "deploy",
        "-vvv",
        f"--scenario={scenario.resolve()}",
    ],
    capture_output=True,
    encoding="UTF-8",
    errors="replace",
    timeout=1800,
)
output = completed.stdout + completed.stderr
# the console encoding (e.g. cp1252 on Windows) may not handle every character of the output
sys.stdout.reconfigure(errors="replace")
print(output)

errors = []
if completed.returncode != 0:
    errors.append(f"the executable exited with code {completed.returncode}")
# without this, a run stopped early without any error would pass
if "Deployment achieved!" not in output:
    errors.append("the deployment did not reach its end")
errors.extend(
    f"logged: {line}"
    for line in output.splitlines()
    if re.search(
        r"\|\|CRITICAL\|\||^Traceback \(most recent call last\)"
        r"|No module named|ModuleNotFoundError|ImportError",
        line,
    )
)

if errors:
    sys.exit(f"Smoke test of {executables[0].name} failed:\n- " + "\n- ".join(errors))

print(f"Smoke test of {executables[0].name} passed.")
