---
id: s-3n0ndk
kind: spec
title: "Search and show give Level 1 first"
---

Search takes several queries from one read, each its words or, with `--phrase`, whole words in order, over titles, statements, and codes, filtered by kind, scope, status, area, and decided-by; a code lists its family and citing records first, then records holding every word, then some; results are Level 1 lines, each record printed once.
With `--brief`, search gives one line per record instead, its header and title without the statement, without the status current under the default filter.
Showing a record gives Level 1, and `show` takes several refs from one read, each record once; a coded record's siblings and citing records follow as brief lines; reasoning and provenance come only when asked for by name.
