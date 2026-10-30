---
id: s-fdzcr2
kind: spec
title: "IDs are minted without coordination, and records may carry a code"
---

An ID is a type prefix and six random characters from Crockford's base32 alphabet, minted without coordination between sessions and never reused.
A record may also carry a human `code` such as ITEM-1, unique and checked, because the author and the sessions quote codes; search finds a record by its code.
