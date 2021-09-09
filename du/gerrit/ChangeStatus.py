from enum import Enum


class ChangeStatus(Enum):
    """
    Change status
    """

    # Change is still being reviewed
    NEW = 1

    # Change has been merged to its branch
    MERGED = 2

    # Change was abandoned by its owner or administrator
    ABANDONED = 3
