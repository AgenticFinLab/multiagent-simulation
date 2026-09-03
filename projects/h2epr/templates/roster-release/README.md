# Roster release template

A roster release contains:

- `README.md` with the representation boundary;
- `roster.json` containing every Draft participant and source appearance;
- `actor-map.json` assigning each participant to an active actor, context,
  world state, process, outside-window record, or source defect;
- `manifest.json` pinning the roster and actor-map artifacts; and
- `SHA256SUMS`.

Every Draft participant appears exactly once in the source roster. Every
active actor has one representation kind and one semantic parent. Exact
observed names, participant types, roles, appearance anchors, participant
count, occurrence count, and numeric ID gaps must be derived from the Draft.
Many-to-one aggregation is explicit, and no runtime actor exists solely in
code. The separate participant-interface release pins human semantic-parent
paths and hashes through its machine semantic index.
