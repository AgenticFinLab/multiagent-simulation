"""
Implementation of functions to support the record, i.e., save and load, of the results.
"""

import os
import json
import re
from typing import Any, Union


def extract_save_id(savename: str):
    """Extract id of the savename."""
    # Assume savename format is "round_123" or other format containing numbers
    match = re.search(r"(\d+)", savename)
    if match:
        return int(match.group(1))
    return None


def parse_block_filename(block_filename: str):
    """Parse block filename to extract relevant information."""
    # Block filename format is "block_{prefix}_{start_idx}-{end_idx}"
    pattern = r"block_(.+)_(\d+)-(\d+)"
    match = re.search(pattern, block_filename)
    if match:
        start_idx = int(match.group(2))
        end_idx = int(match.group(3))
        return start_idx, end_idx
    return None, None


def whether_new_block(
    folder: str,
    savename: str,
    file_format: str,
    block_size: int,
) -> bool:
    """Determine whether to create a new block file."""
    target_block_file = find_target_block(folder, savename, file_format)

    # No suitable block file found, need to create new file
    if not target_block_file:
        return True

    # Check if existing file is full
    file_path = os.path.join(folder, target_block_file)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            # File is full, need to create new file
            # Now checking dictionary size instead of list size
            if isinstance(existing_data, dict) and len(existing_data) >= block_size:
                return True
    except (json.JSONDecodeError, FileNotFoundError):
        return True  # File has issues, create new file

    return False


def find_target_block(
    folder: str,
    savename: str,
    file_format: str,
) -> str:
    """Find the block file that should store the data based on savename."""
    save_id = extract_save_id(savename)
    if save_id is None:
        return ""

    # Find matching block file where save_id falls within the block range
    for filename in os.listdir(folder):
        if re.match(rf"^block_rounds_\d+-\d+\.{file_format}$", filename):
            start_idx, end_idx = parse_block_filename(
                filename.replace(f".{file_format}", "")
            )
            if start_idx is not None and start_idx <= save_id <= end_idx:
                return filename

    return ""


def get_next_block(
    savename: str,
    file_format: str,
    block_size: int,
) -> str:
    """Generate the next block filename."""
    # Extract basic information from savename
    save_id = extract_save_id(savename)
    if save_id is None:
        save_id = 0

    # Determine the block range that contains this save_id
    start_idx = (save_id // block_size) * block_size
    end_idx = start_idx + block_size - 1

    return f"block_rounds_{start_idx}-{end_idx}.{file_format}"


def save_record(
    data: Any,
    folder: str,
    savename: str,
    file_format: str = "json",
    as_block: bool = True,
    block_size: int = 1000,
):
    """
    Save the record data to a JSON file either as a single file or a block in the file.

    Args:
        data (Any): The data to be saved.
        folder (str): The folder path where the file will be saved.
        savename (str): The name of the file (without extension).
        file_format (str): The format of the file (default: "json").
        as_block (bool): Whether to save as block or single file.
        block_size (int): Maximum number of records per block file.
    """
    # Ensure folder exists
    os.makedirs(folder, exist_ok=True)

    if not as_block:
        # Save as single file
        file_path = os.path.join(folder, f"{savename}.{file_format}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, default=str, ensure_ascii=False, indent=2)
    else:
        # Save as block file - store as dictionary with savename as key
        if whether_new_block(folder, savename, file_format, block_size):
            # Create new block file
            block_filename = get_next_block(
                savename, file_format, block_size=block_size
            )
            file_path = os.path.join(folder, block_filename)
            # Store as dictionary with savename as key
            new_data = {savename: data}
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(new_data, f, default=str, ensure_ascii=False, indent=2)
        else:
            # Add to existing block file
            target_block_file = find_target_block(folder, savename, file_format)
            if target_block_file:
                file_path = os.path.join(folder, target_block_file)
                # Read existing data and add new data
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)

                existing_data[savename] = data

                # Rewrite file
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(
                        existing_data, f, default=str, ensure_ascii=False, indent=2
                    )


def load_record(
    folder: str,
    savename: str,
    file_format: str = "json",
    from_block: bool = True,
) -> Union[Any, None]:
    """
    Load the record data from a file either as a single file or from block files.

    Args:
        folder (str): The folder path where the file is stored.
        savename (str): The name of the file (without extension).
        file_format (str): The format of the file (default: "json").
        as_block (bool): Whether to load from block files or single file.

    Returns:
        Union[Any, Dict[str, Any], None]: The loaded data, or None if file not found.
    """
    # Check if folder exists
    if not os.path.exists(folder):
        return None

    if not from_block:
        # Load from single file
        file_path = os.path.join(folder, f"{savename}.{file_format}")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return None
    else:
        # Load from block files - return the specific entry by savename
        target_block_file = find_target_block(folder, savename, file_format)

        if not target_block_file:
            return None

        file_path = os.path.join(folder, target_block_file)
        with open(file_path, "r", encoding="utf-8") as f:
            block_data = json.load(f)
            if savename in block_data:
                return block_data[savename]
            else:
                return None
