import {
  appended,
  checkChange,
  cleanText,
  level1,
  load,
  type Message,
  newestLast,
  Raises,
  strip,
  type Thread,
  ThreadState,
  threadPath,
  tree,
  ValueError,
  writeThread,
} from "#core";
import { Conflict, Forbidden, LodgeError, NotFound } from "./errors.ts";
import { actorText, type Now, PublishOutcome } from "./ports.ts";
import {
  AddOutcome,
  type ThreadList,
  type ThreadShown,
  type ThreadsWaiting,
  type Written,
  written,
} from "./results.ts";
import { notFound, readChecked, readState, resolveRef, type State, type Wiring } from "./state.ts";
import { minuteOf, stampOf } from "./time.ts";
import { mintUnused } from "./writes.ts";

function find(state: State, ref: string): Thread {
  const thread = state.snapshot.threads.get(ref.toLowerCase());
  if (!thread) throw notFound(state, `thread named ${ref}`, ref);
  return thread;
}
function message(
  now: Now,
  people: ReadonlySet<string>,
  by: string,
  text: string,
  where: string | null,
  when: string | null,
  close: boolean,
): Message {
  text = cleanText(text);
  if (!text && !close) throw new LodgeError("the message is empty");
  if (!strip(by)) throw new LodgeError("by needs a non-empty role");
  if (!people.has(by) && by.toLowerCase().includes("author"))
    throw new LodgeError(
      people.has("author")
        ? "write author exactly, or use your own role"
        : "name a person of the project exactly, or use your own role",
    );
  let stamp: string;
  if (people.has(by)) {
    if (where === null || !strip(where))
      throw new LodgeError(
        by === "author"
          ? "a message by author needs where, the place of the author's words"
          : `a message by ${by} needs where, the place of ${by}'s words`,
      );
    stamp = when ?? minuteOf(now);
  } else {
    if (where !== null || when !== null)
      throw new LodgeError(
        people.has("author")
          ? "where and when are for messages by author"
          : "where and when are for messages by a person",
      );
    stamp = stampOf(now);
  }
  return { by, when: stamp, text, where };
}
export interface MessageOptions {
  readonly where?: string | null;
  readonly when?: string | null;
  readonly commit?: boolean;
  readonly close?: boolean;
}
export async function writeMessage(
  w: Wiring,
  ref: string,
  raises: Raises | null,
  by: string,
  text: string,
  { where = null, when = null, commit = false, close = false }: MessageOptions = {},
  approves: number | null = null,
): Promise<Written> {
  for (let i = 0; i < 3; i++) {
    if (approves !== null && !(await w.store.held()).some((h) => h.seq === approves))
      throw new NotFound(`nothing is held under number ${approves}`);
    const state = await readState(w.store),
      now = w.clock.now(),
      msg = message(now, state.snapshot.people, by, text, where, when, close),
      s = state.snapshot;
    let thread: Thread, description: string;
    if (raises !== null) {
      const about = resolveRef(state, ref),
        id = mintUnused(
          w.ids,
          "q",
          new Set([...s.decisions.keys(), ...s.entries.keys(), ...s.threads.keys()]),
        );
      thread = {
        kind: "thread",
        id,
        about,
        raises,
        state: ThreadState.OPEN,
        opened: stampOf(now),
        messages: [msg],
      };
      description = `${raises === Raises.DOUBT ? "doubt raised" : "question asked"} by ${by}`;
    } else {
      thread = find(state, ref);
      if (thread.state === ThreadState.CLOSED) throw new LodgeError(`${thread.id} is closed`);
      thread = appended(thread, msg, close);
      description = close ? `closed by ${by}` : `${by} reply`;
    }
    if (s.people.has(by) && w.actor.kind === "person" && w.actor.name !== by)
      throw new Forbidden(`only ${by} writes as ${by}; nothing was written`);
    const path = threadPath(thread.id);
    let content: string;
    try {
      content = writeThread(thread, s.people);
    } catch (error) {
      if (!(error instanceof ValueError)) throw error;
      throw new LodgeError(error.message);
    }
    const after = load(
      tree({
        rev: state.current.rev,
        people: state.current.people,
        files: new Map([...state.current.files, [path, content]]),
        attachments: state.current.attachments,
      }),
    );
    const check = checkChange(load(state.published), after, w.settings, stampOf(now), s);
    if (!check.ok)
      return written({
        ids: [thread.id],
        outcome: AddOutcome.CHECK_FAILED,
        check,
        about: thread.about,
      });
    if (s.people.has(by) && w.actor.kind === "agent") {
      const held = await w.store.hold({
        kind: "message",
        person: by,
        by: actorText(w.actor),
        operation: raises !== null ? "ask" : close ? "close" : "reply",
        ref: raises !== null ? thread.about : thread.id,
        raises,
        text: close && !msg.text ? null : msg.text,
        where: msg.where as string,
        when: msg.when,
      });
      return written({
        ids: [thread.id],
        outcome: AddOutcome.HELD,
        check,
        about: thread.about,
        awaits: by,
        held,
      });
    }
    const commitMessage = `Thread ${thread.id}: ${description}`;
    const outcome = await w.store.publish(
      state.current,
      new Map([[path, content]]),
      commitMessage,
      approves,
    );
    if (outcome === PublishOutcome.REJECTED) {
      if (approves !== null && !(await w.store.held()).some((h) => h.seq === approves))
        throw new NotFound(`nothing is held under number ${approves}`);
      continue;
    }
    const committed =
      commit && outcome === PublishOutcome.STAGED
        ? await w.store.commit([path], commitMessage)
        : null;
    return written({
      ids: [thread.id],
      outcome: outcome === PublishOutcome.PUBLISHED ? AddOutcome.PUBLISHED : AddOutcome.STAGED,
      check,
      committed,
      about: thread.about,
    });
  }
  throw new Conflict(
    "other changes reached the store three times; nothing was written, so try again",
  );
}
export async function listOpen(w: Wiring): Promise<ThreadList> {
  return openIn(await readChecked(w));
}
function openIn(state: State): ThreadList {
  const s = state.snapshot,
    items = newestLast([...s.threads.values()].filter((t) => t.state === ThreadState.OPEN));
  const records = new Map<string, { readonly title: string }>([...s.decisions, ...s.entries]);
  const titles = new Map<string, string>();
  for (const t of items) {
    const r = records.get(t.about);
    if (r) titles.set(t.about, r.title);
  }
  return { items, titles, read: state.read };
}
export async function show(w: Wiring, ref: string): Promise<ThreadShown> {
  const state = await readChecked(w),
    thread = find(state, ref),
    s = state.snapshot;
  return {
    thread,
    about:
      s.decisions.has(thread.about) || s.entries.has(thread.about)
        ? level1(s, state.derived, thread.about, state.failing)
        : null,
    read: state.read,
  };
}
export async function waiting(w: Wiring): Promise<ThreadsWaiting> {
  return waitingIn(await readChecked(w));
}
export function waitingIn(state: State): ThreadsWaiting {
  const listed = openIn(state);
  return {
    forAgent: listed.items.filter((t) => state.snapshot.people.has(t.messages.at(-1)?.by ?? "")),
    forAuthor: listed.items.filter((t) => !state.snapshot.people.has(t.messages.at(-1)?.by ?? "")),
    titles: listed.titles,
    read: listed.read,
  };
}
