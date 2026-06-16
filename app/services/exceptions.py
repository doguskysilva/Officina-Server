class ServiceError(Exception):
    pass


class ProjectNotFound(ServiceError):
    def __init__(self) -> None:
        super().__init__("Project not found")


class ProjectConflict(ServiceError):
    pass
