from pydantic import BaseModel


class LogConfig(BaseModel):
    DEFAULT_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    ACCESS_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(client_addr)s - %(request_line)s | %(status_code)s"
    LOG_LEVEL: str = "INFO"

    version: int = 1
    disable_existing_loggers: bool = False

    handlers: dict = {
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "default1": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "default": {
            "filename": "error.log",
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "default",
            "encoding": "UTF-8"
        },
    }

    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "format": DEFAULT_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": True,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "format": ACCESS_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "use_colors": True,
        },
    }

    loggers: dict = {
        "uvicorn": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": True},
        "uvicorn.error": {"level": LOG_LEVEL, "propagate": True},
        "uvicorn.access": {"handlers": ["access"], "level": LOG_LEVEL, "propagate": False},
        "sqlalchemy.engine": {"handlers": ["default"], "level": LOG_LEVEL, "propagate": True}
    }
