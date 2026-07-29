from abc import ABC, abstractmethod
from core.models import Repo


class Target(ABC):
    @abstractmethod
    def migrate(self, repo: Repo, temp_dir: str, tar_path: str):
        ...
