## About this Project

Building a pipeline to AI generate slop novels with as little human input as possible.

## Project Notes

When working with this codebase, prioritize readability over cleverness.
State assumptions, never guess silently.
Minimum code, nothing speculative.
Surgical changes. Don't refactor adjacent code.
Define success, loop until verified.
Do not remove my comments. They are there for documentation purposes.

## Key Directories

- `src/` — main Python source; `main.py` is the entry point, `NovelGen/` handles generation logic, `utils/` has helpers like template rendering
- `Blueprints/` — per-novel YAML configs (characters, locations, chapters, continuity, etc.)
- `Templates/` — prompt templates (`.txt`) rendered at runtime with blueprint data
- `outputs/` — generated chapter text files
- `manuscripts/` — assembled full manuscripts