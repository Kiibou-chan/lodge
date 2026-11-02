export const Scope = { PRODUCT: "product", PROCESS: "process" } as const;
export type Scope = (typeof Scope)[keyof typeof Scope];
export const Action = { CREATE: "create", EDIT: "edit", RETIRE: "retire", LINK: "link" } as const;
export type Action = (typeof Action)[keyof typeof Action];
export interface Quote {
  readonly text: string;
  readonly where: string;
  readonly when: string;
}
export interface Change {
  readonly entry: string;
  readonly action: Action;
}
export interface NumberHandle {
  readonly value: string;
  readonly handle: string;
}
export interface Imported {
  readonly file: string;
  readonly heading: string;
}
export interface Decision {
  readonly kind: "decision";
  readonly id: string;
  readonly title: string;
  readonly scope: Scope;
  readonly decidedBy: string;
  readonly date: string;
  readonly statement: string;
  readonly reasoning: string;
  readonly code: string | null;
  readonly changes: readonly Change[];
  readonly replaces: readonly string[];
  readonly narrows: readonly string[];
  readonly confirms: readonly string[];
  readonly workItem: string | null;
  readonly quote: Quote | null;
  readonly numbers: readonly NumberHandle[];
  readonly attachments: readonly string[];
  readonly importedFrom: Imported | null;
}
export function decision(
  value: Omit<
    Decision,
    | "reasoning"
    | "code"
    | "changes"
    | "replaces"
    | "narrows"
    | "confirms"
    | "workItem"
    | "quote"
    | "numbers"
    | "attachments"
    | "importedFrom"
    | "kind"
  > &
    Partial<
      Pick<
        Decision,
        | "reasoning"
        | "code"
        | "changes"
        | "replaces"
        | "narrows"
        | "confirms"
        | "workItem"
        | "quote"
        | "numbers"
        | "attachments"
        | "importedFrom"
        | "kind"
      >
    >,
): Decision {
  return {
    kind: "decision",
    reasoning: "",
    code: null,
    changes: [],
    replaces: [],
    narrows: [],
    confirms: [],
    workItem: null,
    quote: null,
    numbers: [],
    attachments: [],
    importedFrom: null,
    ...value,
  };
}
export interface SpecEntry {
  readonly kind: "spec";
  readonly id: string;
  readonly area: string;
  readonly title: string;
  readonly statement: string;
  readonly code: string | null;
  readonly importedFrom: Imported | null;
  readonly restsOn: readonly string[];
}
export function specEntry(
  value: Omit<SpecEntry, "code" | "importedFrom" | "restsOn" | "kind"> &
    Partial<Pick<SpecEntry, "code" | "importedFrom" | "restsOn" | "kind">>,
): SpecEntry {
  return {
    kind: "spec",
    code: null,
    importedFrom: null,
    restsOn: [],
    ...value,
  };
}
export interface Area {
  readonly kind: "area";
  readonly name: string;
  readonly title: string;
  readonly intro: string;
  readonly order: readonly string[];
  readonly rank: number | null;
}
export function area(
  value: Omit<Area, "rank" | "kind"> & Partial<Pick<Area, "rank" | "kind">>,
): Area {
  return {
    kind: "area",
    rank: null,
    ...value,
  };
}
export interface Problem {
  readonly kind: "problem";
  readonly path: string;
  readonly check: number;
  readonly message: string;
  readonly line: number | null;
}
export function problem(
  value: Omit<Problem, "line" | "kind"> & Partial<Pick<Problem, "line" | "kind">>,
): Problem {
  return {
    kind: "problem",
    line: null,
    ...value,
  };
}
export const Raises = { DOUBT: "doubt", QUESTION: "question" } as const;
export type Raises = (typeof Raises)[keyof typeof Raises];
export const ThreadState = { OPEN: "open", CLOSED: "closed" } as const;
export type ThreadState = (typeof ThreadState)[keyof typeof ThreadState];
export interface Message {
  readonly by: string;
  readonly when: string;
  readonly text: string;
  readonly where: string | null;
}
export function message(value: Omit<Message, "where"> & Partial<Pick<Message, "where">>): Message {
  return {
    where: null,
    ...value,
  };
}
export interface Thread {
  readonly kind: "thread";
  readonly id: string;
  readonly about: string;
  readonly raises: Raises;
  readonly state: ThreadState;
  readonly opened: string;
  readonly messages: readonly Message[];
}
export type Record = Decision | SpecEntry;
