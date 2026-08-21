# H2EPR-0288 research roster

- Version: `0.1`
- Status: accepted research scope
- Accepted: 21 August 2026
- Event: Panic of 1907, acute New York phase

This roster defines the participants and processes that must be accounted for
before the first consolidated event mapping. It is a research roster, not an
executable participant list: some rows will produce Agent Definitions, some
will produce population models, and others remain scenario-owned.

## Research boundary

H2EPR-0288 asks:

> How did institution-specific decisions and population responses transmit
> distress from the Knickerbocker run through its credit, clearing, and support
> channels into the subsequent New York trust-company and call-money crisis,
> and how did private and collective mechanisms alter immediate liquidity
> outcomes?

The selected horizon runs from emerging Knickerbocker pressure and National
Bank of Commerce accommodation on or around 18 October through the collective
response visible by 26 October 1907. The exact runtime start, clock, and event
schedule remain scenario-design questions.

The failed United Copper corner and the initial affiliated-bank distress are
starting context. National diffusion, international gold flows, recovery, and
later institutional reform are outside v0.1.

## Roster

| Participant or process | v0.1 disposition | Causal responsibility or boundary | Current state |
|---|---|---|---|
| Knickerbocker Trust Company | Agent | institutional assessment, authorization, support-seeking, communication, and adaptation | Definition `0.2.1` accepted; reference binding available |
| New York Clearing House Association | Agent | case classification, review, authority, scoped disposition, and communication | Definition `0.2.1` accepted; reference binding available |
| National Bank of Commerce in New York | Agent | credit, request intermediation, clearing relationship, notice, and communication choices | Definition `0.1.0` accepted; consolidated mapping deferred |
| Knickerbocker depositors | representation gate | withdrawal, waiting, access, and response to information; decide between cohort Agent, population model, or scenario demand process | first production batch |
| J. P. Morgan and private-financier coordination | Agent | examination commissioning, private-aid decisions, coordination, and money-pool formation | focused research must settle the individual-versus-coordination representation before Definition |
| Trust Company of America | Agent | institution-specific response, support-seeking, collateral, communication, and operational choices | focused research and Definition required |
| Lincoln Trust Company | Agent | institution-specific response and support path; retain separately unless evidence supports aggregation | focused research and Definition required |
| trust-company presidents' committee | representation gate | formation, review, contribution, and allocation choices | use an Agent only if these choices are not fixed by an institutional protocol |
| depositors at later trust companies | representation gate | heterogeneous contagion and withdrawal pressure | decide institution-specific cohorts versus a bounded aggregate model |
| NYCH member banks and large correspondent banks | representation gate | member-owned resources, commitments, certificate demand, and possible disagreement | begin as a reviewed cohort; promote named Agents only when needed by the question |
| brokers, call-money lenders, and borrowers | representation gate | collective market liquidity, collateralized lending, and liquidation behavior | population/cohort model unless autonomous named choices are required |
| NYSE venue and market operation | scenario or institutional process | matching, loan-post, collateral, price, and venue mechanics | a governance interface requires a separate roster revision |
| clearing, settlement, message transport, notice delivery, and resource adjudication | scenario process | timing, routing, legal and physical effects, and result production | owned by the scenario/environment |
| U.S. Treasury public deposits | explicit exogenous resource input | changes available resources without claiming to explain the public decision | not an Agent in v0.1 |
| Charles T. Barney, Knickerbocker directors, and officers | aggregated within the Knickerbocker representation | internal authorization and leadership are represented through the institutional interface | split only if distinct information or interacting choices become causally necessary |
| Heinze, Morse, Thomas, United Copper, and affiliated-bank distress | initial history | establishes the acute-phase starting state | not endogenous in v0.1 |
| interior banks, national cash demand, European money centers, gold inflows, Congress, and later reform bodies | outside v0.1 | wider transmission, recovery, or institutional aftermath | requires a new event question and roster version |

A representation gate is a required modeling decision, not a placeholder
Agent. Its batch closes with either an accepted Agent Definition, an accepted
population/cohort interface, or an explicit scenario disposition.

## Production order

The two-role Knickerbocker–NYCH work is the completed reference pilot. National
Bank of Commerce is the third accepted Definition and joins the event only at
the consolidated mapping stage.

Roster production proceeds in causal batches:

1. resolve the Knickerbocker depositor representation;
2. research Morgan/private coordination, Trust Company of America, and Lincoln
   Trust Company, splitting the batch if evidence review requires it;
3. resolve the trust-company committee, later depositor, member-bank, and
   call-money representation gates, then write Definitions only for the roles
   admitted as Agents.

The order may be shortened or split for reviewability. It must not be expanded
with a new role merely because that participant is historically prominent.

## Definition release gate

`Roster Definition release v0.1` is ready when:

- every roster row has a reviewed disposition;
- every admitted Agent has an accepted, event-bound Definition;
- every population/cohort has an accepted behavioral interface or an explicit
  scenario externalization;
- each accepted product passes the lightweight interface preflight against the
  event [semantic skeleton](../../scenarios/panic_1907/semantic-skeleton.md);
- shared evidence conflicts and participant-time boundaries are visible; and
- a release manifest pins the roster, Definition, evidence, and skeleton
  identities.

The release does not itself authorize implementation or simulation. It is the
entry point for one consolidated Definition-to-implementation mapping and
carrier review.

## Change policy

Roster v0.1 is frozen in the practical sense: batches may refine evidence and
Definitions, but they may not silently change the event question, horizon,
causal owner, or disposition of another row. Such a change requires an owner
decision and a new roster version. Git retains accepted history; working
alternatives remain under the ignored local research area.
