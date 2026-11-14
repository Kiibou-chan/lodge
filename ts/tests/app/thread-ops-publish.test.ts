import { expect, test } from "bun:test";
import { AddOutcome, Conflict, NotFound } from "#app";
import { filters, Raises } from "#core";
import { areaText } from "../core/applying.ts";
import { CountingIds, FixedClock } from "./fakes.ts";
import { opened, PATH, project, Q, raises, required, wired } from "./support.ts";

test("rejected_publish_starts_again", async () => {
  const store = project();
  store.rejectNext(new Map());
  const written = await wired(store).ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?");
  expect(written.outcome).toBe(AddOutcome.PUBLISHED);
  expect(store.attempts).toBe(2);
});

test("commit_after_staged_when_asked", async () => {
  const store = project({ staged: true });
  const written = await wired(store).ask("s-aaaaaa", Raises.DOUBT, "author", "Why?", {
    where: "a session",
    commit: true,
  });
  expect(store.commits).toEqual([[[PATH], `Thread ${Q}: doubt raised by author`]]);
  expect(written.committed).not.toBeNull();
  expect(required(written.committed).detail).toBe("");
});

test("no_commit_unless_asked", async () => {
  const { store, lodge } = await opened(true);
  const written = await lodge.reply(Q, "agent", "Here.");
  expect(store.commits).toEqual([]);
  expect(written.committed).toBeNull();
});

test("no_commit_when_published", async () => {
  const store = project();
  const written = await wired(store).ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?", {
    commit: true,
  });
  expect(store.commits).toEqual([]);
  expect(written.committed).toBeNull();
});

test("threads_lists_open_newest_last", async () => {
  const store = project(),
    lodge = wired(store, new FixedClock(undefined, 60000), new CountingIds(9, -1));
  await lodge.ask("s-aaaaaa", Raises.DOUBT, "agent", "First");
  await lodge.ask("s-aaaaaa", Raises.QUESTION, "agent", "Second");
  const third = await lodge.ask("s-aaaaaa", Raises.DOUBT, "agent", "Third");
  await lodge.close(required(third.ids[0]), "agent");
  const listed = await lodge.threads();
  expect(listed.items.map((t) => t.id)).toEqual(["q-999999", "q-888888"]);
  expect(listed.titles.get("s-aaaaaa")).toBe("Transcripts are kept");
  expect(listed.read.freshness).not.toBeNull();
});

test("thread_shows_one_thread", async () => {
  const { lodge } = await opened();
  const shown = await lodge.thread(Q.toUpperCase());
  expect(shown.thread.id).toBe(Q);
  expect(shown.about?.id).toBe("s-aaaaaa");
  expect(shown.read.freshness).not.toBeNull();
  await raises(lodge.thread("q-000000"), NotFound, "no thread named q-000000");
});

test("threads_waiting_groups", async () => {
  const { lodge } = await opened();
  await lodge.ask("s-aaaaaa", Raises.QUESTION, "author", "Second", { where: "a session" });
  const waiting = await lodge.threadsWaiting();
  expect(waiting.forAgent.map((t) => t.id)).toEqual(["q-222222"]);
  expect(waiting.forAuthor.map((t) => t.id)).toEqual([Q]);
  expect(waiting.titles).toEqual(new Map([["s-aaaaaa", "Transcripts are kept"]]));
  expect(waiting.read.freshness).not.toBeNull();
});

test("show_carries_the_records_threads", async () => {
  const { lodge } = await opened();
  await lodge.close(Q, "agent");
  expect((await lodge.show("s-aaaaaa")).threads.map((t) => t.id)).toEqual([Q]);
  expect((await lodge.show("item-1")).threads).toEqual([]);
});

test("added_paths_lists_the_files_written", async () => {
  const added = await wired(project()).add([["area.md", areaText("name: access")]]);
  expect(added.paths).toEqual(["lodge/spec/access/_area.md"]);
});

test("search_and_timeline_leave_threads_out", async () => {
  const { lodge } = await opened();
  expect(new Set((await lodge.search("", filters())).items.map((i) => i.id))).toEqual(
    new Set(["s-aaaaaa", "d-aaaaaa"]),
  );
  expect((await lodge.timeline()).items.map((i) => i.id)).toEqual(["d-aaaaaa"]);
});

test("thread_about_a_missing_record_reads", async () => {
  const { store, lodge } = await opened();
  store.files.set(PATH, required(store.files.get(PATH)).replace("s-aaaaaa", "s-zzzzzz"));
  const shown = await lodge.thread(Q);
  expect(shown.about).toBeNull();
  expect(required(shown.thread.messages[0]).text).toBe("Why?");
  expect(required((await lodge.threads()).items[0]).about).toBe("s-zzzzzz");
  expect(required((await lodge.threadsWaiting()).forAuthor[0]).id).toBe(Q);
});

test("three_rejections_are_a_conflict", async () => {
  const store = project();
  store.rejectNext(new Map(), new Map(), new Map());
  await raises(
    wired(store).ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?"),
    Conflict,
    "three times",
  );
  expect(store.attempts).toBe(3);
  expect(store.publishes).toEqual([]);
});
