import type { CheckResult, CoreSettings, Filters, Raises, SpecArea } from "#core";
import type { Clock, IdSource, Store } from "./ports.ts";
import * as reads from "./reads.ts";
import type {
  Added,
  Listed,
  Read,
  Shown,
  ThreadList,
  ThreadShown,
  ThreadsWaiting,
  Written,
} from "./results.ts";
import type { Wiring } from "./state.ts";
import * as threads from "./threads.ts";
import { type AddOptions, add, mint } from "./writes.ts";

export class Lodge {
  private readonly wiring: Wiring;
  constructor(store: Store, clock: Clock, ids: IdSource, settings: CoreSettings) {
    this.wiring = { store, clock, ids, settings };
  }
  async mint(prefix: "d" | "s"): Promise<string> {
    return mint(this.wiring, prefix);
  }
  async add(
    drafts: readonly (readonly [string, string])[],
    options: AddOptions = {},
  ): Promise<Added> {
    return add(this.wiring, drafts, options);
  }
  async search(query: string, filters: Filters, { limit = 20 } = {}): Promise<Listed> {
    return reads.searchRecords(this.wiring, query, filters, limit);
  }
  async show(ref: string, { reasoning = false, provenance = false } = {}): Promise<Shown> {
    return reads.show(this.wiring, ref, reasoning, provenance);
  }
  async waitingAll(): Promise<readonly [Listed, ThreadsWaiting]> {
    return reads.waitingAll(this.wiring);
  }
  async timeline({ limit = 50 } = {}): Promise<Listed> {
    return reads.timeline(this.wiring, limit);
  }
  async spec({
    area = null,
  }: {
    area?: string | null;
  } = {}): Promise<readonly [string, Read, readonly SpecArea[]]> {
    return reads.spec(this.wiring, area);
  }
  async problems(): Promise<readonly [CheckResult, Read]> {
    return this.check(false);
  }
  async check(gate: boolean): Promise<readonly [CheckResult, Read]> {
    return reads.check(this.wiring, gate);
  }
  async draft(ref: string): Promise<string> {
    return reads.draft(this.wiring, ref);
  }
  async ask(
    ref: string,
    raises: Raises,
    by: string,
    text: string,
    options: threads.MessageOptions = {},
  ): Promise<Written> {
    return threads.writeMessage(this.wiring, ref, raises, by, text, options);
  }
  async reply(
    thread: string,
    by: string,
    text: string,
    options: threads.MessageOptions = {},
  ): Promise<Written> {
    return threads.writeMessage(this.wiring, thread, null, by, text, options);
  }
  async close(
    thread: string,
    by: string,
    { text = null, ...options }: threads.MessageOptions & { text?: string | null } = {},
  ): Promise<Written> {
    return threads.writeMessage(this.wiring, thread, null, by, text ?? "", {
      ...options,
      close: true,
    });
  }
  async threads(): Promise<ThreadList> {
    return threads.listOpen(this.wiring);
  }
  async thread(ref: string): Promise<ThreadShown> {
    return threads.show(this.wiring, ref);
  }
  async threadsWaiting(): Promise<ThreadsWaiting> {
    return threads.waiting(this.wiring);
  }
}
