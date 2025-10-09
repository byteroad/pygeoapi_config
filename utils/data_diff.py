from copy import deepcopy
from typing import Any


def diff_yaml_dict(obj1: dict, obj2: dict, missing_props=[]) -> dict:
    """Returns all added, removed or changed elements between 2 dictionaries."""

    diff_data = {"added": {}, "removed": {}, "changed": {}}
    diff_obj(obj1, obj2, diff_data, "")

    # run diff through several conditions
    # 1. Exclude removed values that are None - not important
    # 2. Exclude values that already triggered warning on opening: .all_missing_props
    new_removed_dict = {}
    for k, v in diff_data["removed"].items():
        if v is not None and k not in missing_props:
            new_removed_dict[k] = v
    diff_data["removed"] = new_removed_dict

    # 3. Exclude changed values, originally warned about
    new_changed_dict = {}
    for k, v in diff_data["changed"].items():
        if v is None and k in missing_props:
            continue
        new_changed_dict[k] = v
    diff_data["changed"] = new_changed_dict

    return diff_data


def diff_obj(obj1: Any, obj2: Any, diff: dict, path: str = "") -> dict:
    """Returns all added, removed or changed elements between 2 objects.
    Ignores diff in dict keys order. For lists, order is checked."""

    if isinstance(obj1, dict) and isinstance(obj2, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in obj1:
                diff["added"][new_path] = obj2[key]
            elif key not in obj2:
                diff["removed"][new_path] = obj1[key]
            else:
                nested = diff_obj(obj1[key], obj2[key], diff, new_path)
                for k in diff:
                    diff[k].update(nested[k])

    elif isinstance(obj1, list) and isinstance(obj2, list):
        max_len = max(len(obj1), len(obj2))
        for i in range(max_len):
            new_path = f"{path}[{i}]"
            if i >= len(obj1):
                diff["added"][new_path] = obj2[i]
            elif i >= len(obj2):
                diff["removed"][new_path] = obj1[i]
            else:
                nested = diff_obj(obj1[i], obj2[i], diff, new_path)
                for k in diff:
                    diff[k].update(nested[k])

    else:
        if obj1 != obj2:
            diff["changed"][path] = {"old": obj1, "new": obj2}

    return diff
