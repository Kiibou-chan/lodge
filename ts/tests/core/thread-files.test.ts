import { expect, test } from "bun:test";
import {
  appended,
  derive,
  feedback,
  lengthGuidance,
  load,
  newestLast,
  type Problem,
  parseThread,
  type Thread,
  threadPath,
  tree,
  ValueError,
  writeThread,
} from "#core";
import { at, decision, filesOf, message, snapshotOf, thread } from "./builders.ts";

function parsed(t: Thread): Thread {
  const p = parseThread(threadPath(t.id), writeThread(t));
  expect(p.kind).toBe("thread");
  return p as Thread;
}
function invalid(old: string, value: string): Problem {
  const t = thread();
  const p = parseThread(threadPath(t.id), writeThread(t).replace(old, value));
  expect(p.kind).toBe("problem");
  expect((p as Problem).check).toBe(1);
  return p as Problem;
}
test("thread_round_trips", () => {
  const t = thread({
    state: "closed",
    messages: [
      message({ text: "One.\nTwo." }),
      message({ by: "author", when: "yesterday", where: "lodge viewer" }),
      message({ text: "" }),
    ],
  });
  expect(parsed(t)).toEqual(t);
});
test.each([
  [false, false],
  [true, true],
])("empty_text_only_on_the_closing_message %p %p", (closed, first) => {
  const t = thread({ state: closed ? "closed" : "open" });
  let text = writeThread(t).replace("A message.", "");
  if (first) text += `\n## Message 2\n\nby: coordinator\nwhen: ${at(1)}\n\nEnd.\n`;
  expect(parseThread(threadPath(t.id), text).kind).toBe("problem");
});
export const EXAMPLE = `---
id: q-4kq1zm
kind: thread
about: s-0abcde
raises: doubt
state: open
opened: 2026-10-29T09:30:00+01:00
---

## Message 1

by: author
when: "2026-10-29 09:30"
where: "lodge viewer"

Is this still true?

## Message 2

by: coordinator
when: 2026-10-29T10:00:00+01:00

It is; see d-3m8qk2.
`;
test("written_shape_matches_the_example", () =>
  expect(
    writeThread(
      thread({
        id: "q-4kq1zm",
        about: "s-0abcde",
        opened: "2026-10-29T09:30:00+01:00",
        messages: [
          message({
            by: "author",
            when: "2026-10-29 09:30",
            where: "lodge viewer",
            text: "Is this still true?",
          }),
          message({ when: "2026-10-29T10:00:00+01:00", text: "It is; see d-3m8qk2." }),
        ],
      }),
    ),
  ).toBe(EXAMPLE));
test.each(["## Message 2", "\\## Message 2"].map((c) => [c]))(
  "text_line_like_a_heading_round_trips %p",
  (text) => expect(parsed(thread({ messages: [message({ text })] })).messages[0]?.text).toBe(text),
);
test.each(['a: "b" # c', "<script>", "## Reasoning"].map((c) => [c]))(
  "yaml_and_markdown_specials_round_trip %p",
  (text) => expect(parsed(thread({ messages: [message({ text })] })).messages[0]?.text).toBe(text),
);
test("author_message_needs_where", () =>
  expect(invalid("by: coordinator", "by: author").message).toContain(
    "an author message needs where",
  ));
test("malformed_id_is_problem_1", () =>
  expect(parseThread("lodge/threads/q-BAD.md", EXAMPLE.replace("q-4kq1zm", "q-BAD")).kind).toBe(
    "problem",
  ));
test("about_must_name_a_decision_or_entry", () =>
  expect(invalid("about: s-aaaaaa", "about: q-aaaaaa").message).toContain("about must name"));
test("thread_needs_a_message", () =>
  expect(invalid("## Message 1", "").message).toContain("at least one message"));
test("messages_numbered_in_order", () =>
  expect(invalid("## Message 1", "## Message 2").message).toContain("numbered"));
test("body_text_before_first_message_refused", () => {
  invalid("## Message 1", "Stray text.\n\n## Message 1");
});
test("appended_refuses_a_closed_thread", () => {
  expect(() => appended(thread({ state: "closed" }), message())).toThrow(ValueError);
  expect(() => appended(thread(), message({ text: "" }))).toThrow(ValueError);
});
test("newest_last_by_opened_then_id", () => {
  const a = thread({ id: "q-aaaaaa", opened: at(1) }),
    b = thread({ id: "q-bbbbbb", opened: at(1) }),
    c = thread({ opened: at(0) });
  expect(newestLast([b, a, c])).toEqual([c, a, b]);
});
test("load_reads_threads_and_their_paths", () => {
  const t = thread(),
    s = load(tree({ rev: null, files: filesOf(t) }));
  expect(s.threads.get(t.id)).toEqual(t);
  expect(s.paths.get(t.id)).toBe(threadPath(t.id));
});
test("nested_file_under_threads_is_stray", () => {
  const s = load(
    tree({ rev: null, files: new Map([["lodge/threads/nested/q-aaaaaa.md", EXAMPLE]]) }),
  );
  expect(s.problems[0]?.check).toBe(1);
  expect(s.problems[0]?.path).toBe("lodge/threads/nested/q-aaaaaa.md");
  expect(s.problems[0]?.message).toContain("this file is not a record");
});
test.each([false, true].map((c) => [c]))("appended_cleans_the_text_and_closes %p", (close) => {
  const r = appended(thread(), message({ text: close ? " " : "a\r\nb \r\n  " }), close);
  expect(r.messages.at(-1)?.text).toBe(close ? "" : "a\nb");
  expect(r.state).toBe(close ? "closed" : "open");
});
test.each([
  [`opened: ${at(0)}`, "opened: yesterday", "opened"],
  ["raises: doubt", "raises: worry", "raises"],
  ["state: open", "state: ajar", "state"],
  [`when: ${at(0)}`, "when: yesterday", "when"],
  ["by: coordinator", "by: coordinator\nextra: value", "extra"],
  ["by: coordinator\n", "", "by"],
])("unreadable_header_values_are_problem_1 %p %p %p", (old, value, key) =>
  expect(invalid(old, value).message).toContain(key),
);
test.each(["A message. ", "A\r\nmessage."].map((c) => [c]))(
  "write_text_error_names_the_field %p",
  (text) => {
    expect(() => writeThread(thread({ messages: [message({ text })] }))).toThrow(ValueError);
    expect(() => writeThread(thread({ messages: [message({ text })] }))).toThrow(/message 1 text/u);
  },
);
test("message_without_metadata_names_the_message", () => {
  const p = invalid(`by: coordinator\nwhen: ${at(0)}\n\nA message.`, "");
  expect(p.message).toBe("a message needs by and when");
  expect(p.line).toBe(10);
});
test("thread_id_is_not_number_feedback", () => {
  const d = decision({ statement: "See q-123456." });
  const s = snapshotOf([d]);
  expect(
    feedback([d], s, derive(s), lengthGuidance()).some((f) => f.message.includes("number")),
  ).toBe(false);
});
