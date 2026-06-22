# Contract: Core External Link Opening

## Function `open_url`

**Location**: `src/impactite/core.py`

**Signature**:

```python
def open_url(url: str) -> None:
    """Открыть URL в системном браузере/обработчике.

    Raises:
        OpenUrlError: если URL не удалось открыть.
    """
```

### Behavior

1. The function calls the system browser handler (`webbrowser.open`) for the given URL.
2. While the browser is being launched, any output written to the application's standard output or standard error file descriptors by the browser process is discarded.
3. After the launch attempt, the original file descriptors are restored.
4. If the browser handler cannot open the URL, `OpenUrlError` is raised.
5. If the browser handler raises any exception, it is wrapped in `OpenUrlError` and re-raised.

### Error Handling

- Callers must catch `OpenUrlError` and surface a localized error message via the UI notification system.
- The function does not interact with Textual widgets or the `App` instance.

### Platform Notes

- The suppression must work on Linux/Unix and Windows file-descriptor models.
- No platform-specific commands (e.g., `xdg-open`) are introduced.
