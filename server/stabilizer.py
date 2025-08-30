from __future__ import annotations

"""Hypothesis stabilization utilities."""

from collections import deque
from typing import Deque, List


class Stabilizer:
    """Track stable prefix across streaming ASR hypotheses.

    Parameters
    ----------
    n_history: int, optional
        Number of latest hypotheses to keep for stability estimation. Defaults to 5.
    delimiters: str, optional
        Characters considered as token delimiters. Stable prefix is trimmed to
        the last occurrence of any of these characters. Defaults to ``" .,!?"``.
    """

    def __init__(self, n_history: int = 5, delimiters: str = " .,!?") -> None:
        self.n_history = n_history
        self.delimiters = delimiters
        self.history: Deque[str] = deque(maxlen=n_history)
        self.stable_prefix: str = ""

    def _longest_common_prefix(self, strs: List[str]) -> str:
        if not strs:
            return ""
        prefix = strs[0]
        for s in strs[1:]:
            while not s.startswith(prefix) and prefix:
                prefix = prefix[:-1]
        return prefix

    def _truncate_to_delim(self, text: str) -> str:
        for i in range(len(text) - 1, -1, -1):
            if text[i] in self.delimiters:
                return text[: i + 1]
        return ""

    def get_delta(self, new_hyp: str) -> str:
        """Return newly stabilized part of the hypothesis.

        Parameters
        ----------
        new_hyp: str
            Latest hypothesis string.

        Returns
        -------
        str
            Portion of text that became stable since last invocation.
        """
        self.history.append(new_hyp)

        lcp = self._longest_common_prefix(list(self.history))
        lcp = self._truncate_to_delim(lcp)

        prev = self.stable_prefix
        if not lcp.startswith(prev):
            delta = ""
        else:
            delta = lcp[len(prev) :]
        self.stable_prefix = lcp
        return delta
