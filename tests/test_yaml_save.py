from dataclasses import asdict, is_dataclass
import yaml
from typing import Any
import pytest
import subprocess
from pathlib import Path
from ..pygeoapi_config_dialog import PygeoapiConfigDialog

BASE_DIR = Path(__file__).parent / "yaml_samples"


# List all YAML files dynamically
# First, delete all YAML files that start with "saved_"
for f in BASE_DIR.glob("saved_*.yml"):
    f.unlink()  # deletes the file
sample_yaml_files = list(BASE_DIR.glob("*.yml"))


# --- 1. Load YAML files ---
def load_yaml(path: str | Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)  # returns nested dicts/lists


@pytest.fixture()
def base_dir():
    return BASE_DIR
    # return os.path.dirname(os.path.abspath(__file__))  # directory of current file


@pytest.mark.parametrize("sample_yaml", sample_yaml_files)
def test_json_schema_on_open_save(qtbot, sample_yaml: str):
    """Validate YAML against schema.json after loading and saving."""

    # Create the dialog widget and let qtbot manage it
    dialog = PygeoapiConfigDialog()
    qtbot.addWidget(dialog)

    # Load YAML
    # abs_yaml_path = os.path.join(base_dir, sample_yaml)
    dialog.open_file(sample_yaml)  # now dialog.config_data has the data stored

    # Save YAML
    abs_new_yaml_path = sample_yaml.with_name(f"saved_{sample_yaml.name}")
    dialog.save_to_file(abs_new_yaml_path)

    result = subprocess.run(
        [
            "check-jsonschema",
            "--verbose",
            "--schemafile",
            "https://raw.githubusercontent.com/geopython/pygeoapi/refs/heads/master/pygeoapi/resources/schemas/config/pygeoapi-config-0.x.yml",
            abs_new_yaml_path,
        ],
        capture_output=True,
        text=True,
    )
    print(f"_______File saved as '{abs_new_yaml_path}'", flush=True)
    assert (
        result.returncode == 0
    ), f"Validation failed:\n{result.stderr}, '{abs_new_yaml_path.name}', {result.stdout}"


@pytest.mark.parametrize("sample_yaml", sample_yaml_files)
def test_open_file_validate_ui_data(qtbot, sample_yaml: str):
    """Run UI data validation from opened file (done in the plugin before saving to the new file)."""

    # Create the dialog widget and let qtbot manage it
    dialog = PygeoapiConfigDialog()
    qtbot.addWidget(dialog)

    # Load YAML
    # abs_yaml_path = os.path.join(base_dir, sample_yaml)
    dialog.open_file(sample_yaml)  # now dialog.config_data has the data stored

    # Validate UI data (to follow exactly the user experience after clicking Save button)
    data_valid, invalid_props = dialog._set_validate_ui_data()

    if not data_valid:
        # fail the test if a legit file (e.g. "docker.config.yml") did not pass the validation
        assert False, f"'{sample_yaml.name}' file UI data is not valid: {invalid_props}"
    else:
        assert True

    print(f"_________Data validated for '{sample_yaml.name}'", flush=True)
    assert True


@pytest.mark.parametrize("sample_yaml", sample_yaml_files)
def test_open_file_validate_ui_data_save_file(qtbot, sample_yaml: str):
    """Run UI data validation from opened file (done in the plugin before saving to the new file)."""

    # Create the dialog widget and let qtbot manage it
    dialog = PygeoapiConfigDialog()
    qtbot.addWidget(dialog)

    # Load YAML
    # abs_yaml_path = os.path.join(base_dir, sample_yaml)
    dialog.open_file(sample_yaml)  # now dialog.config_data has the data stored

    # Save YAML - EVEN THOUGH some mandatory fields might be missing and recorded as empty strings/lists
    abs_new_yaml_path = sample_yaml.with_name(f"saved_updated_{sample_yaml.name}")
    dialog.save_to_file(abs_new_yaml_path)

    # open the new file
    dialog.open_file(abs_new_yaml_path)  # now dialog.config_data has the data stored

    # get the YAML diff
    yaml1 = load_yaml(sample_yaml)
    yaml2 = load_yaml(abs_new_yaml_path)

    diff_data = diff_yaml(yaml1, yaml2)
    diff_yaml_path = sample_yaml.with_name(f"saved_DIFF_{sample_yaml.name}")

    # save to file
    with open(diff_yaml_path, "w", encoding="utf-8") as file:
        yaml.dump(
            diff_data,
            file,
            Dumper=dialog.dumper,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            indent=4,
        )

    if len(diff_data) == 0:
        assert True

    assert (
        False
    ), f"YAML data changed after saving: '{sample_yaml.name}'. \nAdded: {len(diff_data['added'])} fields, changed: {len(diff_data['changed'])} fields, removed: {len(diff_data['removed'])} fields."


def diff_yaml(obj1: Any, obj2: Any, path: str = "") -> dict:
    """Returns all added, removed or changed elements between 2 YAML files.
    Ignores diff in dict keys order. For lists, order is checked."""

    diff = {"added": {}, "removed": {}, "changed": {}}

    if isinstance(obj1, dict) and isinstance(obj2, dict):
        all_keys = set(obj1.keys()) | set(obj2.keys())
        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            if key not in obj1:
                diff["added"][new_path] = obj2[key]
            elif key not in obj2:
                diff["removed"][new_path] = obj1[key]
            else:
                nested = diff_yaml(obj1[key], obj2[key], new_path)
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
                nested = diff_yaml(obj1[i], obj2[i], new_path)
                for k in diff:
                    diff[k].update(nested[k])

    else:
        if obj1 != obj2:
            diff["changed"][path] = {"old": obj1, "new": obj2}

    return diff
