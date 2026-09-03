# Source Profile template

A Source Profile records:

- event ID and stable slug;
- exposure mode and protocol eligibility;
- exactly three allowed logical inputs;
- repository-relative path, size, and SHA-256 for each input;
- prohibited inputs and prohibited discovery behavior;
- dataset limitations and claim exclusions; and
- profile identity and version.

The loader resolves paths directly. It must not list sibling files, search for
fallbacks, or open Reference/evaluation material to prove that those files are
excluded.

The logical-name sequence is exactly `event_spec`, `frozen_evidence`,
`draft_epg`. `discovery_policy`, dataset limitations, all prohibited-input
classes, and all scientific claim exclusions are required. Admission validates
the exposed Draft stage, episode, participant, and action structure in addition
to file identity.
