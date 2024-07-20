import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def make_logger(verbosity: Optional[int] = None) -> logging.Logger:  # type: ignore
    """Make a consistent logger that respects persistent verbosity settings."""
    logger = logging.getLogger("qor-collection")  # type: ignore
    logger.setLevel(logging.DEBUG)  # type: ignore

    if len(logger.handlers) != 2 or (not Path("/dev/log").exists() and len(logger.handlers) != 1):
        formatter = logging.Formatter("%(message)s")  # type: ignore

        stderr = logging.StreamHandler(stream=sys.stderr)  # type: ignore
        stderr.setFormatter(formatter)
        if verbosity is not None:
            stderr.setLevel(40 - (min(3, verbosity) * 10))
        else:
            stderr.setLevel(40)
        logger.addHandler(stderr)

        if Path("/dev/log").exists():
            syslog = logging.handlers.SysLogHandler(address="/dev/log")
            syslog.setFormatter(formatter)
            syslog.setLevel(logging.INFO)  # type: ignore
            logger.addHandler(syslog)
    else:
        if verbosity is not None:
            stderr = logger.handlers[0]
            # Never lower the verbosity after it's been made high
            stderr.setLevel(min(stderr.level, 40 - (min(3, verbosity) * 10)))

    return logger
