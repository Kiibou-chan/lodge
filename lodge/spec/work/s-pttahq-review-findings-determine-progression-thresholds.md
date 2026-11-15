---
id: s-pttahq
kind: spec
title: "Review findings determine progression thresholds"
rests_on: [s-tprwhs, s-cf0qph]
---

From build step 5, reviews report findings through the API as part of the review artefact, each with severity Blocking, Important, or Minor.
`no_findings_above` is read from findings rather than a verdict.
A move driven by a session's review is shown as reported rather than checked.
