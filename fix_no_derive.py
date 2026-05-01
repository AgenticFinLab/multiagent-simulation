import os
import re


def fix_players_py(file_path):
    """Fix LLM/RuleLLM/Rag players.py files to remove quantity-sign derivation and use explicit action field."""
    with open(file_path, "r") as f:
        lines = f.readlines()

    # Find the decide() method
    decide_start = -1
    for i, line in enumerate(lines):
        if "async def decide(self) ->" in line or "def decide(self) ->" in line:
            decide_start = i
            break

    if decide_start == -1:
        print(f"WARNING: No decide() method found in {file_path}")
        return False

    # Find the end of the decide() method (first line that's not indented after a blank line)
    decide_end = len(lines)
    indent_level = None
    for i in range(decide_start + 1, len(lines)):
        stripped = lines[i].lstrip()
        if stripped == "" or stripped.startswith("#"):
            continue
        current_indent = len(lines[i]) - len(stripped)
        if indent_level is None:
            indent_level = current_indent
        if current_indent < indent_level:
            decide_end = i
            break

    # Extract the decide() body
    decide_body = lines[decide_start:decide_end]

    # Look for patterns to replace
    new_body = []
    i = 0
    while i < len(decide_body):
        line = decide_body[i]

        # Pattern 1: "bid_price = float(decision[\"bid_price\"])
        if 'bid_price = float(decision["bid_price"]' in line:
            # Insert action extraction before bid_price
            new_body.append(line)
            # Find where to insert action extraction (after decision parsing but before first bid_price)
            # Look backwards for decision parsing
            j = i - 1
            while j >= 0:
                if "decision =" in decide_body[j] or "parsed =" in decide_body[j]:
                    # Insert action extraction right after this line
                    new_body.insert(-1, '        action = decision["action"]\n')
                    break
                j -= 1
            else:
                # If no decision parsing found, insert at top of decide body
                new_body.insert(0, '        action = decision["action"]\n')
            i += 1
            continue

        # Pattern 2: "if quantity > 0:" and "elif quantity < 0:" blocks
        elif (
            "if quantity > 0:" in line
            or "elif quantity < 0:" in line
            or "if quantity < 0:" in line
            or "if quantity > 0:" in line
        ):
            # Replace with action-based branching
            if "if quantity > 0:" in line:
                new_line = line.replace("if quantity > 0:", 'if action == "buy":')
            elif "elif quantity < 0:" in line:
                new_line = line.replace("elif quantity < 0:", 'elif action == "sell":')
            elif "if quantity < 0:" in line:
                new_line = line.replace("if quantity < 0:", 'if action == "sell":')
            elif "if quantity > 0:" in line:
                new_line = line.replace("if quantity > 0:", 'if action == "buy":')
            else:
                new_line = line

            # Also replace any abs(quantity) calls
            new_line = new_line.replace("abs(quantity)", "quantity")
            new_body.append(new_line)

            # Skip the next lines until we find the end of this block
            j = i + 1
            while j < len(decide_body):
                next_line = decide_body[j]
                if next_line.strip() == "" or next_line.strip().startswith("#"):
                    j += 1
                    continue
                # Check indentation level
                if len(next_line) - len(next_line.lstrip()) <= len(line) - len(
                    line.lstrip()
                ):
                    break
                j += 1

            # Now process the block
            k = i + 1
            while k < j:
                block_line = decide_body[k]
                # Replace any abs(quantity) calls
                if "abs(quantity)" in block_line:
                    block_line = block_line.replace("abs(quantity)", "quantity")
                # Replace quantity > 0 / < 0 with action checks
                if "if quantity > 0:" in block_line:
                    block_line = block_line.replace(
                        "if quantity > 0:", 'if action == "buy":'
                    )
                elif "elif quantity < 0:" in block_line:
                    block_line = block_line.replace(
                        "elif quantity < 0:", 'elif action == "sell":'
                    )
                elif "if quantity < 0:" in block_line:
                    block_line = block_line.replace(
                        "if quantity < 0:", 'if action == "sell":'
                    )
                elif "if quantity > 0:" in block_line:
                    block_line = block_line.replace(
                        "if quantity > 0:", 'if action == "buy":'
                    )
                new_body.append(block_line)
                k += 1

            i = j
            continue

        # Pattern 3: Remove abs(quantity) calls
        elif "abs(quantity)" in line:
            new_line = line.replace("abs(quantity)", "quantity")
            new_body.append(new_line)
            i += 1
            continue

        # Pattern 4: Add validate_order import and call
        elif "return {" in line or "return {" in line:
            # Insert validate_order call before return
            new_body.append("        from masim.format.order import validate_order\n")
            new_body.append("        validate_order(order)\n")
            new_body.append(line)
            i += 1
            continue

        # Pattern 5: Add action to order dict
        elif '"quantity": quantity,' in line:
            # Insert action before quantity
            new_body.append('            "action": action,\n')
            new_body.append(line)
            i += 1
            continue

        # Pattern 6: Add action to order dict (different style)
        elif "order = {" in line:
            new_body.append(line)
            # Look for where to add action
            j = i + 1
            while j < len(decide_body):
                if "}" in decide_body[j]:
                    break
                j += 1
            # Insert action before the closing brace
            new_body.append('            "action": action,\n')
            i += 1
            continue

        new_body.append(line)
        i += 1

    # Replace the decide() body
    new_lines = lines[:decide_start] + new_body + lines[decide_end:]

    # Write back
    with open(file_path, "w") as f:
        f.writelines(new_lines)

    return True


