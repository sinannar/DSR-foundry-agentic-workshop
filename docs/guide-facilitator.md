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

The full workshop runs 3-4 hours. Adjust to your audience and the time available.

| Module | Focus | Notes |
|--------|-------|-------|
| 00 Setup | Environment, sign-in, health check | Block until everyone passes `health-check.py`. |
| 01-03 | Portal walkthrough, Toolkit, prompt-based agents | Fast, confidence-building modules. |
| 04-05 | Agent tools, evaluations, MCP tools | Core content; protect this time. |
| 06-07 | Foundry Toolboxes, Foundry IQ | Demand-driven; trim depth if behind. |
| 08-09 | Agent Framework, hosted agents | Core content; protect this time. |
| 10-11 | Agent ops, Agent ID, publishing | Demo only if attendees are on `foundry-user`. |

## Per-lab facilitation

- Frame each lab with the problem it solves before attendees open the starter.
- Let attendees attempt the starter; reveal the `solution/` only after a genuine attempt.
- Call out that each lab is independently runnable, so a blocked attendee can move on and
  return later.

## Common issues

| Issue | Cause | Resolution |
|-------|-------|------------|
| Health check fails at setup | Sign-in or `.env` value missing. | Re-run `az login`; confirm assignment values. |
| Attendee cannot deploy a model | Expected on the `foundry-user` role. | Point them to the pre-deployed models. |
| Lab 08 publishing blocked | Needs Foundry Project Manager. | Have the organizer raise the role, or demo it. |
| Attendee fell behind | Long-running step or distraction. | Each lab is self-contained — resume at the current module. |

## Fallback

Keep one demo project as a fallback for an attendee whose assignment is blocked, and let a
proctor pair them on it while you continue delivery.
