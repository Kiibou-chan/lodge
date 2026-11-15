---
id: s-p6n0x6
kind: spec
title: "MCP exposes the same operations to local sessions only"
rests_on: [s-zjdzre]
---

An MCP server exposes the same operations for local sessions only.
Cloud sessions use the `lodge` command because MCP connectors travel through Anthropic's servers, where the environment's network secret does not reach them.