# List of files to fix
files_to_fix = [
    "examples/ArchegosCollapse/LLM/players.py",
    "examples/ArchegosCollapse/RuleLLM/players.py",
    "examples/ArchegosCollapse/Rag/players.py",
    "examples/AsianFinancialCrisis/LLM/players.py",
    "examples/AsianFinancialCrisis/RuleLLM/players.py",
    "examples/AsianFinancialCrisis/Rag/players.py",
    "examples/AssetBubble/LLM/players.py",
    "examples/AssetBubble/RuleLLM/players.py",
    "examples/AssetBubble/Rag/players.py",
    "examples/AvailabilityBias/LLM/players.py",
    "examples/AvailabilityBias/RuleLLM/players.py",
    "examples/AvailabilityBias/Rag/players.py",
    "examples/DispositionEffect/LLM/players.py",
    "examples/EquityPremium/RuleLLM/players.py",
    "examples/EquityPremium/Rag/players.py",
    "examples/FlashCrash/LLM/players.py",
    "examples/FlashCrash/RuleLLM/players.py",
    "examples/FlashCrash/Rag/players.py",
    "examples/FlashCrash2010/LLM/players.py",
    "examples/FlashCrash2010/RuleLLM/players.py",
    "examples/FlashCrash2010/Rag/players.py",
    "examples/HerdEffect/LLM/players.py",
    "examples/HerdEffect/Rag/players.py",
    "examples/LiquidityDryup/LLM/players.py",
    "examples/LiquidityDryup/RuleLLM/players.py",
    "examples/LiquidityDryup/Rag/players.py",
    "examples/MarketCrash/LLM/players.py",
    "examples/MarketCrash/RuleLLM/players.py",
    "examples/MarketCrash/Rag/players.py",
    "examples/MomentumEffect/LLM/players.py",
    "examples/MomentumEffect/RuleLLM/players.py",
    "examples/MomentumEffect/Rag/players.py",
    "examples/ReversalEffect/LLM/players.py",
    "examples/ReversalEffect/RuleLLM/players.py",
    "examples/ReversalEffect/Rag/players.py",
    "examples/ShortSqueeze/LLM/players.py",
    "examples/ShortSqueeze/RuleLLM/players.py",
    "examples/ShortSqueeze/Rag/players.py",
    "examples/VolatilityClustering/LLM/players.py",
    "examples/VolatilityClustering/RuleLLM/players.py",
    "examples/VolatilityClustering/Rag/players.py",
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        print(f"Fixing {file_path}")
        fix_players_py(file_path)
    else:
        print(f"File not found: {file_path}")
