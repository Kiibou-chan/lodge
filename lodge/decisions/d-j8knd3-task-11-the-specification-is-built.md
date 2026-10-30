---
id: d-j8knd3
kind: decision
title: "Task 11: the specification is built as structure and escapes lines starting with a hash"
scope: process
decided_by: coordinator
date: 2026-10-29T18:34:25+01:00
work_item: "docs/superpowers/plans/done/2026-10-29-lodge.md"
imported_from: {file: "docs/superpowers/plans/done/2026-10-29-lodge-progress.md", heading: "line 160"}
---

I1, `core` gains `spec_view(s, d, failing, area=None)` returning the areas as structure (title, intro, `Level1` entries in order); `render_spec` formats that structure and puts a backslash before any intro or statement line starting with `#`; the app's `spec` returns the structure beside the text, and `spec_page` builds its headings from the fields, never by parsing Markdown.

## Reasoning

A statement starting `## ` rendered a flagged entry's text as a separate unflagged entry (task-11-review.md, I1, run), must-not 1, and the escape keeps `lodge spec` output unambiguous too.
Cost if wrong: one more core function and a changed `spec_page` signature.
Line handles such as spec:N refer to the files at this ruling's date.
