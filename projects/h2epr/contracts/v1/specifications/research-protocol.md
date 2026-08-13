# Research protocol

The first experiment family is retrospective event-process continuation.
Before a run, a declared time origin `t0` partitions real information into a
construction prefix and a held-out continuation.

Two development modes must remain distinguishable:

- **Architecture demo:** a builder may inspect a complete draft to design or
  close engineering interfaces. Every target-specific descendant is marked
  `full_draft_exposed` and `architecture_demo_only`.
- **Strict continuation:** a clean builder receives only the approved event
  specification fields, frozen-evidence references allowed by policy, and a
  typed projection whose claims end at the cutoff. The build is
  `clean_prefix_only` and may become `strict_eligible` only after review.

A builder that has seen the target suffix cannot regain strict eligibility by
relabeling an artifact or rebuilding descendants. A clean-build strict rerun
is required after an engineering demo before continuation-fidelity evidence is
scientifically admissible.

Runtime agents produce observations, decisions, intentions, messages, and
actions. The environment produces dispositions, exogenous releases, local
outcomes, and authoritative state versions. The compiler never asks an agent
to output a complete event graph directly.

