---
id: d-14vk9b
kind: decision
title: "lodge is a command-line tool with instructions, not an MCP server"
scope: product
decided_by: author
date: 2026-10-29T22:16:47+01:00
quote: {text: "I don't think I can install additional mcp servers in cloud environments", where: "lodge brainstorm", when: "2026-10-29"}
---

Agents use lodge through a command they run through Bash, plus a guide that lodge prints.
There is no MCP server.

## Reasoning

I don't think I can install additional mcp servers in cloud environments
