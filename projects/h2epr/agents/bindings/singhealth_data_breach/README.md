# SingHealth Data Breach bindings

This directory contains the event-qualified semantic mapping and bounded
carrier binding for H2EPR-0616. The two releases serve different purposes:

- [`consolidated/`](consolidated/) maps all nine released participant products
  to capability-qualified semantic identities and Contracts V1 carrier rules;
  it contains no participant or environment implementation.
- [`scm-technical-operations-gcio-v0.1/`](scm-technical-operations-gcio-v0.1/)
  binds one selected technical--operations--GCIO lineage to exact observation,
  action, message, route, authority, lifecycle, and verification-result
  carriers.

The bounded binding does not extend to the remaining ten actor instances or
fifty semantic intent placements. The accepted Scenario Configuration remains
non-executable, and no full-event simulation or historical-validity claim is
implied.
