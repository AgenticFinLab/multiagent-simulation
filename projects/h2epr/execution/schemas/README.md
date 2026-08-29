# Rule-execution schemas

These project-local schemas define the two reviewed inputs that precede an
H2EPR full-roster Rule run:

| Schema | Responsibility |
|---|---|
| `policy-realization-v0.1.schema.json` | Participant decision, private-state, lifecycle, and selected Scenario-policy implementations with explicit configuration pointers |
| `executable-scenario-package-v0.1.schema.json` | Exact semantic lineage, versioned actor/carrier and component binding, runtime-bundle contract, repeated run plan, output custody, and claim boundary |

The schemas reject unknown fields and constrain the stable structural surface.
They do not infer semantic coverage. Executable admission must also load the
exact accepted Scenario Configuration, roster, mapping, Scenario release, and
Policy Realization, including the configuration-admission receipt and accepted
mapping manifest, then prove set equality for actors, capabilities,
population units, observations, private state, fixed parameter pointers,
commitments, intents, revisit triggers, structural selections, exogenous
inputs, selected policies, lifecycles, and implementation IDs. Successful
schema validation alone never authorizes a run.

The run profile carries one seed and requires two independent materializations
of the same inputs. Its output contract compares the materialized bundle,
trace, tick and run seals, replay receipt, and generated EPG, and also checks
replay-state equality and trace-to-graph closure.

These files are not additions to the Contracts V1 serialized schema catalog.
They are H2EPR execution profiles whose lineage begins at an accepted Scenario
Configuration rather than the earlier draft/prefix construction protocol.
