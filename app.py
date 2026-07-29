import sys
import os
import shutil
from dotenv import load_dotenv

from core.models import load_repos
from core.backup import get_backup_folder, clone_mirror, make_tarball
from targets.github import GithubTarget
from targets.s3 import S3Target

load_dotenv()

TARGETS = {
    "github": GithubTarget(),
    "s3": S3Target(),
}


def cmd_backup():
    repos = load_repos()
    backup_path = get_backup_folder()

    for repo in repos:
        print(f"\n[BACKUP] {repo.name}")
        repo_path = os.path.join(backup_path, f"{repo.name}.git")
        clone_mirror(repo.source, repo_path)
        tar_path = make_tarball(repo_path)
        print(f"OK backup: {tar_path}")

    print(f"\nBackups en: {backup_path}")


def cmd_migrate(target_name: str):
    target = TARGETS.get(target_name)
    if not target:
        print(f"Target inválido: {target_name}. Opciones: {', '.join(TARGETS)}")
        sys.exit(1)

    repos = load_repos()

    for repo in repos:
        temp_dir = f"/tmp/{repo.name}.git"

        try:
            clone_mirror(repo.source, temp_dir)
            tar_path = make_tarball(temp_dir)
            target.migrate(repo, temp_dir, tar_path)
        except Exception as e:
            print(f"FALLO en {repo.name}: {e}")
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def main():
    if len(sys.argv) < 2:
        print("Uso: python app.py [backup | migrate github|s3]")
        return

    mode = sys.argv[1]

    if mode == "backup":
        cmd_backup()
    elif mode == "migrate":
        if len(sys.argv) < 3:
            print("Uso: python app.py migrate [github | s3]")
            return
        cmd_migrate(sys.argv[2])
    else:
        print(f"Modo inválido: {mode}. Usa: backup o migrate")


if __name__ == "__main__":
    main()
