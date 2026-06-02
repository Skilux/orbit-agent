# Orbit — Task Prompt Library

Short, copy-paste prompts a marketer pastes turn by turn. The system prompts (`planner.md`, `executor.md`) carry all the detail — keep these minimal. Replace `<email>` with the recipient address the demo uses.

---

## Planner — Discover & propose

```
Find me a revenue opportunity this week and propose a win-back campaign.
Dig into the data, surface the cohort worth chasing with a dollar number,
then draft the offer and the email copy. Stop for my approval before anything sends.
```

## Planner — Re-plan / iterate

```
Opens look weak on that cohort. Look at the results and propose a sharper
iteration — adjust the angle or offer where the data says to.
Give me a new brief and wait for my approval.
```

## Executor — Execute the approved campaign

```
Approved. Execute the campaign from the brief on <email>.
Write the properties, fire orbit_winback, then verify it actually sent.
```

## Executor — Monitor / check results

```
Check the results for <email> — did the orbit_winback email send?
Read back the event status and tell me plainly.
```

---

### Optional variants

Planner — narrower goal:
```
Who should we win back, and what should we offer them? Show me the numbers.
```

Executor — re-verify after waiting:
```
Re-check <email>. Has the status changed since last time?
```
