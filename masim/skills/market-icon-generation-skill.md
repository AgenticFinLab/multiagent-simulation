---
name: market-icon-generation-skill
description: Generate and register AGENT_POOL market-coordinator icons when a new or forked market profile is added under examples/AGENT_POOL/market/{market-type}-{stem}.md during create or polish pipelines, or when polish discovers that a reused market profile lacks a valid icon. Market Type (stock/fx/opinion/etc.) is a first-class classifier and MUST be reflected in the icon filename, the visual motif, and the Chinese label tag.
---

# Market Icon Generation Skill

## Purpose

Create or repair the visual icon that belongs to a reusable
AGENT_POOL **market coordinator** profile. This skill is a sibling of
`agent-icon-generation-skill.md`; that skill covers participant agents
under `examples/AGENT_POOL/{finance,opinion}/`. This skill covers
market coordinators under `examples/AGENT_POOL/market/`.

Market coordinators differ from participant agents in one crucial
way: they are defined primarily by *what kind of market they are*
(stock, FX, opinion, information, deposit, …). This skill therefore
elevates **Market Type** to a required naming and visual dimension.

## Required Inputs

| Input                    | Source                                                                            |
|--------------------------|-----------------------------------------------------------------------------------|
| Market Type slug         | Row 1 of the profile's `## Summary` table (canonical slug from `market-design-skill.md §2.1`) |
| Coordinator stem         | Profile filename without `.md`, with the `{market-type}-` prefix stripped         |
| Coordinator summary      | Profile `## Summary` table                                                        |
| Mechanism family         | Profile Summary row `Mechanism Family` + `## Theoretical / Mechanistic Foundation` |
| Feedback direction       | Profile Summary row `Feedback Direction`                                          |
| Existing style reference | `examples/AGENT_POOL/agent_images/design.md` and `icon_focused_contact_sheet.jpg` |
| Participant icon set     | `examples/AGENT_POOL/agent_images/icons/finance-*.png` (for style consistency)    |

## Outputs

| Artefact              | Required path / change                                                                              |
|-----------------------|-----------------------------------------------------------------------------------------------------|
| Icon PNG              | `examples/AGENT_POOL/agent_images/icons/market/{market-type}-{coordinator-stem}.png`                |
| Profile icon row      | `| Icon | ![](../agent_images/icons/market/{market-type}-{coordinator-stem}.png) |` in §4.11        |
| Design.md mapping row | Add one row under a `## Mapping: market/ coordinators → icons/market/` section in `agent_images/design.md` |

## Invocation Rules

Invoke this skill for a market profile in any of these cases:

- The profile was just created by a new AGENT_POOL market outcome
  (e.g. a scenario introduced a novel coordination mechanism).
- The profile was just forked (e.g. splitting `stock-standard-price-impact`
  into a fast-mean-reversion variant).
- A scenario or variant polish audit discovers a coordinator identity
  in `simulation-bases.md`, in a variant's `players.yml` market block,
  or in the code, and the expected profile/icon pair is absent.
- A polish audit finds an `Icon` row whose linked PNG is missing,
  empty, or not named `{market-type}-{stem}.png`.
- A polish audit finds that `agent_images/design.md` has no mapping
  row for the coordinator.

Do not invent alternate filenames. The market-to-icon relationship
is always:

```
examples/AGENT_POOL/market/{market-type}-{stem}.md
    ↔ examples/AGENT_POOL/agent_images/icons/market/{market-type}-{stem}.png
```

`{market-type}` MUST be one of the canonical slugs from
`market-design-skill.md §2.1` (`stock`, `fx`, `commodity`, `bond`,
`deposit`, `credit`, `crypto`, `historical-asset`, `derivatives`,
`opinion`, `information`). No other prefixes are permitted. The
profile author is responsible for adding a new slug to `§2.1` (with
evidence) before generating an icon under a new prefix.

## Market Type → Visual Motif Palette

**Market Type dominates the icon's visual identity.** The Market-Type
element is the *primary symbol* (large, centered, upper 55–65% of
the badge). The mechanism motif is the *secondary symbol* (smaller,
below the primary). Together they form a two-tier concept diagram.
This contrasts with participant icons, which show a robot head +
one small motif.

