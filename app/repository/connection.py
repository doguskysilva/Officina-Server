from app.repository.base import ProjectRepository

_repository: ProjectRepository | None = None


def get_repository() -> ProjectRepository:
    if _repository is None:
        raise RuntimeError("Repository not initialized — call set_repository() first")
    return _repository


def set_repository(repository: ProjectRepository) -> None:
    global _repository
    _repository = repository
