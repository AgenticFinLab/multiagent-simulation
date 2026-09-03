# Event package template

Create `events/<event>/package/` only after the Source Profile,
roster/actor map, semantic parents, participant interfaces, Scenario
Definition and Mechanism, and exhaustive shared configuration provenance are
admitted.

The assembly publishes three identities:

- `semantic_assembly_sha256` excludes backend status and releases;
- `backend_catalog_sha256` binds backend availability to that semantic core;
- `assembly_sha256` seals the complete assembly record.

Compile the core first. It contains Source Profile, semantic index, portable
participants and scenario, participant semantic index, and shared
configuration. Its `package_sha256` excludes both the backend catalog hash and
all binding rows. Attach an implemented backend in a second operation, through
its registered factory. Attachment adds realization/configuration bytes and a
binding, updates `manifest_sha256`, and must leave `package_sha256` unchanged.

The package role surface is:

| File | Responsibility |
|---|---|
| `manifest.json` | Core identity, separate catalog identity, attachment status, exposure, and claim boundary |
| `source-profile.json` | Exact three-file construction allow-list and prohibitions |
| `semantic-assets.json` | Semantic assembly and released-parent identities only |
| `participants.json` | Complete Draft roster, dispositions, and active actors |
| `participant-interface.json` | Shared observation, intent, lifecycle, and capability surface |
| `participant-semantic-index.json` | Actor to human semantic parent, hash, and Draft anchors |
| `scenario.json` | Logical timeline, mechanism, state, routes, and termination |
| `shared-configuration.json` | Backend-neutral selections and value provenance |
| `shared-configuration-provenance.json` | Exact coverage or typed exemption for every top-level shared setting |
| `backend-bindings/<backend>.json` | One attached backend's package parent, configuration, provenance coverage, implementation, and failure routing |
| `backend-bindings/<backend>-realization.json` | Exact reviewed implementation projection copied from its release |
| `backend-bindings/<backend>-configuration.json` | Exact backend decision settings copied from their admitted release |
| `backend-bindings/<backend>-configuration-provenance.json` | Exact coverage or typed exemption for every top-level backend setting |
| `README.md` / `SHA256SUMS` | Reader boundary and exact inventory |

Reject an unsafe path, parent drift, unregistered implementation, backend
substitution, attachment-induced core-hash change, actor/action mismatch, or
uncovered configuration value. `llm` and `rulellm` remain unattached until a
real implementation and its provenance/failure contracts exist.
