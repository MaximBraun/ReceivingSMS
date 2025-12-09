import logging
from logging.config import dictConfig

from app.core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()

    level = "DEBUG" if settings.app_debug else "INFO"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
            },
            "loggers": {
                "uvicorn": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "app": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
        }
    )

    logging.getLogger("app").info("Logging is configured", extra={"env": settings.app_env})