| Market Type slug   | Chinese label root | Primary motif element                       | Palette family   |
|--------------------|--------------------|---------------------------------------------|------------------|
| `stock`            | 股票               | Candlestick / equity chart bar              | blue / cyan      |
| `fx`               | 外汇               | Two currency arrows crossing                | teal / green     |
| `commodity`        | 商品               | Barrel / grain / raw-material cube          | gold / orange    |
| `bond`             | 债券               | Bond certificate + yield curve              | olive / navy     |
| `deposit`          | 存款               | Bank vault door + coin stack                | slate / gold     |
| `credit`           | 信贷               | Loan contract + handshake / seal            | olive / gold     |
| `crypto`           | 加密               | Blockchain block + peg link                 | violet / cyan    |
| `historical-asset` | 历史资产           | Antique quill + subscription certificate    | sepia / gold     |
| `derivatives`      | 衍生品             | Option payoff kink / volatility surface     | coral / violet   |
| `opinion`          | 舆论               | Speech bubbles converging / diverging       | violet / cyan    |
| `information`      | 信息               | Signal-propagation network + megaphone      | coral / cyan     |

Below the primary Market-Type symbol, add a **mechanism motif** that
signals the specific coordinator behaviour:

| Mechanism family                       | Secondary motif element                    |
|----------------------------------------|--------------------------------------------|
| Standard price-impact + mean-reversion | Anchor + small centering arrows            |
| Order-book matching                    | Layered bid/ask book stack                 |
| Reserve-depletion / peg defence        | Draining reservoir + shield                |
| Rumour / SIS contagion propagation     | Radiating waves from a central node        |
| DeGroot / averaging opinion dynamics   | Converging arrows toward a centroid        |
| Threshold cascade                      | Falling dominoes                           |
| Positive-feedback amplifier            | Upward-spiralling arrow                    |
| Random-walk / pure-noise baseline      | Scattered dots on a horizontal axis        |

The combined composition is: **Market-Type primary symbol on top
(large, centered), mechanism motif below (smaller, centered), Chinese
label pill at the bottom**. Both symbols MUST be readable at 128×128
thumbnail size.

## Chinese Label Tag Convention

Market coordinators use the noun **协调器** or **场** (rather than
`投资者` which is reserved for participant agents). Choose based on
what the coordinator actually does:

- **协调器** — for coordinators that clear a matching-engine-like
  process (stock, fx, commodity, bond, derivatives).
- **场** — for coordinators that maintain a diffuse environmental
  field (opinion场, 信息场).
- **系统** — for coordinators that model an institutional system
  (deposit系统, 信贷系统).

Format the label as two lines: role/mechanism on top, market-type
noun on the bottom. Examples:

- `股票市场` / `协调器` for a `stock-standard-price-impact` coordinator
- `外汇市场` / `汇率协调器` for an `fx-reserve-depletion` coordinator
- `舆论场` / `回声室型` for an `opinion-echo-chamber-clustering` coordinator
- `信息场` / `谣言传播型` for an `information-sis-contagion` coordinator
- `存款系统` / `挤兑协调器` for a `deposit-bank-run` coordinator

## Style Contract

Market coordinators are **environment / field / system** objects, NOT
participant agents. The icon visual language MUST reflect this
distinction. A user scanning `agent_images/icons/` in a file browser
should be able to tell player-icons from coordinator-icons *at a
glance*, without reading labels.

**Player vs. Environment — icon language boundary.**

| Family                 | Directory                    | Visual language          | Central subject                              |
|------------------------|------------------------------|--------------------------|----------------------------------------------|
| Participant agents     | `icons/finance/`, `icons/opinion/` | Robot head + one motif   | Friendly robot head (an actor)               |
| Market coordinators    | `icons/market/`              | **Headless · dual-motif** | Market-Type primary symbol (a mechanism)     |

Coordinator icons contain **no robot head, no face, no antenna, no
character**. The subject is the mechanism itself.

**Composition (coordinator icons).**

- Square 512×512 PNG.
- Centered circular badge that fills most of the canvas.
- Soft two-color gradient inside the circle; **pure white** outside
  the circle (never transparent, never checkerboard).
