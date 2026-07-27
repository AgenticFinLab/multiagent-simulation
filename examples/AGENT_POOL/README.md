# Agent Pool

This folder is the unified workspace for investor-agent profiles.

## Structure

- `ExtractedExampleInvestors/`: agents extracted from the existing `examples/` and `configs/` scenarios.
- `ExtractedExampleInvestors/unique/`: deduplicated market-level agent archetypes.
- `ExtractedExampleInvestors/non-unique/`: original scenario-level extracted profiles before cross-scenario deduplication.
- `agent_images/`: agent icon PNGs (`icons/{domain}-{stem}.png`) and `design.md` catalogue used by the Streamlit Agent Market.

Manually designed / custom investor agents now live alongside this folder at `examples/CUSTOMIZED_SIMULATION/`.

## Notes

The source material was copied from `investment-agents/` so the previous generated catalog remains intact.
