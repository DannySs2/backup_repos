import json
from dataclasses import dataclass
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
