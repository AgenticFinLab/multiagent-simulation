# Design rationale

## Why event assets are separate from MASim

MASim supplies reusable simulation infrastructure: agent/player lifecycles,
communication, event-process values, transport, authoritative reduction,
trace, and seals. H2EPR adds a benchmark contract with strict source exposure,
complete participant accounting, backend-neutral semantics, explicit backend
bindings, replay, trace-derived graphs, and compact publication evidence.

Keeping H2EPR in `projects/h2epr/` lets benchmark rules evolve without
silently changing MASim for other collaborators. H2EPR records the exact MASim
source bytes used by each run, so reuse remains auditable.

## Why Agent Definitions do not fix behavior

Traditional scenario definitions often combine persona, numeric parameters,
prompt content, policy rules, and runtime settings. That is convenient for one
simulation but makes backend comparison ambiguous: changing from Rule to LLM
also changes the participant being represented.

H2EPR Agent Definitions and Population Models instead own stable decision-unit
semantics: identity, available information, authority, admissible choices,
state, uncertainty, and limits. Exact Rule rows, model prompts, decoding, and
constraint policies live in backend configuration and realization. The same
participant surface can therefore support multiple decision mechanisms.

## Why the Draft EPG is an input, not an answer key

The current construction protocol fully exposes the Draft EPG. It supplies a
bounded event outline, participant occurrences, actions, and temporal anchors
for building a runnable package. Treating it as an answer key would confuse
construction support with held-out evaluation.

Generated output can be read against the Draft to find implementation or
modeling discrepancies, provided that exposure is disclosed. Historical fit
and benchmark performance require an independently accepted target and clean
protocol.

## Why Rule is retained

Rule is a deterministic participant baseline and a systems oracle. It tests
whether the event package, interface, environment, transport, trace, replay,
graph, and publisher can close without model-service variability. It also
provides a controlled comparator for future LLM and RuleLLM backends.

Rule rows are event-local data. The runner and backend implementation contain
no event identities or domain vocabulary. Success on several events is useful
reuse evidence only when the same common implementation and contract are
independently verified.

## Why the environment is authoritative

Participants express intents and messages. They do not declare that a request
was delivered, authorized, feasible, successful, or state-changing. Central
environment admission preserves one state authority, makes conflicting writes
observable, and gives Rule and model backends the same consequence semantics.

All decisions at a coordinate see one sealed prestate. Distinct concurrent
writes to the same field are rejected without partial effects. Idempotent
same-value writes are safe and ordered by semantic content rather than opaque
runtime IDs.

## Why the Generated EPG is trace-derived

Building the graph from a hand-authored summary would create another source of
truth. H2EPR instead compiles it from the sealed trace and retains every trace
record as a graph node. Navigation nodes and edges improve traversal while
exact coverage preserves provenance.

The graph is therefore a view of simulated evidence. It does not independently
validate the simulation or history.

## Why releases are compact

Raw traces and graphs can be large and are naturally attempt-local. The
tracked release pins their identities, counts, custody locator, and independent
verification while keeping the repository readable. Reproduction and
publication can reject missing or changed custody through hashes.

Git retains replaced tracked assets. Local project memory retains process
history. The current repository exposes one accepted version, which reduces
navigation ambiguity without destroying recoverability.

## Why synthetic fixtures precede real events

Tests that depend only on published events can pass vacuously when the
registry is empty or can accidentally canonize event-specific vocabulary.
Two temporary synthetic packages with different actors, intents, states, and
messages exercise the complete common contract independently of a historical
case.

A later blind real-event trial tests whether the human documentation,
templates, Skills, schemas, and failure routes are usable with imperfect data.
Reusable findings return to the framework; event-specific choices stay in the
event package.
