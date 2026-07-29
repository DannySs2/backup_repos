import json
import os
import requests
from dataclasses import dataclass, field
from typing import Optional

REPOS_FILE = "repos.json"


@dataclass
class Repo:
    name: str
    source: str
    target: Optional[str] = None
    s3_prefix: Optional[str] = None

    @classmethod
    def from_dict(cls, d):
        return cls(
            name=d["name"],
            source=d["source"],
            target=d.get("target"),
            s3_prefix=d.get("s3_prefix"),
        )


def load_repos():
    with open(REPOS_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    return [Repo.from_dict(r) for r in raw]


def fetch_github_repos():
    token = os.getenv("GITHUB_TOKEN")
    owner = os.getenv("GITHUB_OWNER")
    host = os.getenv("GITHUB_HOST", "github-new")

    if not token:
        raise Exception("Falta GITHUB_TOKEN en .env")
    if not owner:
        raise Exception("Falta GITHUB_OWNER en .env (ej: desarrolloHT2023)")

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }

    repos = []
    page = 1

    org_url = f"https://api.github.com/orgs/{owner}/repos"
    resp = requests.get(f"{org_url}?per_page=1", headers=headers, timeout=30)

    if resp.status_code == 200:
        base_url = org_url + "?per_page=100&page={}"
    else:
        base_url = "https://api.github.com/user/repos?per_page=100&page={}&type=all"

    while True:
        url = base_url.format(page)
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        for r in batch:
            if r.get("fork"):
                continue
            repos.append(Repo(
                name=r["name"],
                source=f"git@{host}:{r['full_name']}",
            ))
        page += 1

    return repos
