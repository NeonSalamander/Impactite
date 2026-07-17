# Research: Directory Tree Colors

## Decision

Store directory colors in `config.yaml` under a top-level `directory_colors` key, keyed by the directory's path relative to `notes_path`. Apply the colors inside the `FileTree` subclass by customizing `Tree.render_label` (and, if necessary, `_render_line`) to inject per-node `Style` colors.

For user input, provide a small modal (`DirectoryColorModal`) with two `Input` fields: one for the background color and one for the label/text color. Validation uses Textual's `Color.parse`; invalid values are rejected before saving.

## Rationale

- `config.yaml` already stores user preferences such as `display.app_theme`, so it is the natural place for directory color personalization.
- Using relative paths keeps the config portable across machines and mirrors how the file tree is constructed from `file_system.root_path`.
- `FileTree` is already a subclass of `Tree`, and `Tree.render_label` is explicitly documented as the intended extension point for customizing how labels are rendered. This lets us inject backgrounds and foregrounds without replacing the tree widget.
- Textual/Rich `Style` accepts any color string that `Color.parse` understands (named colors, hex, rgb), which is enough for the requested functionality and avoids adding a color-picker dependency.
- A modal follows the existing interaction pattern used for creating folders, notes, and selecting templates.

## Alternatives Considered

- **External sidecar file (e.g., `.directory_colors.yaml` inside notes)**: Rejected because the user explicitly requested that colors be saved in settings, and a sidecar file would introduce an additional persistent artifact outside the config.
- **Absolute path keys**: Rejected because it would make the config non-portable and would break when the vault is moved or synced to another machine.
- **Per-directory hidden metadata file**: Rejected; it would pollute the notes tree and conflict with the plain-file philosophy of the project.
- **Built-in color picker widget**: Textual does not ship with a standard color picker in the current version, so no extra dependency solution exists. Using validated `Input` fields keeps the implementation self-contained.
- **Applying colors recursively to child files/directories**: Rejected to match the spec scope: colors affect only the directory node itself, not its children.
