import type { CoreSettings, Filters, Raises } from "#core";
import type { Clock, IdSource, Store } from "./ports.ts";
import * as reads from "./reads.ts";
import type { Added } from "./results.ts";
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
  async search(query: string, filters: Filters, { limit = 20 } = {}) {
    return reads.searchRecords(this.wiring, query, filters, limit);
  }
  async show(ref: string, { reasoning = false, provenance = false } = {}) {
    return reads.show(this.wiring, ref, reasoning, provenance);
  }
  async waitingAll() {
    return reads.waitingAll(this.wiring);
  }
  async timeline({ limit = 50 } = {}) {
    return reads.timeline(this.wiring, limit);
  }
  async spec({ area = null }: { area?: string | null } = {}) {
    return reads.spec(this.wiring, area);
  }
  async problems() {
    return this.check(false);
  }
  async check(gate: boolean) {
    return reads.check(this.wiring, gate);
  }
  async draft(ref: string) {
    return reads.draft(this.wiring, ref);
  }
  async ask(
    ref: string,
    raises: Raises,
    by: string,
    text: string,
    options: threads.MessageOptions = {},
  ) {
    return threads.writeMessage(this.wiring, ref, raises, by, text, options);
  }
  async reply(ref: string, by: string, text: string, options: threads.MessageOptions = {}) {
    return threads.writeMessage(this.wiring, ref, null, by, text, options);
  }
  async close(
    ref: string,
    by: string,
    { text = null, ...options }: threads.MessageOptions & { text?: string | null } = {},
  ) {
    return threads.writeMessage(this.wiring, ref, null, by, text ?? "", options, true);
  }
  async threads() {
    return threads.listOpen(this.wiring);
  }
  async thread(ref: string) {
    return threads.show(this.wiring, ref);
  }
  async threadsWaiting() {
    return threads.waiting(this.wiring);
  }
}
