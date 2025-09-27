import yaml
import subprocess
import os
import venv
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).parent.parent  # adjust if script is inside a subfolder
WORKFLOW_FILE = REPO_ROOT / ".github" / "workflows" / "unit-tests.yml"
VENV_DIR = REPO_ROOT / ".venv_workflow"  # dedicated venv in repo root
REQ_MAIN = REPO_ROOT / "requirements.txt"
REQ_DEV = REPO_ROOT / "requirements_dev.txt"

# 1. Create the virtual environment if it doesn't exist
if not VENV_DIR.exists():
    print(f"Creating virtual environment at {VENV_DIR}")
    venv.create(VENV_DIR, with_pip=True)

# Determine Python and pip inside the venv
if os.name == "nt":
    python_exe = VENV_DIR / "Scripts" / "python.exe"
    pip_exe = VENV_DIR / "Scripts" / "pip.exe"
else:
    python_exe = VENV_DIR / "bin" / "python"
    pip_exe = VENV_DIR / "bin" / "pip"

# Upgrade pip inside the venv
subprocess.run(
    [str(python_exe), "-m", "pip", "install", "--upgrade", "pip"], check=True
)

# Install requirements into the venv
print("\nInstalling main requirements...")
subprocess.run(
    [str(python_exe), "-m", "pip", "install", "-r", str(REQ_MAIN)], check=True
)

print("Installing dev/test requirements...")
subprocess.run(
    [str(python_exe), "-m", "pip", "install", "-r", str(REQ_DEV)], check=True
)

# 4. Load workflow YAML
with open(WORKFLOW_FILE) as f:
    workflow = yaml.safe_load(f)

# 5. Iterate through jobs and steps
for job_name, job in workflow.get("jobs", {}).items():
    print(f"\n=== Running job: {job_name} ===")
    for step in job.get("steps", []):
        if "run" in step:
            cmd = step["run"]

            # 5a. Set environment variables for this step
            env_vars = os.environ.copy()
            step_env = step.get("env", {})
            for k, v in step_env.items():
                env_vars[k] = v

            # 5b. Replace "python" in commands with venv Python
            cmd = cmd.replace("python", str(python_exe))

            # 5c. Run the command from repo root
            print(f"\n--> Running: {cmd}")
            subprocess.run(cmd, shell=True, check=True, env=env_vars, cwd=REPO_ROOT)
