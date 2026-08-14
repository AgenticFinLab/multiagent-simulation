# ADR-0001: G1 project-local construction incubator

- Status: accepted for the bounded G1 candidate
- Scope: Source Adapter and Construction IR only
- Reconsideration: mandatory before G3 integration

## Context

G1 needs a Reference-blind construction implementation without prematurely
making event-project policy part of the generic MASim package. It must also
avoid presenting an incomplete implementation as a runnable scenario. The
stable V1 schemas already live under `contracts/v1/` and remain their single
owner.

## Decision

Incubate G1 under `projects/h2epr/src/h2epr/construction/`. Tests expose that
source root explicitly; root `setup.py` package discovery and distribution are
unchanged. The project package may publicly expose the bounded construction
responsibilities, but its internal modules and private class split remain
adjustable.

Production G1 code imports only the Python standard library. It receives
approved input roots, explicit SourceDescriptors and any contract paths from
callers. It neither discovers repository locations nor imports Phase-0 test
support. Accepted schemas are not copied under `src/`.

The internal snapshot format starts at `h2epr.construction_ir.v1`. Any change
to snapshot meaning or shape requires an explicit successor snapshot version,
migration documentation and old/new deterministic tests. Refactoring or
relocating implementation without changing that meaning is compatible.

## Consequences and limits

This placement makes current ownership clear and keeps G1 independent of
MASim's broad runtime import graph. It does not decide installed packaging,
participant/runtime ownership, scenario/configuration placement, or generic
framework extraction. It supplies no runtime, simulation, compiler, evaluator,
or scientific result.

Before G3, a reviewed successor decision must use G1/G2 evidence to retain,
package, relocate or split the incubator. Compatible future movement is
permitted and does not weaken V1 contracts. Cross-domain evidence through the
later 0616 gate remains necessary before any shared-core extraction claim.