- Upper 55–65% of the circle: **Market-Type primary symbol** — a
  large, flat vector diagram of the Market-Type motif (see §"Market
  Type → Visual Motif Palette"), rendered in dark navy `#1E293B`
  outlines with palette-family fill accents. This is the icon's
  hero element.
- Lower 20–25% (above the label): **mechanism motif** — a smaller
  secondary symbol positioned centrally under the primary symbol,
  visually subordinate but readable at thumbnail size.
- Bottom 15–20%: **rounded white Chinese label pill** with the
  two-line label per the convention above. This is the ONLY text
  in the icon.
- A subtle horizontal separator (thin light-navy divider or gradient
  band) MAY appear between the primary and secondary motifs to
  reinforce the "hierarchy of concept" reading.

**Composition rules.**

1. **No character.** Do NOT draw a robot, humanoid, face, eyes,
   antenna, helmet, or any anthropomorphic element. The coordinator
   is a mechanism, not an actor.
2. **Primary-first hierarchy.** The Market-Type element MUST be
   larger and more prominent than the mechanism element (roughly
   2×–3× the visual weight). Reading order is: Market-Type → mechanism
   → label.
3. **Central alignment.** Both motifs are centered horizontally.
   Do not stack them side-by-side; do not push the primary symbol
   into a corner.
4. **Label noun.** Bottom label uses `协调器 / 场 / 系统` per the
   convention above, NEVER `投资者`.

**Visual language.**

- Flat / vector-like illustration, clean geometric shapes, high
  contrast — matches the aesthetic of participant icons but with
  mechanism as subject.
- Dark navy `#1E293B` outlines for foreground objects; palette-family
  fills per Market Type.
- Palette family follows the Market-Type table above.
- Keep the background uncluttered — a single mechanism reads better
  than a busy scene.
- Text appears only in the bottom Chinese label pill.
- Optional subtle background texture inside the badge: faint gridlines
  for `stock`/`bond`/`derivatives`, faint radial rings for `opinion`/
  `information`, faint hexagonal lattice for `crypto`. Keep at ≤15%
  opacity so it does not compete with the primary symbol.

**Do not generate.**

- **No robot head, humanoid, face, eyes, antenna, helmet, or any
  anthropomorphic element anywhere in the icon.** This is the single
  most important rule that distinguishes coordinator icons from
  participant icons.
- No photorealistic trading floors, exchanges, servers, or
  screenshots.
- No 3D render, oil painting, watercolour, anime, pixel art, or
  logo-only style.
- No English text inside the icon artwork.
- No watermark, signature, brand mark, extra captions, or dense
  decoration.
- No sticker outline halo around the badge.
- No transparent or checkerboard background — pure white outside
  the circle.
- No participant `投资者` noun in the label tag.

## Procedure

1. **Derive the file name and mapping.** Use lowercase kebab-case
   with the Market-Type slug as prefix:

   ```
   examples/AGENT_POOL/market/{market-type}-{stem}.md
       →
   examples/AGENT_POOL/agent_images/icons/market/{market-type}-{stem}.png
   ```

   Example: profile `market/stock-standard-price-impact.md` maps to
   icon `icons/market/stock-standard-price-impact.png`. If a stale
   row in `design.md` points elsewhere, replace it with the canonical
   mapping. If a stale PNG exists at
   `icons/{market-type}-{stem}.png` (missing the `market/`
   subdirectory), MOVE it to the correct subdirectory rather than
   creating a duplicate.

2. **Extract Market Type + mechanism motif.** Read the profile's
   `## Summary` table. Row 1 (`Market Type`) → palette + Market-Type
   motif. Row 3 (`Mechanism Family`) → mechanism motif.

3. **Derive the Chinese label.** Two lines, per the label convention
   above. Never use `投资者`. Prefer noun-shaped forms already
   present in `design.md` for the market family (e.g. if two `stock`
   coordinators already exist, reuse `股票市场 / 协调器` root and
   distinguish via the top line).

4. **Generate the image.** Use the available image-generation
   capability with this prompt shape (adapt the bracketed slots).
   The prompt is explicitly **headless** — participant icons have
   robot heads; coordinator icons do NOT.

   ```text
   Create a 512x512 PNG flat vector infographic icon for a market
   coordinator mechanism. Composition: large centered circular badge
   with a soft two-color gradient (<palette>), pure white outside
   the circle (never transparent). ABSOLUTELY NO robot, humanoid,
   face, eyes, antenna, helmet, or any character element — this is
   NOT an agent avatar, this is a mechanism diagram.

   Upper 55-65% of the badge: a LARGE centered PRIMARY symbol that
   depicts the Market-Type motif — <market-type-motif-detailed>.
   Rendered as flat vector diagram in dark navy #1E293B outlines
   with <palette> fill accents. This is the icon's hero element.

   Lower 20-25% of the badge (above the label pill): a SMALLER
   centered SECONDARY symbol depicting the mechanism motif —
   <mechanism-motif-detailed>. Same flat vector style, subordinate
   in size to the primary symbol. A subtle thin horizontal divider
   may separate the two symbols.

   Bottom 15-20%: rounded white Chinese label pill with EXACTLY this
   two-line label: line 1 "<top-line-label>", line 2 "<bottom-line-label>".
   This is the ONLY text in the image.

   Style: flat, clean, geometric, thumbnail-readable at 128x128.
   NO photorealism, NO 3D, NO robot, NO face, NO character, NO
   full-body illustration, NO complex background, NO English text
   inside the artwork, NO watermark, NO participant "投资者" noun,
   NO sticker outline halo around the badge, NO transparent or
   checkerboard background.
   ```

   If image generation is unavailable, stop and record a blocking
   note. The profile MUST NOT claim an icon path until the PNG
   exists.

5. **Save and verify.** Save the PNG at the required
   `agent_images/icons/market/` path. Verify:
   - The file exists and is non-empty (typically 150 KB – 2 MB).
   - The image is square, preferably 512×512.
   - The icon visually contains: circular badge on pure white
     background, a LARGE centered Market-Type primary symbol,
     a SMALLER centered mechanism secondary symbol below it,
     and a readable two-line Chinese label pill using
     `协调器 / 场 / 系统` (never `投资者`).
   - **The icon contains NO robot head, NO face, NO antenna, NO
     humanoid, NO character of any kind.** This is the top failure
     mode: image generators default to putting characters into
     "agent" icons. Any character element = automatic reject.
   - The filename is exactly `{market-type}-{stem}.png` under
     `icons/market/`.
   - **Do a full visual read of every icon**, not just a size check.
     Per project memory, icon compliance CANNOT be judged by file
     size alone; failing icons (robot head sneaking in, halo sticker,
     transparent background) frequently produce 600 KB – 1 MB files
     that look fine numerically.
   - If any icon fails the visual read, regenerate with stricter
     anti-failure language emphasised (e.g. "ABSOLUTELY NO robot,
     NO face, NO character — this is a MECHANISM DIAGRAM ONLY, like
     a textbook infographic; NO sticker outline halo; pure white
     background").
   - Batch generate ≤ 4 icons in parallel and verify each batch
     visually before starting the next; retry failures immediately.

6. **Patch the profile.** In `## Design Provenance and Versioning`
   (§4.11 in `market-design-skill.md`), add or update exactly one
   table row. If a stale `Icon` row exists, replace it:

   ```markdown
   | Icon | ![](../agent_images/icons/market/{market-type}-{stem}.png) |
   ```

   Also verify the `Market Type` row in §4.11 matches Row 1 of §4.2
   Summary — Market Type consistency across profile + icon path is
   a validation gate.

7. **Patch the image mapping.** In
   `examples/AGENT_POOL/agent_images/design.md`, ensure there is a
   dedicated section `## Mapping: market/ coordinators → icons/market/`
   (create it once, below the existing `finance/ & opinion/` mapping
   section). Add or update one row per market profile with columns:

   - `#`
   - `Market Type` (canonical slug)
   - `Profile` (e.g. `market/stock-standard-price-impact.md`)
   - `Icon` (e.g. `market/stock-standard-price-impact.png`)
   - `Display Name` (Chinese label, two-line collapsed to one with `/`)
   - `Match Reason` (short — Market-Type motif + mechanism motif)

8. **Record provenance.** Bump the profile's `Version` field.

## Validation Checklist

Run these checks three consecutive times during coordinator-audit
closeout:

- [ ] Profile `.md` exists at
      `examples/AGENT_POOL/market/{market-type}-{stem}.md` with a
      canonical Market Type slug
- [ ] Icon PNG exists at
      `examples/AGENT_POOL/agent_images/icons/market/{market-type}-{stem}.png`
- [ ] PNG passed the full **visual read** (not just size check)
- [ ] Icon visually shows: circular badge on pure white background,
      a LARGE centered Market-Type primary symbol occupying the upper
      55–65% of the badge, a SMALLER centered mechanism secondary
      symbol below it, and a two-line Chinese label pill using
      `协调器 / 场 / 系统` (never `投资者`)
- [ ] Icon contains **NO robot head, NO face, NO antenna, NO
      humanoid, NO character element** — coordinator icons are
      strictly headless mechanism diagrams
- [ ] Background outside the circular badge is pure white (never
      transparent, never checkerboard, never patterned)
- [ ] Icon palette matches the Market-Type palette from §2 table
- [ ] Profile §4.11 has exactly one `| Icon |` row pointing to the
      correct path
- [ ] Profile §4.11 `Market Type` row matches §4.2 Summary row 1
      AND matches the file-name prefix on disk
- [ ] `agent_images/design.md` has a `## Mapping: market/ coordinators
      → icons/market/` section
- [ ] That section has exactly one row per coordinator profile with
      `Market Type` column populated
- [ ] Reused coordinator profiles are not regenerated when their
      existing icon resolves; they are generated or repaired only
      when the icon is missing, broken, or unmapped
- [ ] No coordinator icon lives under
      `agent_images/icons/{market-type}-{stem}.png` (i.e. outside the
      `market/` subdirectory); any such stale file has been moved

## Status

| Field   | Content                                                                    |
|---------|----------------------------------------------------------------------------|
| Version | 1.1.0                                                                      |
| Created | 2026-07-16                                                                 |
| Updated | 2026-07-16 (v1.1.0: switched to headless dual-motif composition; coordinators are mechanism diagrams, not agent avatars) |
| Status  | canonical                                                                  |
| Sibling | `agent-icon-generation-skill.md` (participant-agent icons)                 |
| Depends | `market-design-skill.md` §2.1 canonical Market Type slugs                  |
