---
id: s-2bzwzv
kind: spec
title: "The specification offers written and dependency views"
rests_on: [s-v022r0, s-m4esa0]
---

The viewer specification offers "As written", the area's stored order, and "By dependency", which is also the order printed by `lodge spec` and the initial viewer view.
In the dependency view, dependants follow what they rest on, siblings in the area's order.
Each entry is indented under the last of its same-area dependencies to be placed, so it always sits under an entry it rests on; its other same-area dependencies appear on an "also rests on" line, and cross-area ones as "rests on s-xxxxxx (area)".
The stored area order remains check 7's reference; the derived order is for reading only.
Both views open with a "Sections" outline listing each area and, folded under it, its entries in the view's order, each a link to the entry; every area folds under its heading and starts open.
