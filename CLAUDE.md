# Claude Code & GitHub Copilot Instructions

This repository is a standalone Home Assistant custom integration (`custom_components/pettracer`),
distributed via HACS. It is a separate project from Home Assistant core (`home-assistant/core`) —
never copy code between this repo and a hacore checkout; keep them as separate git clones and
separate editor windows.

## Git Commit Guidelines

- **Do NOT amend, squash, or rebase commits that have already been pushed to the PR branch after
  the PR is opened** — reviewers need to follow the commit history, as well as see what changed
  since their last review.

## Pull Requests

- If this repo has a `.github/PULL_REQUEST_TEMPLATE.md`, use it and NEVER REMOVE ANYTHING from it.
- Do not remove checkboxes that are not checked — leave all unchecked checkboxes in place so
  reviewers can see which options were not selected.

## Development

- Target the Python syntax supported by the Home Assistant versions this integration is meant to
  run on (check `manifest.json` and `hacs.json` before relying on newer language features — unlike
  hacore, this repo is not pinned to core's latest minimum Python version).
- No automated test suite exists yet in this repo. When adding tests, follow Home Assistant's own
  testing conventions:
  - Use `pytest`, with `pytest_homeassistant_custom_component` fixtures (the custom-integration
    equivalent of core's internal test fixtures).
  - Ensure all test function parameters have type annotations; prefer concrete types
    (`HomeAssistant`, `MockConfigEntry`, etc.) over `Any`.
  - Prefer `@pytest.mark.usefixtures` over unused fixture arguments.
  - Avoid conditions/branching in tests — split tests or use parametrization instead.
  - Use `pytest.mark.parametrize` with `pytest.param(..., id=...)` instead of duplicating similar
    test bodies.
  - Use Syrupy `.ambr` snapshots instead of exhaustively hand-writing expected test data.
  - Hardcoded `entity_id`s in tests are fine; use a constant if the same one repeats.

## Good practices

- `quality_scale.yaml` in this repo currently targets Bronze. Platinum/Gold-level integrations in
  Home Assistant core are good references for patterns worth adopting as the scale climbs.
- When reviewing entity actions, do not suggest extra defensive checks for input already validated
  by Home Assistant's service/action schemas and entity selection filters. Suggest additional
  guards only when data bypasses those validators or is transformed into a less-safe form.
- When validation guarantees a dict key exists, prefer direct key access (`data["key"]`) over
  `.get("key")` so contract violations are surfaced instead of silently masked.
- Keep comments concise. Prefer one short line stating the non-obvious constraint, or no comment
  at all.
- Do not add comments that just restate the code on the following line(s). Comments should only
  explain why (non-obvious constraints, surprising behavior, workarounds), never what. Never add
  comments that justify a change by referencing what the code looked like before. Comments in
  tests that explain why a call or assertion is made are fine.
- Do not add section or divider comments — they go stale and mislead.
- When catching exceptions, keep try-clauses as small as possible: avoid wrapping large blocks in
  a try-clause, and avoid catching exceptions from functions that aren't expected to raise them.
- Sensitive service actions — those that can change configuration or have security implications —
  should require an admin user, via the `async_register_admin_service` helper.
