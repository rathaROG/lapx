# Copyright (c) 2026 Ratha SIV | MIT License

import os
from typing import Optional


def _normalize_threads(n_threads: Optional[int]) -> int:
    """Use the CPU count for None or zero. Convert other values to an integer.

    Return at least one worker.
    """
    if n_threads is None or n_threads == 0:
        return max(1, int(os.cpu_count() or 1))
    return max(1, int(n_threads))
