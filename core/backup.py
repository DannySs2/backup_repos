import os
import datetime
import tarfile
import shutil
from core.runner import run

BASE_BACKUP_DIR = "backups"


def get_backup_folder():
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(BASE_BACKUP_DIR, date)
    os.makedirs(path, exist_ok=True)
    return path


def clone_mirror(source, dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    run(["git", "clone", "--mirror", source, dest])


def make_tarball(repo_path):
    tar_path = f"{repo_path}.tar.gz"
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(repo_path, arcname=os.path.basename(repo_path))
    shutil.rmtree(repo_path)
    return tar_path
