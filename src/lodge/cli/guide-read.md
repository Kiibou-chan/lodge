# lodge: the reading guide for agents

A decision records a change and why, with who decided and the entries it changes.
An entry says what holds now, in one paragraph, and belongs to an area.
An area groups entries with a title, an intro, and a written order.
Read through lodge, never by opening record files.
Run `lodge waiting` at the start of a session, note and tell the author what waits for an agent.
`lodge search "several words" --brief`
`lodge search --phrase "exact words in order" --brief`
`lodge search CODE --brief`
`lodge search word1 word2 --brief`
Quotes only group words into one query, with records holding all the words first; --phrase lists exact runs first, then near matches with every word in another order, then some words, and word1 word2 makes two queries.
A code search puts the family and citers first, with dotted descendants belonging to the family; CODE.why is used where a project codes reasoning that way.
`lodge show REF REF REF`
`lodge show CODE.why --reasoning`
`lodge show REF --provenance`
REF is an ID or a code; show gives the statement, status, who decided, date, and flags, and lists siblings and citers for a coded record.
--reasoning adds the why, or an entry's changing decisions; --provenance adds the author's quote, numbers, work item, attachments, and links both ways.
`lodge spec`
`lodge threads`
The specification groups entries by area; threads lists open doubts and questions, and lodge thread ID reads one by its ID.
Unmarked brief records are current, meaning they still hold; replaced decisions have successors, retired entries no longer hold, and author confirmation is a separate flag.
"awaiting the author" means an agent changed something the author decided or confirmed, so do not treat it as settled.
"in doubt" marks an open doubt on a record or its dependencies; "question open" marks a question, and "narrowed by" names decisions limiting what holds.
"fails check" marks a record failing a check, and problem: names a file lodge cannot read; tell the author about either, and about a freshness line saying the lodge branch was rewritten, which only the author accepts.
