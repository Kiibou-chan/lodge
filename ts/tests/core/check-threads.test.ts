import { expect, test } from "bun:test";
import {
  appended,
  checkChange,
  checkState,
  coreSettings,
  load,
  Raises,
  type Thread,
  ThreadState,
  tree,
  unrecordedProblems,
} from "#core";
import { area, entry, filesOf, message, snapshotOf, thread } from "./builders.ts";

test.each([false, true].map((c) => [c]))("thread_problems_are_visible_in_reads %p", (wrongName) => {
  const t = thread();
  const s = snapshotOf(
    [t],
    wrongName ? { paths: new Map([[t.id, "lodge/threads/wrong.md"]]) } : {},
  );
  const result = checkState(s);
  expect(result.problems.length).toBeGreaterThan(0);
  expect(unrecordedProblems(s, result)).toEqual(result.problems);
});

function changes(before: Thread, after: Thread) {
  const e = entry({ id: "s-aaaaaa" });
  return checkChange(
    snapshotOf([area(), e, before]),
    snapshotOf([area(), e, after]),
    coreSettings(),
    "2026-10-30T12:00:00+01:00",
  );
}
function fails(before: Thread, after: Thread, text: string) {
  expect(
    changes(before, after).problems.some((p) => p.check === 5 && p.message.includes(text)),
  ).toBe(true);
}
test("open_thread_passes_every_check", () => {
  const t = thread();
  expect(changes(t, t).ok).toBe(true);
  expect(checkState(snapshotOf([area({ order: [t.about] }), entry({ id: t.about }), t])).ok).toBe(
    true,
  );
});
test("unresolved_about_fails_check_2", () => {
  expect(
    checkState(snapshotOf([thread()])).problems.some(
      (p) => p.check === 2 && p.message.includes("about s-aaaaaa, which does not exist"),
    ),
  ).toBe(true);
});
test("duplicate_thread_id_fails_check_2", () => {
  const t = thread(),
    files = filesOf(t);
  files.set(`lodge/threads/${t.id}-copy.md`, [...files.values()][0] as string);
  expect(load(tree({ rev: null, files })).problems.filter((p) => p.check === 2)).toHaveLength(2);
});
test("file_name_must_start_with_the_id", () => {
  const t = thread();
  expect(
    checkState(
      snapshotOf([t], { paths: new Map([[t.id, "lodge/threads/wrong.md"]]) }),
    ).problems.some((p) => p.check === 1),
  ).toBe(true);
});
test("appending_a_message_passes", () => {
  const t = thread();
  expect(changes(t, appended(t, message())).ok).toBe(true);
});
test("closing_passes", () => {
  const t = thread();
  expect(changes(t, appended(t, message({ text: "" }), true)).ok).toBe(true);
});
test("editing_a_published_message_fails_check_5", () => {
  const t = thread();
  fails(
    t,
    { ...t, messages: [message({ text: "Edited." })] },
    "a published message was changed or removed; messages are only appended",
  );
});
test("removing_a_message_fails_check_5", () => {
  const t = thread({ messages: [message(), message()] });
  fails(t, { ...t, messages: t.messages.slice(0, 1) }, "a published message");
});
test("changing_about_fails_check_5", () => {
  const t = thread();
  fails(t, { ...t, about: "s-bbbbbb" }, "about of a published thread was changed");
});
test("changing_raises_fails_check_5", () => {
  const t = thread();
  fails(t, { ...t, raises: Raises.QUESTION }, "raises of a published thread was changed");
});
test("reopening_fails_check_5", () => {
  const t = thread({ state: ThreadState.CLOSED });
  fails(t, { ...t, state: ThreadState.OPEN }, "a closed thread was opened again");
});
test("message_after_closing_fails_check_5", () => {
  const t = thread({ state: ThreadState.CLOSED });
  fails(
    t,
    { ...t, messages: [...t.messages, message()] },
    "a message was added after the thread was closed",
  );
});
test("closing_without_a_message_fails_check_5", () => {
  const t = thread();
  fails(t, { ...t, state: ThreadState.CLOSED }, "a thread was closed without a closing message");
});
test.each([false, true].map((c) => [c]))(
  "missing_published_thread_fails_check_2 %p",
  (stalePath) => {
    const t = thread();
    const result = checkChange(
      snapshotOf([t]),
      snapshotOf([], stalePath ? { paths: new Map([[t.id, "lodge/threads/old.md"]]) } : {}),
      coreSettings(),
      "2026-10-30T12:00:00+01:00",
    );
    expect(result.problems.some((p) => p.check === 2 && p.message.includes(t.id))).toBe(true);
  },
);
test("changing_opened_fails_check_5", () => {
  const t = thread();
  fails(
    t,
    { ...t, opened: "2026-10-31T12:00:00+01:00" },
    "opened of a published thread was changed",
  );
});
