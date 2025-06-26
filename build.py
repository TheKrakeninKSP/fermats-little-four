"""wrapper file to run pipreqs with specified options"""

import subprocess

def run_pipreqs(target_dir=".", force=True, savepath=None, ignore=None, encoding=None):
    command = ["pipreqs", target_dir]
    if force:
        command.append("--force")
    if savepath:
        command += ["--savepath", savepath]
    if ignore:
        command += ["--ignore", ignore]
    if encoding:
        command += ["--encoding", encoding]

    print("Running command:", " ".join(command))

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("pipreqs output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running pipreqs:\n", e.stderr)

if __name__ == "__main__":
    run_pipreqs(target_dir=".", savepath="requirements.txt")
