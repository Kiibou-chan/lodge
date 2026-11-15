# Recheck final fixes (cf71f19, c5af5fa)
Gate: bun run check at c5af5fa: 1862 pass, 0 fail, depcruise clean.
All five findings answered: body-before-auth http.ts:49-57; cap passkeys.ts:46-56; token text tokens.ts:19-27, ports.ts:79-84; I-1 person.ts:33-64; M-b http.ts:49-55.
Reverts: http.ts presence check -> 5 fail; person.ts text/attachments -> 4 fail (tests fail first).
Checks: presence regex equals auth.ts bearer regex; cookie via sessionSecret (non-empty); absent/chunked Content-Length gives 0, Bun limit still applies; held message branch unchanged; actorText not called on event reads.
Counts: 0 Blocking, 0 Important, 0 Minor.
