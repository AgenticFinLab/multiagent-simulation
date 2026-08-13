# Entity and participant contract

Construction produces an `EntityRegistry`, a reviewed participant roster, and
one `ParticipantArtifact` for each autonomous or aggregated actor. Every real
draft participant is classified as one of:

- autonomous participant agent;
- institutional or environment agent;
- aggregate population agent; or
- exogenous event/environmental process.

Selection is explicit and reviewable. High-impact actors with distinct
authority, information, goals, or action repertoires should remain separate.
Low-impact, homogeneous, or population-scale actors may be aggregated when the
aggregation rule, retained heterogeneity, and lost distinctions are recorded.

A participant artifact separates identity/persona from behavior, memory, and
mutable resource state. It may encode goals, preferences, authority, resources,
initial information, skills, action repertoire, constraints, risk posture,
communication dependencies, response rules, and uncertainty. It does not copy
post-`t0` real actions into a policy.

The intended MASim mapping is: participant identity and institutional role to
Persona; policy and stateful decision behavior to Player; assembly and source
policy to configuration; observation boundaries to perceive inputs; action
repertoire to closed Action schemas; and partner/route policy to topology and
Message transport.

