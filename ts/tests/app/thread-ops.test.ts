import { expect, test } from "bun:test";
import { LodgeError, NotFound } from "#app";
import { load, Raises, ThreadState, tree } from "#core";
import { project, raises, wired } from "./support.ts";

const Q = "q-111111";
const PATH = `lodge/threads/${Q}.md`;
async function opened(staged = false) {
  const store = project({ staged }),
    lodge = wired(store);
  await lodge.ask("s-aaaaaa", Raises.DOUBT, "coordinator", "Why?");
  return { store, lodge };
}
function stored(store: ReturnType<typeof project>) {
  const thread = load(tree({ rev: null, files: store.files })).threads.get(Q);
  if (!thread) throw new Error("missing thread");
  return thread;
}
test("ask_writes_a_thread_file", async () => {
  const store = project();
  const written = await wired(store).ask("s-aaaaaa", Raises.DOUBT, "coordinator", "Why?");
  expect([...required(store.publishes[0])[0].keys()]).toEqual([PATH]);
  const thread = stored(store);
  expect(written.about).toBe(thread.about);
  expect(thread.about).toBe("s-aaaaaa");
  expect(thread.raises).toBe(Raises.DOUBT);
  expect(thread.state).toBe(ThreadState.OPEN);
  expect(thread.messages).toHaveLength(1);
  expect(required(thread.messages[0]).by).toBe("coordinator");
  expect(required(thread.messages[0]).when).toBe("2026-10-29T09:30:00+01:00");
  expect(written.ids).toEqual([Q]);
  expect(written.check.ok).toBe(true);
});

test("ask_resolves_a_code", async () => {
  const store = project();
  await wired(store).ask("item-1", Raises.QUESTION, "reviewer", "Why?");
  expect(stored(store).about).toBe("d-aaaaaa");
  expect(required(store.publishes[0])[1]).toBe(`Thread ${Q}: question asked by reviewer`);
});

test("ask_on_an_unknown_ref_is_not_found", async () => {
  await raises(
    wired(project()).ask("missing", Raises.DOUBT, "agent", "Why?"),
    NotFound,
    "no record named missing",
  );
});

test("author_message_needs_where", async () => {
  await raises(
    wired(project()).ask("s-aaaaaa", Raises.DOUBT, "author", "Why?"),
    LodgeError,
    "a message by author needs where",
  );
});

test("author_when_defaults_to_the_minute", async () => {
  const store = project();
  await wired(store).ask("s-aaaaaa", Raises.DOUBT, "author", "Why?", { where: "a session" });
  expect(required(stored(store).messages[0]).when).toBe("2026-10-29 09:30");
});

test.each([[{ where: "a session" }], [{ when: "yesterday" }]])(
  "agent_message_may_not_carry_where",
  async (value) => {
    await raises(
      wired(project()).ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?", value),
      LodgeError,
      "where and when are for messages by author",
    );
  },
);

test.each([["Author"], ["the author"], [""]])("role_like_author_refused", async (value) => {
  await raises(
    wired(project()).ask("s-aaaaaa", Raises.DOUBT, value, "Why?"),
    LodgeError,
    value ? "write author exactly, or use your own role" : "by needs a non-empty role",
  );
});

test.each([[""], [" \r\n "]])("empty_text_refused", async (value) => {
  const { store, lodge } = await opened();
  await raises(
    lodge.ask("s-aaaaaa", Raises.DOUBT, "agent", value),
    LodgeError,
    "the message is empty",
  );
  await raises(lodge.reply(Q, "agent", value), LodgeError, "the message is empty");
  expect(store.publishes).toHaveLength(1);
});

test("text_loses_cr_and_outer_whitespace_only", async () => {
  const store = project();
  await wired(store).ask("s-aaaaaa", Raises.DOUBT, "agent", " \r\nA  B\r\n C \r\n ");
  expect(required(stored(store).messages[0]).text).toBe("A  B\n C");
});

test.each([["where"], ["when"]])("unstorable_where_refused", async (value) => {
  const store = project();
  const meta = { where: "a session", [value]: "a\x01" };
  await raises(
    wired(store).ask("s-aaaaaa", Raises.DOUBT, "author", "Why?", meta),
    LodgeError,
    value,
  );
  expect(store.publishes).toEqual([]);
});

test("reply_appends", async () => {
  const { store, lodge } = await opened();
  const written = await lodge.reply(Q.toUpperCase(), "author", "Here.", { where: "a session" });
  expect(stored(store).messages.map((m) => m.text)).toEqual(["Why?", "Here."]);
  expect(written.about).toBe("s-aaaaaa");
  expect(required(store.publishes.at(-1))[1]).toBe(`Thread ${Q}: author reply`);
});

test("reply_to_closed_thread_refused", async () => {
  const { lodge } = await opened();
  await lodge.close(Q, "agent");
  await raises(lodge.reply(Q, "agent", "Again"), LodgeError, `${Q} is closed`);
  await raises(lodge.close(Q, "agent"), LodgeError, `${Q} is closed`);
});

test("close_appends_closed_by_the_closer", async () => {
  const { store, lodge } = await opened();
  await lodge.close(Q, "reviewer");
  const thread = stored(store);
  expect(thread.state).toBe(ThreadState.CLOSED);
  expect(required(thread.messages.at(-1)).text).toBe("");
  expect(required(thread.messages.at(-1)).by).toBe("reviewer");
  expect(required(store.publishes.at(-1))[1]).toBe(`Thread ${Q}: closed by reviewer`);
});

test("close_without_text_passes_the_check", async () => {
  const { lodge } = await opened();
  expect((await lodge.close(Q, "agent")).check.ok).toBe(true);
});

test.each([
  [" Answer.\r\n ", "Answer."],
  [" \r\n ", ""],
])("close_with_text", async (text, expected) => {
  const { store, lodge } = await opened();
  await lodge.close(Q, "agent", { text });
  expect(required(stored(store).messages.at(-1)).text).toBe(expected);
});

function required<T>(value: T | undefined | null): T {
  if (value === undefined || value === null) throw new Error("missing fixture value");
  return value;
}
