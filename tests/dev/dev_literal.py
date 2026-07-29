from typing import Literal, get_args

deletion_pol = Literal["force_delete", "trash_only", "trash_or_delete"]


print("trash_only" in get_args(deletion_pol))
print("zip" in get_args(deletion_pol))

if not "test" in get_args(deletion_pol):
    print(get_args(deletion_pol))

