import os
import requests
from core.models import Repo
from core.runner import run
from targets.base import Target

COMMON_LFS_PATTERNS = [
    "*.zip", "*.rar", "*.7z", "*.mp4", "*.mov", "*.avi",
    "*.mkv", "*.iso", "*.sql", "*.bak", "*.jar", "*.war",
    "*.tar", "*.gz", "*.pdf", "*.psd",
]


class GithubTarget(Target):
    def migrate(self, repo: Repo, temp_dir: str, tar_path: str):
        if not repo.target:
            raise RuntimeError(f"Repo '{repo.name}' no tiene 'target' para GitHub")

        print(f"\n[MIGRATE github] {repo.name}")

        self._create_repo(repo.name)
        self._apply_lfs(temp_dir)
        self._push_mirror(repo.target, temp_dir)

    def _create_repo(self, repo_name):
        token = os.getenv("GITHUB_TOKEN")
        if not token:
            raise Exception("Falta GITHUB_TOKEN en .env")

        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }
        data = {"name": repo_name, "private": True}

        try:
            resp = requests.post(
                "https://api.github.com/user/repos",
                headers=headers,
                json=data,
                timeout=20,
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Error de red creando repo {repo_name}: {e}") from e

        if resp.status_code == 201:
            print(f"Repo creado en GitHub: {repo_name}")
        elif resp.status_code == 422:
            print(f"Repo ya existe: {repo_name}")
        else:
            raise Exception(f"Error creando repo: {resp.text}")

    def _apply_lfs(self, repo_path):
        print("Inicializando Git LFS...")
        run(["git", "lfs", "install"], cwd=repo_path)
        print("Migrando archivos grandes a Git LFS...")
        include = ",".join(COMMON_LFS_PATTERNS)
        run(
            ["git", "lfs", "migrate", "import", "--everything", f"--include={include}"],
            cwd=repo_path,
        )
        print("Git LFS aplicado")

    def _push_mirror(self, target_url, repo_path):
        run(["git", "remote", "set-url", "origin", target_url], cwd=repo_path)
        run(["git", "push", "--mirror"], cwd=repo_path)
        print("Push a GitHub completado")
