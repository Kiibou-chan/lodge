---
id: s-b4dtqk
kind: spec
title: "Export batches writes within each server run"
rests_on: [s-f6eaj1]
---

Every published write tells the exporter.
Within one run of the server, exports batch to at most one commit a minute.
After a failure or a moved branch, the exporter retries after a minute.
On restart, `start` exports at once for projects with a target; the interval is not persisted across restarts.
An unchanged tree makes no commit.
