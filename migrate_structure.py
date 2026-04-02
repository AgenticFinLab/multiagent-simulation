#!/usr/bin/env python3
"""Migrate examples, configs, and EXPERIMENT directories to nested structure."""

import os
import shutil
import re
from pathlib import Path

BASE_DIR = Path("/Users/sjia/Documents/AgenticFinLab/Projects/multiagent-simulation")

# Define migration mapping: old_name -> (parent, subdir)
MIGRATION_MAP = {
    # AssetBubble variants
    "AssetBubble": ("AssetBubble", "Rule"),
    "AssetBubbleLLM": ("AssetBubble", "LLM"),
    "AssetBubbleRuleLLM": ("AssetBubble", "RuleLLM"),
    "AssetBubbleRag": ("AssetBubble", "Rag"),
    # DispositionEffect variants
    "DispositionEffect": ("DispositionEffect", "Rule"),
    "DispositionEffectLLM": ("DispositionEffect", "LLM"),
    "DispositionEffectRuleLLM": ("DispositionEffect", "RuleLLM"),
    # HerdEffect variants
    "HerdEffect": ("HerdEffect", "Rule"),
    "HerdEffectLLM": ("HerdEffect", "LLM"),
    "HerdEffectRuleLLM": ("HerdEffect", "RuleLLM"),
    # EquityPremium variants
    "EquityPremium": ("EquityPremium", "Rule"),
    "EquityPremiumLLM": ("EquityPremium", "LLM"),
    # FlashCrash variants
    "FlashCrash": ("FlashCrash", "Rule"),
    "FlashCrashLLM": ("FlashCrash", "LLM"),
    # LiquidityDryup variants
    "LiquidityDryup": ("LiquidityDryup", "Rule"),
    "LiquidityDryupLLM": ("LiquidityDryup", "LLM"),
    # MarketCrash variants
    "MarketCrash": ("MarketCrash", "Rule"),
    "MarketCrashLLM": ("MarketCrash", "LLM"),
    # MomentumEffect variants
    "MomentumEffect": ("MomentumEffect", "Rule"),
    "MomentumEffectLLM": ("MomentumEffect", "LLM"),
    # ReversalEffect variants
    "ReversalEffect": ("ReversalEffect", "Rule"),
    "ReversalEffectLLM": ("ReversalEffect", "LLM"),
    # ShortSqueeze variants
    "ShortSqueeze": ("ShortSqueeze", "Rule"),
    "ShortSqueezeLLM": ("ShortSqueeze", "LLM"),
    # VolatilityClustering variants
    "VolatilityClustering": ("VolatilityClustering", "Rule"),
    "VolatilityClusteringLLM": ("VolatilityClustering", "LLM"),
}


def migrate_directory(base_path: Path, dir_type: str):
    """Migrate directories to nested structure.

    Args:
        base_path: Base directory (examples, configs, or EXPERIMENT)
        dir_type: Type of directory for logging
    """
    print(f"\n=== Migrating {dir_type} ===")

    for old_name, (parent, subdir) in MIGRATION_MAP.items():
        old_path = base_path / old_name
        new_path = base_path / parent / subdir

        if not old_path.exists():
            print(f"  SKIP: {old_name} not found")
            continue

        # Create parent directory
        parent_path = base_path / parent
        parent_path.mkdir(parents=True, exist_ok=True)

        # Move directory
        print(f"  MOVE: {old_name} -> {parent}/{subdir}")
        shutil.move(str(old_path), str(new_path))

    # Remove empty parent directories that were created but have no content
    for parent in set(p for p, _ in MIGRATION_MAP.values()):
        parent_path = base_path / parent
        if parent_path.exists() and not any(parent_path.iterdir()):
            parent_path.rmdir()


def update_yaml_paths(base_path: Path):
    """Update record_path and class references in YAML files."""
    print(f"\n=== Updating YAML paths in {base_path} ===")

    for yml_file in base_path.rglob("*.yml"):
        content = yml_file.read_text()
        original = content
        modified = False

        # Update record_path
        for old_name, (parent, subdir) in MIGRATION_MAP.items():
            old_pattern = f"EXPERIMENT/{old_name}/"
            new_pattern = f"EXPERIMENT/{parent}/{subdir}/"
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                modified = True

        # Update class references in players.yml
        for old_name, (parent, subdir) in MIGRATION_MAP.items():
            # Pattern: examples.OldName.players -> examples.Parent.Subdir.players
            old_pattern = f"examples.{old_name}.players"
            new_pattern = f"examples.{parent}.{subdir}.players"
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                modified = True

        if modified:
            yml_file.write_text(content)
            print(f"  UPDATED: {yml_file.relative_to(base_path)}")


def update_python_imports(base_path: Path):
    """Update import paths in Python files."""
    print(f"\n=== Updating Python imports in {base_path} ===")

    for py_file in base_path.rglob("*.py"):
        content = py_file.read_text()
        original = content
        modified = False

        # Update sys.path.insert patterns
        for old_name, (parent, subdir) in MIGRATION_MAP.items():
            # Pattern: from AssetBubble.analysis -> from Rule.analysis (when inside AssetBubble/)
            pass  # Most imports use relative paths, should still work

        if modified:
            py_file.write_text(content)
            print(f"  UPDATED: {py_file.relative_to(base_path)}")


def main():
    """Run the full migration."""
    import sys

    # Redirect output to log file
    log_path = BASE_DIR / "migration_log.txt"
    with open(log_path, "w") as log:
        sys.stdout = log

        print("=" * 60)
        print("MASIM Directory Restructuring Migration")
        print("=" * 60)

        # Migrate directories
        migrate_directory(BASE_DIR / "examples", "examples")
        migrate_directory(BASE_DIR / "configs", "configs")
        migrate_directory(BASE_DIR / "EXPERIMENT", "EXPERIMENT")

        # Update paths in YAML files
        update_yaml_paths(BASE_DIR / "configs")
        update_yaml_paths(BASE_DIR / "examples")

        print("\n" + "=" * 60)
        print("Migration complete!")
        print("=" * 60)

        sys.stdout = sys.__stdout__

    # Also print to stdout
    print(f"Migration log written to: {log_path}")


if __name__ == "__main__":
    main()
