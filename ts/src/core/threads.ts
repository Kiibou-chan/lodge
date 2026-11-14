import { assemble, keyLine, loadHeader, readWith, trimBlock } from "./document.ts";
import { equal } from "./equal.ts";
import { ValueError } from "./errors.ts";
import {
  checkKeys,
  FormatError,
  readEnum,
  readId,
  readOptionalStr,
  readStamp,
  readStr,
  require as requireField,
} from "./fields.ts";
import { isId } from "./ids.ts";
import { type Message, type Problem, Raises, type Thread, ThreadState } from "./model.ts";
import { READ_BACK_FIELDS } from "./read-back-fields.ts";
import { instant } from "./stamps.ts";
import { byCodePoint, strip } from "./text.ts";
import { quoted } from "./yamlio.ts";
export const THREADS = "lodge/threads/";
const HEADING = /^## Message [0-9]+$/u;
const ESCAPE = /(?<=^|\n)\\*## Message [0-9]+(?=\n|$)/gu;
const UNESCAPE = /(?<=^|\n)\\+## Message [0-9]+(?=\n|$)/gu;
export function threadPath(id: string): string {
  return `${THREADS}${id}.md`;
}
export function parseThread(path: string, text: string): Thread | Problem {
  return readWith(path, text, (header, body) => {
    checkKeys(header, ["id", "kind", "about", "raises", "state", "opened"]);
    const id = readId(requireField(header, "id"), "id", "q");
    if (requireField(header, "kind") !== "thread")
      throw new FormatError("kind must be 'thread'", "kind");
    const about = readStr(requireField(header, "about"), "about");
    if (!isId(about) || !["d-", "s-"].includes(about.slice(0, 2)))
      throw new FormatError("about must name a decision or a specification entry", "about");
    const raises = readEnum(Raises, requireField(header, "raises"), "raises");
    const state = readEnum(ThreadState, requireField(header, "state"), "state");
    const opened = readStamp(requireField(header, "opened"), "opened");
    return {
      kind: "thread",
      id,
      about,
      raises,
      state,
      opened,
      messages: messages(body, state, text.split("\n").length - body.split("\n").length),
    };
  });
}
function messages(body: string, state: ThreadState, offset: number): readonly Message[] {
  const lines = body.split("\n"),
    starts = lines.flatMap((line, i) => (HEADING.test(line) ? [i] : []));
  if (!starts.length) throw new FormatError("a thread needs at least one message");
  if (lines.slice(0, starts[0]).some((line) => strip(line)))
    throw new FormatError("text before ## Message 1");
  return starts.map((start, i) => {
    if (lines[start] !== `## Message ${i + 1}`)
      throw new FormatError("messages are numbered 1, 2, 3, in order", null, offset + start + 1);
    return readMessage(
      lines,
      start + 1,
      starts[i + 1] ?? lines.length,
      offset,
      state === ThreadState.CLOSED && i === starts.length - 1,
    );
  });
}
function readMessage(
  lines: string[],
  first: number,
  end: number,
  offset: number,
  closing: boolean,
): Message {
  const heading = first;
  while (first < end && !strip(lines[first] as string)) first++;
  let split = first;
  while (split < end && strip(lines[split] as string)) split++;
  if (first === split) throw new FormatError("a message needs by and when", null, offset + heading);
  const headerText = lines.slice(first, split).join("\n");
  let by: string, when: string, where: string | null;
  try {
    const header = loadHeader(headerText);
    checkKeys(header, ["by", "when", "where"]);
    by = readStr(requireField(header, "by"), "by");
    when = readStr(requireField(header, "when"), "when");
    where = readOptionalStr(header, "where");
    if (by === "author" && where === null)
      throw new FormatError("an author message needs where", "where");
    if (by !== "author") when = readStamp(when, "when");
  } catch (error) {
    if (!(error instanceof FormatError)) throw error;
    const relative = error.key !== null ? keyLine(headerText, error.key) : error.line;
    throw new FormatError(error.message, error.key, offset + first + (relative || 2) - 1);
  }
  const text = trimBlock(lines.slice(split, end).join("\n"));
  if (!text && !closing)
    throw new FormatError("message text must not be empty", null, offset + split + 1);
  return { by, when, where, text: text.replace(UNESCAPE, (m) => m.slice(1)) };
}
function quote(key: string, value: string): string {
  try {
    return quoted(value);
  } catch (error) {
    if (!(error instanceof ValueError)) throw error;
    throw new ValueError(`${key}: ${error.message}`);
  }
}
export function writeThread(thread: Thread): string {
  const header = [
    `id: ${thread.id}`,
    "kind: thread",
    `about: ${thread.about}`,
    `raises: ${thread.raises}`,
    `state: ${thread.state}`,
    `opened: ${thread.opened}`,
  ];
  const blocks = thread.messages.map((m, i) => {
    const by = /^[A-Za-z0-9][A-Za-z0-9._-]*$/u.test(m.by) ? m.by : quote("by", m.by);
    const meta = [`by: ${by}`, `when: ${m.by === "author" ? quote("when", m.when) : m.when}`];
    if (m.where !== null) meta.push(`where: ${quote("where", m.where)}`);
    const text = trimBlock(m.text).replace(ESCAPE, (m) => `\\${m}`);
    return `## Message ${i + 1}\n\n${meta.join("\n")}${text ? `\n\n${text}` : ""}`;
  });
  const text = assemble(header, blocks.join("\n\n")),
    back = parseThread(threadPath(thread.id), text);
  if (back.kind === "problem")
    throw new ValueError(`the thread would not read back: ${back.message}`);
  for (let i = 0; i < Math.min(thread.messages.length, back.messages.length); i++) {
    for (const field of READ_BACK_FIELDS.message)
      if (thread.messages[i]?.[field] !== back.messages[i]?.[field])
        throw new ValueError(`the thread would not read back unchanged: message ${i + 1} ${field}`);
  }
  if (READ_BACK_FIELDS.thread.some((field) => !equal(thread[field], back[field])))
    throw new ValueError("the thread would not read back unchanged: header or messages");
  return text;
}
export function cleanText(text: string): string {
  return strip(text.replaceAll("\r\n", "\n"));
}
export function appended(thread: Thread, message: Message, close = false): Thread {
  if (thread.state === ThreadState.CLOSED) throw new ValueError("the thread is closed");
  const cleaned = { ...message, text: cleanText(message.text) };
  if (!cleaned.text && !close) throw new ValueError("message text must not be empty");
  return {
    ...thread,
    messages: [...thread.messages, cleaned],
    state: close ? ThreadState.CLOSED : ThreadState.OPEN,
  };
}
export function newestLast(threads: Iterable<Thread>): readonly Thread[] {
  return [...threads].sort(
    (a, b) => instant(a.opened) - instant(b.opened) || byCodePoint(a.id, b.id),
  );
}
