---
id: d-a3e8kb
kind: decision
title: "Records are Markdown files in git, with settings outside the data"
scope: product
decided_by: coordinator
date: 2026-10-30T01:26:22+01:00
changes:
  - {entry: s-z1zvb4, action: create}
  - {entry: s-evv024, action: create}
  - {entry: s-r1eh11, action: create}
---

Records are Markdown files with a YAML header in git, one per file, behind one storage interface.
Settings live in `.lodge.toml` at the root of the working checkout, outside the data.

## Reasoning

One record per file behind one storage interface was settled, so that a server can replace the storage later.

The layout puts an area's title, intro, and order in `_area.md`, entries and decisions in their own files, and expanded evidence under attachments, outside the default read path.

Settings are outside the data because in branch mode lodge must know where the data is before it can read it.

Markdown with a YAML header follows an existing project: the header for programs, the body for people.

The layout, the Markdown with a YAML header, and the location of the settings are the specification author's calls, marked in the design document for the author to check.
