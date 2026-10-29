### Task 13: Dogfooding and the public README

**Files:**
- Create: `.lodge.toml` (checkout mode, defaults), `lodge/**` through `lodge init` and `lodge add` only
- Modify: `README.md` (for a stranger: what lodge is, install from a tag, `lodge init`, the write path, the viewer, the hook snippet, `.lodge.toml` keys), `scripts/check.sh` (add `uv run lodge check --gate`)

- [ ] **Step 1:** `uv run lodge init` in this repository.
- [ ] **Step 2:** Record each item of the spec's "Her decisions, as she made them" as an author decision through `lodge add`: scope `product` for what lodge does, `process` for how it is built; `quote.text` her verbatim words from the spec or the brainstorm, `where: "lodge brainstorm"`, `when` the time given there, otherwise `2026-10-29`; where neither holds her words for that item, `quote: {text: "Approved", where: "docs/superpowers/specs/2026-10-29-lodge-design.md", when: "2026-10-29 14:26"}`; codes `LODGE-1` to `LODGE-4` on those four; reasoning a summary of the spec's why, never longer than the spec's own words on it.
- [ ] **Step 3:** `uv run lodge check --gate` and `uv run lodge waiting`; expected: `ok`, and `nothing waits for the author`.
- [ ] **Step 4:** Rewrite `README.md`; `grep -n '~/\|/home/' README.md src -r` prints nothing.
- [ ] **Step 5:** Set the version to `0.1.0` in `pyproject.toml` and `test_version`; run `sh scripts/check.sh`.
- [ ] **Step 6: Commit and push**; tag `v0.1.0` and push the tag.


## Carried from earlier tasks (ledger rulings, binding)

- Step 6 changes: commit and push the branch, but do not create or push any tag; the `v0.1.0` tag waits until after the final review and the merge to `main`, on the author's go.
- Step 2 covers every item in "Her decisions, as she made them", now including LODGE-5, LODGE-6, and LODGE-7, with codes `LODGE-1` to `LODGE-7` on those seven; LODGE-6 and LODGE-7 carry her words and times as the spec gives them. Run each add with `--dry-run` first.
- README: install from a tag (`uv tool install git+https://github.com/Kiibou-chan/lodge@<tag>`); the write path says `lodge add --dry-run` before `lodge add`; `--attach FILE` once per file, UTF-8 text only, for an add creating one decision; the hook section keeps the review's advice and states the frozen-glob syntax lodge implements without calling it `fnmatch` (Task 12 N2: `*` does not cross `/`, `[...]` is literal); "the author", never "her" or "she"; one sentence per line, British English, no em-dashes, Oxford comma.
- Record files are written only through `lodge add` (CLAUDE.md, Hard rules); never by hand.
