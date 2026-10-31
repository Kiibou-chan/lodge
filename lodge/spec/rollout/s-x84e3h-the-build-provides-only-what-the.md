---
id: s-x84e3h
kind: spec
title: "The build provides only what the importer needs"
rests_on: [s-yhppm5, s-kvwrqw, s-f859z1]
---

The first build of lodge, 0.1.0, provides only what the importer needs: `imported_from`, explicit past dates (the date is data, so `core` stays clock-free), and the exemptions for imported records in the author-quote and entry-needs-decision checks.
An imported author decision without a recoverable quote shows as imported, unquoted, at Level 1, so that it does not read as more settled than it is.
