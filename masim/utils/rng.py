"""Deterministic RNG helpers for reproducible MASim runs.

The framework derives a per-agent ``random.Random`` from a single run-level
``seed`` (from ``setting.seed``) salted by the agent identity.  Two agents in
the same run therefore receive different streams, while two runs with the same
seed and configuration receive byte-identical streams — the foundation of
reproducible simulation.

When ``seed`` is ``None`` the helper returns a fresh, non-deterministic
``random.Random`` (the historical behaviour), so existing configs without a
seed keep working unchanged.
"""

from __future__ import annotations

import hashlib
import random
from typing import Optional


def derive_rng(seed: Optional[int], salt: str = "") -> random.Random:
    """Return a seeded (or fresh) :class:`random.Random` instance.

    Parameters
    ----------
    seed
        Run-level integer seed from ``setting.seed``. ``None`` disables
        determinism and returns an OS-seeded generator.
    salt
        Stable per-agent discriminator (typically the player identity) so two
        stochastic agents sharing one seed still draw independent streams.
    """
    if seed is None:
        return random.Random()
    digest = hashlib.sha256(f"{seed}:{salt}".encode("utf-8")).hexdigest()
    # random.Random accepts an arbitrary hashable int; truncate to 64 bits to
    # keep the state small and platform-stable.
    return random.Random(int(digest, 16) & ((1 << 64) - 1))
