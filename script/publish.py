import subprocess
import os
def run_command(command):
    """Run a shell command and print its output."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, command)

if __name__ == "__main__":
    # Prompt the user for their API token
    api_token = os.environ.get("PYPI_API_TOKEN")

    # Run 'poetry build'
    run_command("poetry build")

    # Run 'twine upload dist/*' with the provided API token
    twine_command = f"twine upload dist/* -u __token__ -p {api_token}"
    run_command(twine_command)
