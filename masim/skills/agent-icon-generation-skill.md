---
name: agent-icon-generation-skill
description: Generate and register AGENT_POOL agent icons when a new or forked reusable agent profile is added under examples/AGENT_POOL/{domain}/ during create or polish pipelines, or when polish discovers that any reused pool profile lacks a valid icon. Use this skill whenever an agent is not already covered by the pool and a new pool markdown file is written, or when auditing that every pool agent has a matching icon PNG, Design Provenance Icon row, and agent_images/design.md mapping.
---

# Agent Icon Generation Skill

## Purpose

Create or repair the visual icon that belongs to a reusable AGENT_POOL agent
profile. This skill is invoked after a new or forked pool agent markdown file
is accepted, and before the Step 2 agent audit is closed. During polish, it is
also invoked for a reused pool profile whenever the profile's icon is absent,
broken, misnamed, or missing from `agent_images/design.md`.

The icon is a UI/display asset, not simulation logic. It supports the Agent
Market and reviewer-facing catalogues by giving each reusable agent a stable
visual identity.

## Required Inputs

| Input                    | Source                                                                            |
|--------------------------|-----------------------------------------------------------------------------------|
| Domain                   | `examples/AGENT_POOL/{domain}/<agent>.md` parent folder                           |
| Agent stem               | pool markdown filename without `.md`                                              |
| Agent summary            | pool file `§3.2 Summary` / Summary table                                          |
| Theory family            | pool file Summary + Theoretical Foundation                                        |
| Behavioral role          | pool file Summary + Design Purpose                                                |
| Existing style reference | `examples/AGENT_POOL/agent_images/design.md` and `icon_focused_contact_sheet.jpg` |

## Outputs

