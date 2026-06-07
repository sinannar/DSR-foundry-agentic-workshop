# Step 04: Add tools and optional evaluations

## Objectives

- Prepare the prompt-based agent for tool integration.
- Optionally run simple evaluations to measure agent quality.

## Steps

1. Open the `retail-assistant` agent created in Step 03.
1. Review the agent instructions and refine them so the agent is ready to call
   tools, for example by stating when it should look up product or policy
   information rather than answer from memory.
1. Identify the tool surfaces available on the Build tab that you will use in
   the next steps (MCP tools in Step 05, knowledge in Step 07).
1. (Optional) Run a simple evaluation:
   1. Prepare a small set of representative prompts and expected behaviors.
   1. Run the evaluation from the toolkit or portal evaluation surface.
   1. Review the scores and note where the agent is weak.
1. Capture any instruction changes that improved evaluation results.

## Validation

- The agent instructions describe when the agent should use tools or knowledge.
- (Optional) An evaluation run completes and produces reviewable scores.

## Troubleshooting

- If evaluation is unavailable, skip the optional section; it is not required
  for the rest of the lab.
- If scores are unexpectedly low, confirm the evaluation prompts match the
  agent's intended scope.
- If instruction edits are not reflected, confirm the agent was saved before
  re-running.
