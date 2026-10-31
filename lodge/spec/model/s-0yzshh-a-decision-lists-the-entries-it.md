---
id: s-0yzshh
kind: spec
title: "A decision lists the entries it changes and the decisions it supersedes"
---

`changes` lists each specification entry the decision touches, with the action `create`, `edit`, `link`, or `retire`.
`replaces` and `narrows` name the decisions it supersedes in whole or in part.
`confirms` names agent decisions the author confirms, and only author decisions use it.
A `link` changes only an entry's `rests_on`; check 4 permits other alterations only when another decision of the same change lists the entry with `edit` or `create`.
