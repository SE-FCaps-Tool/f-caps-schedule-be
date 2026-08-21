# Editable Manual Timeline Design

## Decision

Quick generation is a draft-authoring aid. The final manual timeline list is
the source of truth after a Manager edits preview output.

## Contract

- Quick preview remains formula-based.
- Manual mutation accepts a shared group duration plus explicitly positioned
  timelines and a group count per timeline.
- Manual timelines may have different durations and capacities.
- Gaps between timelines are derived breaks.
- Detail output keeps the common `blocks[].groupSlots[]` shape. Uniform-only
  summary fields are nullable for heterogeneous manual timelines.

## Persistence

Store the normalized manual timeline array as an immutable JSONB snapshot on
the Timeframe revision. Existing scalar columns remain for compatibility and
carry derived representative values where meaningful.

## Validation

- At least one timeline; bounded list size.
- Local wall-clock times only.
- Positive group duration and group count.
- Timeline duration exactly matches group duration multiplied by group count.
- No overlaps; backend sorts and assigns sequence numbers.
