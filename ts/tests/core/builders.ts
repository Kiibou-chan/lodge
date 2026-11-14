import {
  type Area,
  areaPath,
  type Decision,
  type Message,
  area as makeArea,
  decision as makeDecision,
  message as makeMessage,
  newRecordPath,
  type Problem,
  Raises,
  type Record,
  Scope,
  type Snapshot,
  type SpecEntry,
  specEntry,
  type Thread,
  ThreadState,
  threadPath,
  tree,
  writeArea,
  writeRecord,
  writeThread,
} from "#core";

let numbers = 0;
const ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz";
function nextId(prefix: string): string {
  const n = ++numbers;
  return `${prefix}-${ALPHABET[Math.floor(n / 1024) % 32]}${ALPHABET[Math.floor(n / 32) % 32]}${ALPHABET[n % 32]}000`;
}
export function at(minute: number): string {
  return `2026-10-28T${String(10 + Math.floor(minute / 60)).padStart(2, "0")}:${String(minute % 60).padStart(2, "0")}:00+01:00`;
}
export function decision(kw: Partial<Decision> = {}): Decision {
  const value = {
    id: nextId("d"),
    title: "A decision",
    scope: Scope.PRODUCT,
    decidedBy: "coordinator",
    date: at(0),
    statement: "A statement.",
    ...kw,
  };
  return makeDecision({
    ...value,
    ...(value.decidedBy === "author" && !("quote" in kw) && !("importedFrom" in kw)
      ? { quote: { text: "Do it.", where: "a session", when: "2026-10-28 10:00" } }
      : {}),
  });
}
export function entry(kw: Partial<SpecEntry> = {}): SpecEntry {
  return specEntry({
    id: nextId("s"),
    area: "storage",
    title: "An entry",
    statement: "What holds now.",
    ...kw,
  });
}
export function area(kw: Partial<Area> = {}): Area {
  return makeArea({ name: "storage", title: "Storage", intro: "", order: [], ...kw });
}
export function message(kw: Partial<Message> = {}): Message {
  return makeMessage({ by: "coordinator", when: at(0), text: "A message.", ...kw });
}
export function thread(kw: Partial<Thread> = {}): Thread {
  return {
    kind: "thread",
    id: nextId("q"),
    about: "s-aaaaaa",
    raises: Raises.DOUBT,
    state: ThreadState.OPEN,
    opened: at(0),
    messages: [message()],
    ...kw,
  };
}
type Item = Record | Area | Thread;
export function filesOf(...items: Item[]): Map<string, string> {
  return new Map(
    items.map((i) =>
      i.kind === "thread"
        ? [threadPath(i.id), writeThread(i)]
        : i.kind === "area"
          ? [areaPath(i.name), writeArea(i)]
          : [newRecordPath(i), writeRecord(i)],
    ),
  );
}
// Keeps items as given, without parsing, so tests can construct defects no store could hold.
export function snapshotOf(
  items: readonly Item[],
  options: {
    attachments?: readonly string[];
    paths?: ReadonlyMap<string, string> | null;
    problems?: readonly Problem[];
  } = {},
): Snapshot {
  return {
    decisions: new Map(items.filter((i) => i.kind === "decision").map((i) => [i.id, i])),
    entries: new Map(items.filter((i) => i.kind === "spec").map((i) => [i.id, i])),
    areas: new Map(items.filter((i) => i.kind === "area").map((i) => [i.name, i])),
    threads: new Map(items.filter((i) => i.kind === "thread").map((i) => [i.id, i])),
    paths: new Map([
      ...items.flatMap((i) =>
        i.kind === "area"
          ? []
          : [[i.id, i.kind === "thread" ? threadPath(i.id) : newRecordPath(i)] as const],
      ),
      ...(options.paths ?? []),
    ]),
    problems: options.problems ?? [],
    attachments: new Set(options.attachments ?? []),
  };
}
export function treeOf(...items: Item[]) {
  return tree({ rev: null, files: filesOf(...items) });
}