| Artefact          | Required path / change                                             |
|-------------------|--------------------------------------------------------------------|
| Icon PNG          | `examples/AGENT_POOL/agent_images/icons/{domain}-{agent-stem}.png` |
| Pool profile link | `                                                                  |
| Mapping row       | Add one row to `examples/AGENT_POOL/agent_images/design.md`        |

## Invocation Rules

Invoke this skill for a pool profile in any of these cases:

- The profile was just created by a `new` AGENT_POOL outcome.
- The profile was just created by a `fork` AGENT_POOL outcome.
- A scenario or variant polish audit discovers an agent identity from a
  target roster, `simulation-bases.md` agent block, variant `players.yml`,
  or implementation module, and the expected pool profile/icon pair for that
  identity is absent.
- A polish audit reuses an existing pool profile but its Design Provenance
  table has no `Icon` row.
- A polish audit finds an `Icon` row whose linked PNG is missing, empty, or
  not named `{domain}-{agent-stem}.png`.
- A polish audit finds that `examples/AGENT_POOL/agent_images/design.md` has
  no row mapping `{domain}/{agent-stem}.md` to
  `{domain}-{agent-stem}.png`.

Do not invent alternate filenames. The agent-to-icon relationship is always:
`examples/AGENT_POOL/{domain}/{agent-stem}.md` maps to
`examples/AGENT_POOL/agent_images/icons/{domain}-{agent-stem}.png`, and
`agent_images/design.md` records that same pair.

For audit mode, derive `{agent-stem}` from the concrete agent identity with
`identity.replace("_", "-")` before checking the filesystem. Example:
`hot_money_funder` expects `finance/hot-money-funder.md` and
`finance-hot-money-funder.png`. Never derive an icon filename from the
scenario name, variant name, display label, or the set of PNGs that already
exists.

## Style Contract

Match the existing icon set in
`examples/AGENT_POOL/agent_images/icon_focused_contact_sheet.jpg` and
`examples/AGENT_POOL/agent_images/icons/`.

**Composition.**

- Square 512x512 PNG.
- Centered circular badge that fills most of the canvas.
- Soft two-color gradient inside the circle; white or transparent outside
  the circle.
- Same friendly robot head in the upper third: rounded white helmet, dark
  screen face, cyan facial details, small antenna points, simple neck circle.
- One large, simple foreground motif in the lower half. The motif must be
  readable at thumbnail size and tied to the agent behavior.
- Rounded white Chinese label tag at the bottom, usually two lines:
  role label on top and role noun below, such as `趋势型` / `投资者`.

**Visual language.**

- Flat/vector-like illustration, clean geometric shapes, high contrast.
- Dark navy outlines for foreground objects; cyan/blue robot accents.
- Existing palette families are preferred: blue/cyan, teal/green, olive,
  gold/orange, coral/red, violet.
- Use only 1 primary motif. Keep the background uncluttered.
- Text appears only in the bottom Chinese label tag.

**Do not generate.**

- No photorealistic people, office scenes, trading floors, screenshots, or
  detailed UI panels.
- No full-body character replacing the standard robot head.
- No 3D render, oil painting, watercolor, anime, pixel art, or logo-only
  style.
- No English text inside the icon artwork, except file/catalog metadata
  outside the image.
- No watermark, signature, brand mark, extra captions, or dense decoration.

## Procedure

1. **Derive the file name and mapping.** Use lowercase kebab-case:
   `{domain}-{agent-stem}.png`. For example,
   `examples/AGENT_POOL/finance/program-trader.md` maps to
   `examples/AGENT_POOL/agent_images/icons/finance-program-trader.png`.
   The mapping row must pair `finance/program-trader.md` with
   `finance-program-trader.png`. If a stale row points to a different
   filename for the same agent, replace it with the canonical mapping.
   During a polish audit, first enumerate the expected identities from the
   selected scenario/variant sources, then apply the same mapping rule to
   each identity. A missing profile `.md` is a profile-definition gap; a
   present profile with no PNG, broken `Icon` row, stale filename, or missing
   `design.md` row is an icon-repair gap.

2. **Derive the display label.** Choose a short Chinese label that matches
   the role, usually `<two-to-four-character role>型投资者` for finance agents.
   Reuse existing label families in `agent_images/design.md` when possible:
   趋势型, 逆向型, 做市型, 风控型, 研究型, 价值型, 情绪型, 防御型, 套利型.
   For non-finance domains, use the domain's natural role noun rather than
   `投资者`.

3. **Choose a motif.** Pick one visible motif that explains the agent at a
   glance. Examples:

   | Role / theory                  | Motif                       |
   |--------------------------------|-----------------------------|
   | Momentum / trend following     | rising arrow, trend line    |
   | Contrarian / reversal          | reverse arrow               |
   | Fundamental value              | diamond, balance, magnifier |
   | Liquidity / market making      | bid-ask book                |
   | Risk control / deleveraging    | shield, gauge, alert        |
   | Information advantage          | eye, network, signal        |
   | Anchoring / slow belief update | anchor, hourglass           |
   | Noise / random behavior        | scattered dots              |

4. **Generate the image.** Use the available image-generation capability with
   this prompt shape:

   ```text
   Create a 512x512 PNG agent icon matching the existing MASim AGENT_POOL
   icon style. Composition: large centered circular badge with soft
   two-color gradient, white/transparent outside the circle, friendly robot
   head in the upper third with rounded white helmet, dark screen face, cyan
   face details and small antenna points. Lower half: one clean flat
   vector-like motif for <motif>, using dark navy outlines and simple
   high-contrast shapes. Bottom: rounded white Chinese label tag with exactly
   this label: <display-label>. Style must match the icon-focused contact
   sheet: flat, clean, geometric, thumbnail-readable. No photorealism, no 3D,
   no full-body character, no complex background, no English text, no
   watermark, no extra captions.
   ```

   If image generation is unavailable in the current environment, stop and
   record a blocking note instead of fabricating an empty placeholder. The
   pool profile must not claim an icon path until the PNG exists.

5. **Save and verify.** Save the PNG at the required path. Verify:
   - The file exists and is non-empty.
   - The image is square, preferably 512x512.
   - The icon visually contains a circular badge, robot character, motif, and
     readable Chinese label.
   - The filename exactly matches `{domain}-{agent-stem}.png`.
   - If visual consistency is uncertain, request review from Qihang or the
     current AGENT_POOL icon owner before marking the icon complete.

6. **Patch the pool profile.** In `## Design Provenance and Versioning`,
   add or update exactly one table row. If a stale or broken `Icon` row
   exists, replace it rather than adding a second row:

   ```markdown
   | Icon | ![](../agent_images/icons/{domain}-{agent-stem}.png) |
   ```

7. **Patch the image mapping.** Add or update one row in
   `examples/AGENT_POOL/agent_images/design.md` under the relevant domain
   mapping table with:
   - Agent path, for example `finance/program-trader.md`
   - Icon filename, for example `finance-program-trader.png`
   - Display label
   - Short match reason tying the motif to the theory or behavior

8. **Record provenance.** Bump the pool profile's `Version` field.

## Validation Checklist

Run these checks three consecutive times during Step 2 closeout:

- [ ] Every referenced pool profile has one `| Icon |` row.
- [ ] The linked PNG exists under `examples/AGENT_POOL/agent_images/icons/`.
- [ ] The PNG filename is `{domain}-{agent-stem}.png`.
- [ ] `agent_images/design.md` has exactly one mapping row pairing
      `{domain}/{agent-stem}.md` with `{domain}-{agent-stem}.png`.
- [ ] The mapping row's display label and match reason are consistent with the
      agent Summary and Theoretical Foundation.
- [ ] Reused pool agents are not regenerated when their existing icon resolves;
      they are generated or repaired when the icon is missing, broken, or
      unmapped.
