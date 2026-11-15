---
id: s-fe4kyr
kind: spec
title: "Builder choices include workflow syntax, mailbox layout, and interface layout"
rests_on: [s-165qfh, s-sb9gee, s-0tn1e8]
---

The workflow document's syntax remains open.
The API's shape is settled as JSON operations over HTTP by d-sry12f, within one API for the interface, the command, and the MCP server.
The passkey library is @simplewebauthn/server under d-yayhct, and the query builder is Kysely under d-4k9wcr.
The dependency checker uses dependency-cruiser and TypeScript's parser.
The mailbox branch's file layout remains open.
Board and task-page appearance remains open within the specified views; a mock goes to the author through the mocking step before the interface is built.
