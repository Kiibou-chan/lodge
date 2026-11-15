---
id: s-3cagcv
kind: spec
title: "The hook redirects moved projects to the server"
---

lodge 0.2 stays usable until a project moves.
A project has moved when its `.lodge.toml` names its server.
Whatever the local store's mode, the hook advises on every file under `lodge/` except attachments that the records live on that server and changes go through the command.
Threads use the thread commands, and frozen-file advice also names the server.
Editing a leftover local copy changes nothing on the server.
