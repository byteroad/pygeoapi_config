import os
import pytest
import subprocess
from pathlib import Path
from ..pygeoapi_config_dialog import PygeoapiConfigDialog

BASE_DIR = Path(__file__).parent / "yaml_samples"


# List all YAML files dynamically
# First, delete all YAML files that start with "saved_"
for f in BASE_DIR.glob("saved_*.yml"):
    f.unlink()  # deletes the file
sample_yaml_files = list(BASE_DIR.glob("*.yml")) + list(BASE_DIR.glob("*.yaml"))


@pytest.fixture()
def base_dir():
    return BASE_DIR
    # return os.path.dirname(os.path.abspath(__file__))  # directory of current file


@pytest.mark.parametrize("sample_yaml", sample_yaml_files)
def test_json_schema_on_open_save(qtbot, base_dir, sample_yaml: str):
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
    ), f"Validation failed:\n{result.stderr}, '{abs_new_yaml_path.name}'"


@pytest.mark.parametrize("sample_yaml", sample_yaml_files)
def test_open_file_validate_ui_data(qtbot, base_dir, sample_yaml: str):
    """Run UI data validation from opened file (done in the plugin before saving to the new file)."""

    # Create the dialog widget and let qtbot manage it
    dialog = PygeoapiConfigDialog()
    qtbot.addWidget(dialog)

    # Load YAML
    # abs_yaml_path = os.path.join(base_dir, sample_yaml)
    dialog.open_file(sample_yaml)  # now dialog.config_data has the data stored

    # Validate UI data (to follow exactly the user experience after clicking Save button)
    data_valid, invalid_props = dialog._set_validate_ui_data()

    # some sample files have incomplete "Hello" Resource data: fail test if they wrongfully passed the validation
    if (
        str(sample_yaml).endswith("pygeoapi-test-config-ogr.yml")
        or str(sample_yaml).endswith("cite.config.yml")
        or str(sample_yaml).endswith("pygeoapi-config.yml")
        or str(sample_yaml).endswith("default.config.yml")
    ):
        if data_valid:
            assert (
                False
            ), f"'{sample_yaml.name}' file UI data is not valid: {invalid_props}"
        else:
            assert True
    else:
        if not data_valid:
            # fail the test if a legit file (e.g. "docker.config.yml") did not pass the validation
            assert (
                False
            ), f"'{sample_yaml.name}' file UI data is not valid: {invalid_props}"
        else:
            assert True

    print(f"_________Data validated for '{sample_yaml.name}'", flush=True)
    assert True
