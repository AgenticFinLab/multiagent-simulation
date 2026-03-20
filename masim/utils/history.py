"""History Buffer utility for memory-efficient state management.

Provides HistoryBuffer - a hybrid storage that combines:
- Hot data: deque(maxlen=entry_limit) for recent entries (O(1) access)
- Cold data: BlockBasedStoreManager for historical entries (disk-based)

Usage Pattern:
    buffer = HistoryBuffer(
        folder="records/market/price",
        entry_limit=100,
        block_size=50,
    )

    # Append data each round
    buffer.append(price)  # Automatically persists when deque overflows

    # Access recent data (from hot deque)
    recent = buffer[-1]         # Last item
    last_10 = buffer[-10:]      # Last 10 items (slice)

    # Access all data (hot + cold)
    all_data = buffer.get_all()  # Reads cold from disk + hot

    # Access specific index
    value = buffer.get(0)        # First item ever (from cold storage)

Memory Profile:
    - With entry_limit=100: Only 100 items in memory
    - Historical data: Persisted to disk, loaded on-demand
    - At 20,000 rounds: ~100 items in memory vs 20,000 without buffer
"""

import os
from collections import deque
from typing import Any, List, Optional, Union

from lmbase.utils.tools import BlockBasedStoreManager


class HistoryBuffer:
    """
    Memory-efficient history storage with automatic disk persistence.

    ┌─────────────────────────────────────────────────────────────────────┐
    │                     ARCHITECTURE                                     │
    ├─────────────────────────────────────────────────────────────────────┤
    │                                                                      │
    │  HOT (Memory)              COLD (Disk)                              │
    │  ┌─────────────┐           ┌─────────────────────────────────┐      │
    │  │   deque     │  overflow │   BlockBasedStoreManager        │      │
    │  │ maxlen=100  │ ───────►  │   (JSON blocks, block_size=50)  │      │
    │  └─────────────┘           └─────────────────────────────────┘      │
    │                                                                      │
    │  Access Pattern:                                                     │
    │  - buffer[-1]     → hot (fast)                                      │
    │  - buffer[0]      → cold (disk read)                                │
    │  - buffer.get_all() → cold + hot (complete history)                 │
    │                                                                      │
    └─────────────────────────────────────────────────────────────────────┘

    Attributes:
        folder: Directory path for cold storage
        entry_limit: Maximum items in hot deque
        block_size: Number of entries per block file
        hot: Recent data in memory (deque)
        cold_store: Historical data manager (BlockBasedStoreManager)
        cold_count: Total items persisted to cold storage
        total_count: Total items ever appended
    """

    def __init__(
        self,
        folder: str,
        entry_limit: int = 100,
        block_size: int = 50,
        initial_values: Optional[List[Any]] = None,
    ):
        """
        Initialize HistoryBuffer.

        Args:
            folder: Directory path for disk storage
            entry_limit: Max items in hot deque (default: 100)
            block_size: Items per block file (default: 50)
            initial_values: Optional list of initial values to populate
        """
        self.folder = folder
        self.entry_limit = entry_limit
        self.block_size = block_size

        # Hot storage (recent data in memory)
        self.hot: deque = deque(maxlen=entry_limit)

        # Cold storage (historical data on disk)
        os.makedirs(folder, exist_ok=True)
        self.cold_store = BlockBasedStoreManager(
            folder=folder,
            file_format="json",
            block_size=block_size,
        )

        # Counters
        self.cold_count: int = 0  # Items in cold storage
        self.total_count: int = 0  # Total items ever appended

        # Pending cold writes (batch before flush)
        self._pending_cold: List[Any] = []

        # Initialize with initial values if provided
        if initial_values:
            for value in initial_values:
                self.append(value)

    def append(self, value: Any) -> None:
        """
        Append a value to the buffer.

        If hot deque is full, overflow is moved to cold storage.

        Args:
            value: Value to append
        """
        # If deque is full, the oldest item will be evicted
        if len(self.hot) == self.entry_limit:
            # Move oldest item to cold pending list
            oldest = self.hot[0]  # Will be evicted
            self._pending_cold.append(oldest)

            # Flush to disk when batch is ready
            if len(self._pending_cold) >= self.block_size:
                self._flush_pending()

        self.hot.append(value)
        self.total_count += 1

    def _flush_pending(self) -> None:
        """Flush pending cold items to disk."""
        if not self._pending_cold:
            return

        # Save batch with sequential naming
        batch_start = self.cold_count
        batch_end = batch_start + len(self._pending_cold) - 1
        savename = f"batch_{batch_start:08d}_{batch_end:08d}"

        self.cold_store.save(savename=savename, data=self._pending_cold)
        self.cold_count += len(self._pending_cold)
        self._pending_cold = []

    def flush(self) -> None:
        """Force flush ALL pending items (pending_cold + hot) to disk.

        This must be called at simulation shutdown to ensure the final
        incomplete batch — items still in the hot deque that were never
        evicted — is written to disk.
        """
        # Move all hot items into pending_cold in order
        # (hot deque is ordered oldest-first)
        self._pending_cold.extend(list(self.hot))
        self.hot.clear()
        self._flush_pending()

    def __len__(self) -> int:
        """Return total count of items (hot + cold + pending)."""
        return self.total_count

    def __iter__(self):
        """Iterate over hot (recent) items only. For all items, use get_all()."""
        return iter(self.hot)

    def __getitem__(self, index: Union[int, slice]) -> Any:
        """
        Access items by index or slice.

        Negative indices access from end (hot data).
        Non-negative indices access from start (may require cold read).

        Args:
            index: Integer index or slice

        Returns:
            Value at index or list of values for slice
        """
        if isinstance(index, slice):
            return self._get_slice(index)
        return self.get(index)

    def get(self, index: int) -> Any:
        """
        Get item at specific index.

        Args:
            index: Index (negative for recent, positive for historical)

        Returns:
            Value at index

        Raises:
            IndexError: If index out of range
        """
        # Handle negative indices
        if index < 0:
            index = self.total_count + index

        if index < 0 or index >= self.total_count:
            raise IndexError(f"Index {index} out of range [0, {self.total_count})")

        # Check if in hot deque
        hot_start_index = self.cold_count + len(self._pending_cold)
        if index >= hot_start_index:
            hot_index = index - hot_start_index
            return self.hot[hot_index]

        # Check if in pending cold
        if index >= self.cold_count:
            pending_index = index - self.cold_count
            return self._pending_cold[pending_index]

        # Must load from cold storage
        return self._load_from_cold(index)

    def _get_slice(self, s: slice) -> List[Any]:
        """Get items for a slice."""
        start, stop, step = s.indices(self.total_count)
        return [self.get(i) for i in range(start, stop, step)]

    def _load_from_cold(self, index: int) -> Any:
        """
        Load a specific index from cold storage.

        Args:
            index: Global index to load

        Returns:
            Value at index
        """
        # Find which batch contains this index
        # Batches are named: batch_00000000_00000499, batch_00000500_00000999, etc.
        batch_start = (index // self.block_size) * self.block_size
        batch_end = min(batch_start + self.block_size - 1, self.cold_count - 1)
        savename = f"batch_{batch_start:08d}_{batch_end:08d}"

        try:
            batch_data = self.cold_store.load(savename=savename)
            local_index = index - batch_start
            return batch_data[local_index]
        except Exception:
            raise IndexError(f"Failed to load index {index} from cold storage")

    def get_recent(self, n: int) -> List[Any]:
        """
        Get the n most recent items (from hot deque).

        This is O(1) as it only accesses memory.

        Args:
            n: Number of recent items to get

        Returns:
            List of n most recent items
        """
        n = min(n, len(self.hot))
        return list(self.hot)[-n:]

    def get_all(self) -> List[Any]:
        """
        Get all items (cold + pending + hot).

        WARNING: This loads ALL cold data from disk. Use sparingly.

        Returns:
            Complete list of all items in chronological order
        """
        result = []

        # Load all cold batches
        for batch_start in range(0, self.cold_count, self.block_size):
            batch_end = min(batch_start + self.block_size - 1, self.cold_count - 1)
            savename = f"batch_{batch_start:08d}_{batch_end:08d}"
            try:
                batch_data = self.cold_store.load(savename=savename)
                result.extend(batch_data)
            except Exception:
                pass  # Skip missing batches

        # Add pending cold
        result.extend(self._pending_cold)

        # Add hot
        result.extend(list(self.hot))

        return result

    def __repr__(self) -> str:
        return (
            f"HistoryBuffer(total={self.total_count}, "
            f"hot={len(self.hot)}, cold={self.cold_count}, "
            f"pending={len(self._pending_cold)})"
        )

    @property
    def recent(self) -> List[Any]:
        """Get hot deque contents as list (most recent items in memory)."""
        return list(self.hot)


# =============================================================================
# Convenience Factory Functions
# =============================================================================


def create_history_buffer(
    base_path: str,
    name: str,
    entry_limit: int = 100,
    initial_value: Optional[Any] = None,
) -> HistoryBuffer:
    """
    Create a HistoryBuffer with standard configuration.

    Args:
        base_path: Base directory for storage
        name: Buffer name (used as subdirectory)
        entry_limit: Max items in hot deque
        initial_value: Optional initial value to append

    Returns:
        Configured HistoryBuffer
    """
    folder = os.path.join(base_path, name)
    buffer = HistoryBuffer(folder=folder, entry_limit=entry_limit)
    if initial_value is not None:
        buffer.append(initial_value)
    return buffer
