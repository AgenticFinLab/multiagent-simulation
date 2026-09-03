# Benchmark-simulation schemas

This directory is the single released schema surface for the current H2EPR
workflow. [`catalog.json`](catalog.json) lists every admitted schema. Protocol
versions remain explicit inside each schema and artifact; the repository does
not publish parallel development generations beside the current contract.

JSON Schema checks local structure. Runtime admission also verifies identities,
hashes, source allow-lists, cross-file actor closure, routes, replay, and graph
provenance. A breaking contract change is reviewed outside this current
surface and replaces the catalog only after every dependent asset and test
passes.

The experiment schemas describe read-only plan admission. They do not imply a
matrix executor or an implemented model backend.
