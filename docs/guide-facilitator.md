# Facilitator Guide

This guide covers how to deliver the workshop: pacing, per-lab facilitation, and the issues
attendees hit most often. For the condensed flow, see the
[Facilitator Quickstart](./quickstart-facilitator.md).

## Delivery goals

- Keep modules interactive and time-boxed.
- Encourage pair troubleshooting before the solution reveal.
- Keep every attendee productive — pull in a [proctor](./guide-proctor.md) early when
  someone is blocked.

## Prepare

1. Confirm the organizer has provisioned the environment and that
   `azd env get-value AZURE_ATTENDEE_PROJECT_NAMES` lists a project per attendee.
1. Run all labs once on a `foundry-user` test identity. This surfaces the same
   least-privilege constraints attendees experience (for example, no model deployment).
1. Confirm proctors have the attendee assignment list and the [Proctor Guide](./guide-proctor.md).

## Suggested pacing

The full workshop runs 3–4 hours. Work through labs in sequence, time-boxing each module. Block on setup until every attendee passes `python scripts/health-check.py` before moving on; unresolved setup issues compound throughout the session.

Protect time for the core agent-building labs. Treat later optional labs as depth-adds and trim their scope when the session is running behind. If attendees are on the default `foundry-user` role, some labs may not be completable independently; treat those as live demonstrations.

## Lab facilitation

- Frame each lab with the problem it solves before attendees open the starter.
- Let attendees attempt the starter; reveal the `solution/` only after a genuine attempt.
- Remind attendees that each lab is independently runnable, so a blocked attendee can move on and return later.

## Common issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Health check fails at setup | Sign-in or `.env` value missing. | Re-run `az login`; confirm assignment values. |
| Attendee cannot deploy a model | Expected on the `foundry-user` role. | Point them to the pre-deployed models. |
| Attendee cannot perform an action in a lab | The lab may require an elevated Foundry role. | Have the organizer raise the role, or demonstrate it live. |
| Attendee fell behind | Long-running step or distraction. | Each lab is self-contained; resume at the current module. |

## Fallback

Keep one demo project as a fallback for an attendee whose assignment is blocked, and let a
proctor pair them on it while you continue delivery.
