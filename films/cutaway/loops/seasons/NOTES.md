# Seasons loop: notes

- 23 Oct 2026: opt-in art directions. `build` ends with a hook: when the module global `KF_ART_NAME` (set by a look-board
  folder, films/cutaway/looks/seasons-<name>/) or `$KF_ART` names a look, the finished scene is dressed by
  films/styles/cutaway/art/<name>.py through films/styles/cutaway/art/_adapter.py, and `frame` calls the look's per-frame
  code last. Without either, nothing changes: frame 100 at 180x320, 8 samples, rendered before and after the edit is
  identical (max pixel difference 0). Cost: none.
