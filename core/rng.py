"""Deterministyczny RNG — seed zapisany w stanie gry dla powtarzalności."""
from __future__ import annotations

import random


class GameRNG:
    """Opakowanie na random.Random z seedem zapisanym w stanie gry."""

    def __init__(self, seed: int = 0) -> None:
        self._rng = random.Random(seed)

    @property
    def seed(self) -> int:
        return self._rng.seed if hasattr(self._rng, "seed") else 0

    def reseed(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def random(self) -> float:
        return self._rng.random()

    def uniform(self, a: float, b: float) -> float:
        return self._rng.uniform(a, b)

    def randint(self, a: int, b: int) -> int:
        return self._rng.randint(a, b)

    def chance(self, p: float) -> bool:
        """Zwraca True z prawdopodobieństwem p (0.0-1.0)."""
        return self._rng.random() < p

    def choice(self, seq):
        return self._rng.choice(seq)