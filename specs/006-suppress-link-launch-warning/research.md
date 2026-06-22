# Research: Suppressing Browser-Launch Console Output

## Decision

Suppress standard output and standard error at the OS file-descriptor level while `webbrowser.open()` runs, then restore both descriptors in a `try/finally` block.

## Rationale

- The warning text (`kf.iconthemes: Icon theme "Breeze" not found.`) is printed by the spawned browser/desktop process, likely to `stderr`, before the original application regains control.
- Python-level `contextlib.redirect_stdout`/`redirect_stderr` only redirect Python-level streams (`sys.stdout`/`sys.stderr`) and do not capture writes from C libraries or spawned sub-processes that inherit raw file descriptors.
- OS-level fd redirection (dup/dup2) captures all writes to fd 1 and fd 2 for the duration of the call and is available on both Unix-like systems and Windows.
- The change stays in `core.py` and keeps `app.py` completely unaware of the suppression.

## Alternatives Considered

| Approach | Why Rejected |
|----------|--------------|
| `contextlib.redirect_stdout`/`redirect_stderr` to `io.StringIO` | Fails to capture C-level or subprocess writes inherited by the browser launcher |
| Replace `webbrowser.open` with `subprocess.run(["xdg-open", url], ...)` | Ties us to Linux/desktop-specific commands; `webbrowser` is cross-platform and already chosen |
| Set `QT_QPA_PLATFORMTHEME` or related env vars | Platform/browser-specific; does not cover other toolkits or future warnings |
| Monkey-patch `webbrowser._browsers` / override the controller | More invasive; fd redirection is simpler and covers all controller backends |
| Replace `new=2` with `autoraise=False` | Has no effect on subprocess output |

## Implementation Notes

- Use `os.dup(1)` and `os.dup(2)` to save current stdout/stderr fds.
- Open `os.devnull` for writing.
- Use `os.dup2(devnull_fd, 1)` and `os.dup2(devnull_fd, 2)` to redirect.
- Wrap `webbrowser.open(...)` in `try/finally` and restore saved fds.
- Close the saved and devnull fds cleanly, guarding against `OSError`.
- Keep the existing `OpenUrlError` contract: raise on exception or when `webbrowser.open` returns `False`.
