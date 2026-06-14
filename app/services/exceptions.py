class ServiceError(Exception):
    """Base class for application service errors."""


class ProjectNotFound(ServiceError):
    def __init__(self) -> None:
        super().__init__("Project not found")


class ProjectConflict(ServiceError):
    pass
