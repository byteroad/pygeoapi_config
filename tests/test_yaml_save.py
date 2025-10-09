from copy import deepcopy
import yaml
import pytest
import subprocess
from pathlib import Path

from ..utils.data_diff import diff_yaml_dict
from ..pygeoapi_config_dialog import PygeoapiConfigDialog

BASE_DIR = Path(__file__).parent / "yaml_samples"


# List all YAML files dynamically
# First, delete all YAML files that start with "saved_"
for f in BASE_DIR.glob("saved_*.yml"):
    f.unlink()  # deletes the file
sample_yaml_files = list(BASE_DIR.glob("*.yml"))


def load_yaml(path: str | Path) -> dict:
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
        print(f"_________Data validated for '{sample_yaml.name}'", flush=True)
        assert True
        return


@pytest.mark.parametrize("sample_yaml", sample_yaml_files)
def test_open_file_validate_ui_data_save_file(qtbot, sample_yaml: str):
    """Run UI data validation from opened file (done in the plugin before saving to the new file)."""

    # Create the dialog widget and let qtbot manage it
    dialog = PygeoapiConfigDialog()
    qtbot.addWidget(dialog)

    # Load YAML
    dialog.open_file(
        sample_yaml
    )  # now dialog.config_data has the data stored including .all_missing_props
    yaml1_data = deepcopy(dialog.yaml_original_data)
    yaml1_missing_props = deepcopy(dialog.config_data.all_missing_props)

    # Save YAML - EVEN THOUGH some mandatory fields might be missing and recorded as empty strings/lists
    abs_new_yaml_path = sample_yaml.with_name(f"saved_updated_{sample_yaml.name}")
    dialog.save_to_file(abs_new_yaml_path)

    # open the new file
    dialog.open_file(abs_new_yaml_path)  # now dialog.config_data has the data stored
    yaml2_data = deepcopy(dialog.yaml_original_data)

    # get diff between old and new data
    diff_data = diff_yaml_dict(yaml1_data, yaml2_data, yaml1_missing_props)

    # save to file
    diff_yaml_path = sample_yaml.with_name(f"saved_DIFF_{sample_yaml.name}")
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

    if (
        len(diff_data["added"]) + len(diff_data["removed"]) + len(diff_data["changed"])
        == 0
    ):
        assert True
        return

    assert (
        False
    ), f"YAML data changed after saving: '{sample_yaml.name}'. \nAdded: {len(diff_data['added'])} fields, changed: {len(diff_data['changed'])} fields, removed: {len(diff_data['removed'])} fields."
