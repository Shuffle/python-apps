# Repository Guidelines

## Project Structure & Module Organization
This repository hosts Shuffle app implementations. Each app lives in a top-level folder named after the integration (e.g., `aws-ec2/`), and each release is versioned under a subfolder like `1.0.0/`. A typical app version contains:

- `src/app.py`: the Shuffle SDK entry point.
- `api.yaml`: OpenAPI definition used by Shuffle.
- `requirements.txt`: Python dependencies for the app.
- `Dockerfile`: container build instructions for the app.
- `README.md`: app-specific usage and action documentation.
- Optional assets such as screenshots (`*.png`).

In `api.yaml`, prefer an `authentication` block for shared credentials (URL, tokens, keys). Actions should only include auth parameters when they truly differ per call.

## Build, Test, and Development Commands
Apps are built and run container-first via the Shuffle SDK image. From an app version directory:

- `docker build -t shuffle-<app>:<version> .`: build the app image.
- `docker run --rm shuffle-<app>:<version>`: run the app container locally.

For quick iteration on code, you can also run the Python entrypoint in a virtualenv:

- `pip install -r requirements.txt`
- `python src/app.py --log-level DEBUG`

## Coding Style & Naming Conventions
Use 4-space indentation and standard Python style. Keep functions `snake_case`, classes `CamelCase`, and constants `UPPER_SNAKE_CASE`. Match existing patterns in `src/app.py` and keep action names aligned with `api.yaml`.

## Creating New Shuffle Apps (Agent Workflow)
Use an existing app as a template (e.g., `http/1.4.0/` or `aws-ec2/1.0.0/`) and follow the same folder layout. A minimal, working app version should include:

- `api.yaml`: action definitions, parameters, and examples.
- `src/app.py`: class extending the Shuffle SDK (`shuffle_sdk.AppBase`).
- `requirements.txt`: third-party dependencies.
- `Dockerfile`: built on `frikky/shuffle:app_sdk`.

When adding actions, ensure the `api.yaml` action name matches the method name in `src/app.py` and parameter names align exactly. Keep input parsing defensive (strings vs JSON), and return JSON-serializable results. For HTTP integrations, centralize auth and base URL handling and add a TLS `verify` option. If a service requires special payloads (e.g., ADF for Jira), accept JSON strings and pass through unchanged. Keep `api.yaml` examples realistic because they show up in the Shuffle UI.

## Authentication & App Configuration
Most apps declare credentials in `api.yaml` under `authentication:` so Shuffle injects them automatically. In code, read those values as normal action arguments (Shuffle passes them into each action). Prefer a single auth helper in `src/app.py` (e.g., `_auth()` for tokens, `_build_api_base()` for base URLs) and reuse it across actions. If an integration supports multiple auth modes (token vs password), accept both and choose the provided one.

Prefer small, focused actions (create, update, list, search) and document auth requirements and examples in the app `README.md`.

## Manual Python App Notes (From Shuffle Docs)
- **SDK image choices:** Shuffle provides Alpine (slim), Kali (security tooling), and Blackarch (kitchen‑sink). This repo’s Dockerfiles typically use `frikky/shuffle:app_sdk` (Alpine‑based) unless a toolset requires otherwise.
- **Directory layout:** `api.yaml`, `Dockerfile`, `requirements.txt`, `README.md`, and `src/app.py` are expected in each app version. Complex apps can add additional modules under `src/` and import them from `app.py`.
- **Actions & wiring:** Every action in `api.yaml` must map to a method in `src/app.py` with the same name and argument list. Authentication parameters are passed into each action automatically when declared under `authentication:`.
- **Utility helpers:** In `AppBase`, you can use `self.get_file`, `self.set_files`, `self.update_file`, and cache helpers `self.get_cache`, `self.set_cache`, `self.delete_cache` for file and key/value workflows.
- **Prototyping:** Build and test your Python logic locally first, then wire it into `src/app.py`. Keep return values JSON‑serializable so Shuffle can consume them.
- **Upload & hotload:** After a prototype works, upload it to Shuffle (cloud) or hotload locally (on‑prem) by rebuilding the app image. Local Docker rebuilds are faster for iteration.

## Testing, Hotloading, and CI/CD
- **Cloud upload test:** Use the Upload App API to add the app to your org, then run a workflow to validate actions.
- **Local hotload (on‑prem):** Place the app folder in `shuffle-apps/`, set `SHUFFLE_APP_HOTLOAD_FOLDER=./shuffle-apps`, then use the hot reload button in the UI. Allow ~20 seconds for the reload to complete.
- **Update workflow deps:** If you update an existing app version, remove and re‑add the app in any workflows that reference it.
- **Fast local iteration:** After the first upload, rebuild locally: `docker images | grep <appname>` then `docker build . -t <imagename>`.
- **CI/CD pattern:** Create a test workflow, upload a test app version, run the workflow via API, and validate `workflowexecution.workflow.validation.valid` before promoting.

## Publishing Apps
- **OpenAPI apps:** Upload to your instance, then use the `/apps` page to publish so it appears on `shuffler.io`.
- **Python apps:** Fork `https://github.com/frikky/shuffle-apps`, add your app, and open a pull request to upstream.

## Testing Guidelines
There is no repository-wide test suite. If you add tests for a specific app, keep them alongside the app version (e.g., `aws-ec2/1.0.0/tests/`) and document how to run them in that app’s `README.md`.

## Commit & Pull Request Guidelines
Commit messages are short and descriptive, sometimes using a prefix like `fix:`. Follow that style and keep commits scoped to a single app/version when possible.

For pull requests, include:

- A clear description of the change and impacted app/version path.
- Updated `README.md` or `api.yaml` when behavior changes.
- Screenshots/assets if user-facing output or UI-related docs are affected.

## Security & Configuration Tips
Many apps require API keys or credentials. Do not commit secrets; use environment variables or Shuffle configuration fields instead, and document required inputs in the app’s `README.md`.
