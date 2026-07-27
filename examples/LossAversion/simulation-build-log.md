# LossAversion Simulation Build Log

## §B Research Notes

### §B.1 Theory verification

Five target anchors map bidirectionally to five complete Theory blocks in `simulation-bases.md §2`. DOI resolution was checked for Prospect Theory, Cumulative Prospect Theory, the disposition effect, momentum, and dealer inventory control.

### §B.2 Stylized-fact verification

The canonical facts are acceptance targets for LAI, DEI, BER, WPI, and VAF. The 70%/20% realization fractions are recorded as scenario calibration, not as estimates reported by Odean (1998).

### §B.3 Empirical anchor

Odean's discount-brokerage study provides the primary empirical anchor: 10,000 accounts observed from 1987–1993, with gains realized more readily than losses.

### §B.4 Agent taxonomy

The identified roles are loss-averse investor, break-even trader, rational trader, momentum trader, and market maker. Each resolves to one canonical AGENT_POOL profile.

### §B.5 Parameter expansion

Theory determines parameter direction and valid sensitivity ranges. Scenario-normalized market impact, order caps, and behavioral fractions remain explicit calibration values and must be tested rather than presented as direct estimates.

## §C Surfaced Gaps and Resolutions

- Resolved: canonical scenario target was absent; reconstructed and locked from existing artefacts.
- Resolved: Ho–Stoll DOI had an incorrect terminal digit in the old pool profile.
- Resolved: three pool profiles were stubs and market-maker was structurally incomplete.
- Resolved: three canonical agent icons and image mapping rows were absent.
- Resolved: Rule analysis imported absent module `examples.standard_rule_analysis`; replaced with supported evaluation components plus scenario-specific behavioral metrics.
- Resolved: `price_impact=0.03` contradicted the documented `0.0002` calibration and caused 87.7% mean absolute deviation; restored `0.0002` and added seeded gain/loss identification stimuli.
- Resolved: repeated same-domain realization exhausted inventory; decisions now trigger once per threshold crossing and re-arm in the neutral band.
- Result: formal Rule run completed 200 rounds; all five scenario acceptance metrics and five output files passed.
