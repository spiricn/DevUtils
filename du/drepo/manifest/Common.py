from enum import Enum


class ProjectOption(Enum):
    """
    Per-project options
    """

    # Project should be cleaned
    CLEAN = 0

    # Project should be re-set
    RESET = 1


# Kept for backward compatibility reasons for now
OPT_CLEAN = ProjectOption.CLEAN
OPT_RESET = ProjectOption.RESET
