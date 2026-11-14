import {
  type Clock,
  CommitOutcome,
  type Committed,
  committed,
  type Gate,
  gate,
  type Held,
  type HeldDraft,
  type IdSource,
  NotFound,
  type Now,
  PublishOutcome,
  type Store,
  stampOf,
} from "#app";
import {
  type Area,
  ATTACHMENTS,
  type Decision,
  instant,
  type SpecEntry,
  type Tree,
  tree,
} from "#core";
import { filesOf } from "../core/builders.ts";

export const START: Now = { epochMs: instant("2026-10-29T09:30:00+01:00"), offsetMinutes: 60 };

// movesAfterRead and rejectNext land another session’s change before publication.
export class MemoryStore implements Store {
  files: Map<string, string>;
  published: Map<string, string>;
  staged: boolean;
  people: ReadonlySet<string>;
  rev = 0;
  declined: [number, string][] = [];
  private holds = new Map<number, Held>();
  commits: [readonly string[], string][] = [];
  commitResult: Committed = committed({ outcome: CommitOutcome.COMMITTED });
  stamp: string | null = "fetched 2026-10-29T08:00:00+00:00";
  publishes: [Map<string, string>, string][] = [];
  attempts = 0;
  gateFor: Gate | null = null;
  private moves: ReadonlyMap<string, string>[] = [];
  private rejections: ReadonlyMap<string, string>[] = [];

  constructor(
    items: (Area | Decision | SpecEntry)[] = [],
    options: { staged?: boolean; people?: ReadonlySet<string> } = {},
  ) {
    this.people = options.people ?? new Set(["author"]);
    this.files = filesOf(...items);
    this.published = new Map(this.files);
    this.staged = options.staged ?? false;
  }
  async hold(draft: HeldDraft): Promise<number> {
    const seq = ++this.rev;
    this.holds.set(seq, structuredClone({ ...draft, seq, at: stampOf(START) }));
    return seq;
  }
  async held(): Promise<readonly Held[]> {
    return structuredClone([...this.holds.values()]);
  }
  async decline(seq: number, reason: string): Promise<void> {
    if (!this.holds.delete(seq)) throw new NotFound(`nothing is held under number ${seq}`);
    this.declined.push([seq, reason]);
    this.rev += 1;
  }
  async commit(paths: readonly string[], message: string): Promise<Committed> {
    this.commits.push([[...paths], message]);
    return this.commitResult;
  }
  async trees(): Promise<readonly [Tree, Tree]> {
    const current = tree({
      rev: String(this.rev),
      files: new Map(this.files),
      people: this.people,
    });
    const published = this.staged
      ? tree({ rev: String(this.rev), files: new Map(this.published), people: this.people })
      : current;
    const move = this.moves.shift();
    if (move !== undefined) this.land(move);
    return [current, published];
  }
  async attachmentTexts(): Promise<ReadonlyMap<string, string>> {
    return new Map([...this.files].filter(([path]) => path.startsWith(ATTACHMENTS)));
  }
  async freshness(): Promise<string | null> {
    return this.stamp;
  }
  async gate(current: Tree): Promise<Gate> {
    if (this.gateFor !== null) return this.gateFor;
    const published = this.staged
      ? tree({ rev: String(this.rev), files: new Map(this.published), people: this.people })
      : current;
    return gate({ published, checked: [["", current]] });
  }
  async publish(
    base: Tree,
    writes: ReadonlyMap<string, string>,
    message: string,
    approves: number | null = null,
  ): Promise<PublishOutcome> {
    this.attempts += 1;
    const rejection = this.rejections.shift();
    if (rejection !== undefined) {
      this.land(rejection);
      return PublishOutcome.REJECTED;
    }
    if (base.rev !== String(this.rev)) return PublishOutcome.REJECTED;
    if (approves !== null && !this.holds.has(approves)) return PublishOutcome.REJECTED;
    this.publishes.push([new Map(writes), message]);
    this.land(writes);
    if (approves !== null) {
      this.holds.delete(approves);
      this.rev += 1;
    }
    return this.staged ? PublishOutcome.STAGED : PublishOutcome.PUBLISHED;
  }
  movesAfterRead(change: ReadonlyMap<string, string>): void {
    this.moves.push(change);
  }
  rejectNext(...changes: ReadonlyMap<string, string>[]): void {
    this.rejections.push(...changes);
  }
  private land(change: ReadonlyMap<string, string>): void {
    for (const [path, text] of change) this.files.set(path, text);
    this.rev += 1;
    if (!this.staged) this.published = new Map(this.files);
  }
}
export class FixedClock implements Clock {
  calls = 0;
  slept: number[] = [];
  constructor(
    public start: Now = START,
    public stepMs = 0,
  ) {}
  now(): Now {
    this.calls += 1;
    return { ...this.start, epochMs: this.start.epochMs + this.stepMs * (this.calls - 1) };
  }
  async sleep(seconds: number): Promise<void> {
    this.slept.push(seconds);
    this.start = { ...this.start, epochMs: this.start.epochMs + seconds * 1000 };
  }
}
export class CountingIds implements IdSource {
  draws = 0;
  next: number;
  constructor(
    first = 1,
    public step = 1,
  ) {
    this.next = first;
  }
  entropy(): Uint8Array {
    this.draws += 1;
    const value = this.next;
    this.next += this.step;
    if (!Number.isInteger(value) || value < 0 || value > 255)
      throw new RangeError("byte must be in range(0, 256)");
    return new Uint8Array(6).fill(value);
  }
}
