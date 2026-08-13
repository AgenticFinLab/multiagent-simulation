# Reference and suffix leakage threat model

Protected information includes the held-out real-process graph, post-`t0`
draft actions and outcomes, suffix-specific causal chains, and derived labels
that reveal those facts.

Leakage paths include prompts, observations, memory, retrieval indexes, cached
tool output, world state, policies distilled from the target suffix, scenario
configuration, compiler heuristics tuned to the answer, evaluator imports, and
human builders who later relabel contaminated artifacts as strict.

Controls are defense in depth:

- deny-by-default construction allowlists;
- typed prefix projection with source hash, cutoff, included pointers,
  suffix-absence receipt, producer identity, and consumer boundary;
- irreversible construction ancestry and contamination labels;
- closed runtime schemas that have no evaluation-reference field;
- test and import boundaries separating runtime/compiler from evaluation;
- trace provenance for every generated graph element; and
- clean-build strict reruns after target-suffix exposure.

Hashing, parsing, copying, or otherwise inspecting a held-out event reference
is itself outside construction/runtime scope. Offline evaluation may access it
only after the run artifacts are sealed. A demo contaminated by complete-draft
access cannot support strict continuation-fidelity claims.

