# Research: Directory Context Menu

## Unknown: How to detect a right-click on a specific directory node

**Decision**: Override `FileTree._on_mouse_down`, inspect `event.button == 3`, and use `self.hover_line` + `self.get_node_at_line(...)` to find the clicked node.

**Rationale**: Textual 8.2.4 does not expose a built-in context-menu widget, so the application must capture the mouse event inside the tree subclass. `hover_line` is already updated by the built-in mouse-hover logic, so it reliably identifies the node under the pointer at click time. The node is confirmed to be a directory by checking that `node.data` is a `Path` pointing to a directory.

**Alternatives considered**:
- Use `event.style.meta` from a `Click` event — discarded because right-clicks may not always produce a `Click` event and `hover_line` is simpler.
- Add a dedicated button or keybinding for directory settings — discarded because the user explicitly requested a right-click context menu.

## Unknown: How to display a context menu near the pointer

**Decision**: Implement the menu as a small `Container` subclass mounted on a full-screen overlay layer with `position: absolute;` and set `self.styles.offset = (event.screen_x, event.screen_y)` in `on_mount`.

**Rationale**: Textual supports absolute offsets via `widget.styles.offset`, so a widget can be positioned at screen coordinates. Mounting it at a higher layer than the tree prevents it from being clipped by the sidebar container. Clicking outside the menu dismisses it by removing the overlay layer.

**Alternatives considered**:
- Use a centered `ModalScreen` — discarded because it does not appear near the pointer.
- Use a `Select` or `ListView` embedded in the sidebar — discarded because it is not a context menu and requires navigating away from the tree.

## Unknown: How to dismiss the context menu

**Decision**: Dismiss when the user presses `Escape`, clicks outside the menu bounds, or selects an action.

**Rationale**: This matches common context menu behavior and is natural in a TUI. The overlay layer can capture the click outside to dismiss and stop propagation to the tree.

**Alternatives considered**:
- Dismiss only on `Escape` — discarded because it is less intuitive.
- Dismiss automatically on any mouse movement — discarded because it would make keyboard navigation and accidental motion frustrating.

## Unknown: How to wire menu actions to existing color functionality

**Decision**: The "Settings" menu item opens the existing `DirectoryColorModal` (from feature 009). The "Reset" menu item calls the existing `action_reset_directory_color` path (or its helper) and refreshes the tree.

**Rationale**: Feature 009 already implemented color persistence, validation, and reset logic. Reusing it avoids duplication and keeps the architecture clean.

**Alternatives considered**:
- Duplicate color persistence logic for the new menu — discarded because it violates the architecture principle of keeping business logic in `core.py` and would create maintenance debt.

## Unknown: Whether right-click should also select the directory

**Decision**: Yes. Before opening the context menu, move the cursor and selection to the clicked node (`self.cursor_line = hover_line`, `self.select_node(node)`), and set `selected_dir` to the node path.

**Rationale**: The user expects the menu to relate to the directory under the pointer. Updating selection also makes the subsequent action consistent with keyboard-based actions.

**Alternatives considered**:
- Open menu without changing selection — discarded because it could be unclear which directory the actions apply to, especially if the pointer is between rows.
