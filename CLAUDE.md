# Repo Rules (IMPORTANT)

## Git hygiene
- NEVER commit temporary, debug, scratch, or test artifacts.
- Only commit production project files required to run the app.
- Before committing, always run `git status` and ensure only relevant source/config files are staged.

## Forbidden files
Do not create or commit:
- *_test*, *test_report*, *debug*, *scratch*, *dump*, *export*
- logs, tmp, cache folders
- any files outside the project structure that are not part of the deliverable

## Where to put scratch output
If you need to create temporary files, put them only into:
- `tmp/` or `.cache/` (both ignored by git)

## Commit discipline
- Prefer small commits focused on the actual fix.
- If generated files appear in git status, unstage them and delete/move them into tmp/.
