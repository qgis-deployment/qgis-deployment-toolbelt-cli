from pathlib import Path
from time import sleep

test_file = Path(__file__).parent.parent.joinpath("fixtures/tmp/dev_files_dates.txt")
test_file.touch(exist_ok=True)

sleep(30)

print(
    f"File.\nCreated: {test_file.stat().st_ctime}\nModified: {test_file.stat().st_mtime}"
)


test_file.unlink(missing_ok=True)
