"""The store on files in git: the only package that runs git or touches the record files."""

from lodge.gitstore.errors import GitMissing, NotARepository, NotInitialised
from lodge.gitstore.git import request_exit
from lodge.gitstore.settings import ProjectSettings, StoreSettings, load_settings
from lodge.gitstore.setup import data_root, holds_records, init_store, open_store, repo_root

__all__ = [
    "GitMissing",
    "NotARepository",
    "NotInitialised",
    "ProjectSettings",
    "StoreSettings",
    "data_root",
    "holds_records",
    "init_store",
    "load_settings",
    "open_store",
    "repo_root",
    "request_exit",
]
