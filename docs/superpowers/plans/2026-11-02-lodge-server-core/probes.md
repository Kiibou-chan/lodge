# Probes for the server-core plan

Run on 2026-11-02 with Bun 1.3.14, Node 26.10.0, and npm 12.2.0, in a scratch folder holding the files in `probes/` (with `bun install`); outputs are quoted as printed.
The plan cites them as "probe N".

1. `bun test tests/db.test.ts`: a Kysely 0.29.7 query over `bun:sqlite` (`probes/src/server/db.ts`, a 15-line adapter to Kysely's `SqliteDatabase` interface) and a `fetch`-style handler called as `handler(new Request(...))` with no socket: `2 pass, 0 fail`.
2. `bun test tests/passkey.test.ts`: registration and sign-in through @simplewebauthn/server 14.0.3 with a software authenticator (ES256 key from WebCrypto, attestation `none`, the signature converted to DER): `1 pass, 0 fail, 4 expect() calls`; the sign-in counter reads 1, and a response to a wrong challenge is refused.
3. `bun build --compile src/cli/main.ts --outfile out/lodge` and `src/server/main.ts` (a `bun:sqlite` program): both binaries run, also under `env -i PATH=/usr/bin:/bin`; the command binary is 94,582,912 bytes.
4. `node --test nodet/` with `node:sqlite`: runs, but `assert.deepStrictEqual(rows, [{ a: 1 }])` fails, since its rows have a null prototype.
   `bun -e 'import {DatabaseSync} from "node:sqlite"'` prints `error: Could not resolve: "node:sqlite"`, and Node's `import("bun:sqlite")` fails with `ERR_UNSUPPORTED_ESM_URL_SCHEME`.
5. `node -e "require('typescript').createSourceFile"` with typescript 7.0.2 prints `undefined`, and dependency-cruiser 18.7.1 then prints `missing-typescript-transpiler: ... typescript: >=2.0.0 <7.0.0` and cruises 0 modules.
   With typescript 6.0.3 and dependency-cruiser 18.6.0, `depcruise src --config .dependency-cruiser.cjs` reports a cycle, an import past a front door, a `core` import of `app`, and `core-no-node: src/core/io.ts → fs`.
6. With `"imports": {"#core": "./src/core/index.ts"}` in `package.json`, `tsc -p .`, Bun, and dependency-cruiser all resolve `import { word } from "#core"` to `src/core/index.ts`; dependency-cruiser marks it `aliased-subpath-import`, and a `bun:sqlite` import is of type `core`.
7. `bun yprobe.ts` (the `yaml` package 2.9.1, `schema: "failsafe"`, `uniqueKeys: true`):
   scalars `yes`, `14:14`, `0x10`, and `~` stay text; `key:` gives `""`; a duplicate key is an error at its line (`DUPLICATE_KEY line 3`); `c: d: e` is an error at line 2;
   but `!!int 5` and `!!python/name:os.system` are only warnings (`TAG_RESOLVE_FAILED`), a U+0001 passes, two documents parse, 5,000 nested brackets parse without error, and the surrogate escapes `\ud83d` and `\ude00` in one double-quoted string join into one character while a lone `\ud83d` stays lone.
8. `bun h.ts` (`@noble/hashes` 2.4.0) and `python3 -c "import hashlib; print(hashlib.sha256(b'a\n').hexdigest()[:12])"` both print `87428fc52280`.
9. `bun -e 'console.log(typeof Temporal)'` and the same in Node print `undefined`, so dates are parsed by lodge's own code.
10. `knip` 6.42.0 reports unused files and unused dependencies; `biome check` 2.5.15 formats and lints `src` and `tests`; both run with no network once installed.
11. The publication dates on npm (`npm view <package> time`), for the rule that a pinned version is at least two weeks old: typescript 6.0.3 2026-04-16, @types/bun 1.4.3 2026-10-12, @biomejs/biome 2.5.15 2026-09-30, dependency-cruiser 18.6.0 2026-10-11, knip 6.42.0 2026-10-18, yaml 2.9.1 2026-09-11, @noble/hashes 2.4.0 2026-08-27, kysely 0.29.7 2026-10-17, @simplewebauthn/server 14.0.3 2026-09-25.
12. Python's `str.isspace()` and `re` `\s` take 0x9 to 0xd, 0x1c to 0x1f, 0x20, 0x85, 0xa0, 0x1680, 0x2000 to 0x200a, 0x2028, 0x2029, 0x202f, 0x205f, and 0x3000 as whitespace; JavaScript's `/\s/u` takes 0x9 to 0xd, 0x20, 0xa0, 0x1680, 0x2000 to 0x200a, 0x2028, 0x2029, 0x202f, 0x205f, 0x3000, and 0xfeff.
    So Python counts 0x1c to 0x1f and 0x85 as whitespace and JavaScript does not, and JavaScript counts 0xfeff and Python does not.
    `str.splitlines()` breaks at 0xa, 0xb, 0xc, 0xd, 0x1c, 0x1d, 0x1e, 0x85, 0x2028, and 0x2029 (checked below 0x3000), where `split("\n")` breaks at 0xa only.
13. With `HOME`, `XDG_CACHE_HOME`, and `TMPDIR` pointing at a read-only folder, `bun test`, `tsc`, dependency-cruiser, Biome, and knip all run as before, so the sandbox's read-only areas do not stop the gate.
14. Over every code point, Python's `re` `\w` matches 142,940 characters, all of which JavaScript's `/[\p{L}\p{N}_]/u` matches too, and the JavaScript class matches 4,657 more, assigned in later Unicode versions than Python's database; Python's `\d` matches 760, all matched by `/\p{Nd}/u`, which matches 10 more.
