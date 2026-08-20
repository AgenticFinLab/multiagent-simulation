# Worked cases and falsification

Worked cases demonstrate the model's logic. Falsification statements give the
model a real possibility of failure. Neither should be written after seeing a
simulation result solely to rationalize it.

## Case portfolio

Choose cases that exercise distinct boundaries. Depending on the participant,
include:

- ordinary operation with sufficient information;
- stress with incomplete or stale information;
- missing authority or unresolved procedure;
- an existing pending request or commitment;
- a new delivered message or result;
- an ineligible, prohibited, or infeasible route;
- partial, delayed, failed, expired, or no-effect result;
- conflict between institutional duties and discretionary goals;
- an edge case or role/authority perturbation.

There is no fixed case count. Coverage should be sufficient to exercise every
major mechanism, persistent state, fallback, and intent family without
creating redundant examples.

## Case format

For each case state:

1. whether it is observed historical, reconstructed, illustrative, or
   counterfactual;
2. event time and exposure status;
3. world conditions relevant to the case;
4. exactly what the participant observes and what remains hidden;
5. prior private state;
6. authority, procedure, resources, and relationships;
7. applicable Decision Commitments and competing mechanisms;
8. institutionally permitted alternatives and precedence;
9. proposed intent, information request, delay, escalation, or abstention;
10. possible environment dispositions and results;
11. expected process pattern;
12. a meaningful perturbation and changed prediction.

Show calculations when the model genuinely contains a quantitative mechanism.
Check arithmetic, inequality directions, units, rounding, and range constraints
independently. A polished numerical example with a sign or threshold error is
more misleading than a clear qualitative case.

## Behavioral prediction classes

State predictions at several levels where appropriate:

- **role prediction:** a participant with different authority should have a
  different intent envelope;
- **information prediction:** masking or delaying a required signal should
  change information seeking, delay, or abstention;
- **state prediction:** a pending or delivered result should alter later
  behavior;
- **institutional prediction:** membership, eligibility, review, or delegation
  should change procedure or available routes;
- **interaction prediction:** messages and results should alter subsequent
  decisions only after delivery;
- **mechanism prediction:** removing a mechanism should change a predeclared
  process pattern;
- **parameter prediction:** changing a bounded parameter should have a stated
  direction or regime effect;
- **forbidden pattern:** future knowledge, actor-name branching, duplicate
  requests, unauthorized actions, or self-realized outcomes should never
  appear.

## Falsification sources

A Definition can be challenged by:

1. **historical evidence** that contradicts its representation, authority,
   information, mechanism, or action set;
2. **implementation conformance evidence** showing that a backend uses hidden
   information, state, or behavior;
3. **process evidence** showing that predeclared event patterns do not match;
4. **counterexample situations** in which the model produces an institutionally
   impossible or insensitive response;
5. **minimality tests** showing that a purportedly mandatory mechanism or field
   has no behavioral or explanatory consequence.

Keep these failure classes separate. A nonconformant backend does not falsify
the behavioral hypothesis; a perfectly conformant backend does not validate
the historical model.

## Perturbation set

Use perturbations such as:

- erase or replace the historical name while preserving semantic properties;
- exchange role or authority profiles;
- remove, delay, stale, coarsen, or contradict an observation;
- inject a future fact and verify that it is rejected;
- alter membership, relationship, authorization, or resource control;
- place a request in pending, delivered, partial, failed, or expired state;
- withdraw a supporting claim;
- substitute a competing mechanism;
- remove a parameter or replace an exact value with an interval;
- split or aggregate the institutional representation.

Predeclare which behavior should change and which should remain invariant.

## Calibration and evaluation language

State how evidence was used:

- construction or representation;
- mechanism selection;
- parameter bounding or calibration;
- worked-case explanation;
- falsification design;
- post-freeze evaluation.

Do not call a case held out if its outcome, process, or source already shaped
the Definition. An exploratory, fully exposed historical reconstruction can
still be valuable, but its evidence status must be stated accurately.

## Adequacy review

- Does every major mechanism appear in at least one case or falsification
  statement?
- Do cases obey the same information and authority boundaries as the prose?
- Are all intent outcomes left to the environment?
- Are quantitative examples correct and evidence-bounded?
- Are observed and counterfactual cases labeled?
- Do perturbations distinguish competing mechanisms?
- Can a failed case identify whether the problem lies in representation,
  evidence, mechanism, scenario, or backend conformance?
- Were predictions stated before using new simulation or evaluation output?
