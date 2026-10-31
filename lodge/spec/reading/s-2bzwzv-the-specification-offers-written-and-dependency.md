---
id: s-2bzwzv
kind: spec
title: "The specification offers written and dependency views"
rests_on: [s-v022r0, s-m4esa0]
---

The viewer specification offers "As written", the area's stored order, and "By dependency", which is also the order printed by `lodge spec` and the initial viewer view.
In the dependency view, dependants follow what they rest on, siblings in the area's order.
Each entry is indented under the first entry it rests on in the area; additional dependencies appear as lines, with cross-area links shown as "rests on s-xxxxxx (area)".
The stored area order remains check 7's reference; the derived order is for reading only.
