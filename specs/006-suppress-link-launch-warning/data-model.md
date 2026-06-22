# Data Model: Suppress External Link Launch Warnings

## `open_url(url: str) -> None`

Pure helper located in `src/impactite/core.py`.

### Inputs

| Field | Type | Description |
|-------|------|-------------|
| `url` | `str` | External `http://` or `https://` URL to open |

### Outputs / Side Effects

| Name | Type | Description |
|------|------|-------------|
| success | side effect | Default browser opens the URL in a new tab when possible |
| failure | `OpenUrlError` | Raised if the URL cannot be opened |

### Invariants

- Must not write browser-process stdout/stderr to the application's TUI.
- Must preserve the existing `OpenUrlError` contract.
- Must restore stdout/stderr fds even if `webbrowser.open` raises.

## `OpenUrlError`

Exception class used by `open_url` to signal failure. Already exists in `src/impactite/core.py`; no change to its definition.
