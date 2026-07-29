import subprocess
import sys


def run(cmd, cwd=None):
    print(f"\u2192 {' '.join(cmd)}")

    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout, end="")

    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else "sin detalle"
        raise RuntimeError(
            f"Error ejecutando comando ({result.returncode}): "
            f"{' '.join(cmd)} | {stderr}"
        )
