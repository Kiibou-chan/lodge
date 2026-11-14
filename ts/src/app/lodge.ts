import type { CoreSettings } from "#core";
import type { Clock, IdSource, Store } from "./ports.ts";
import type { Wiring } from "./state.ts";
import { type AddOptions, add, mint } from "./writes.ts";

export class Lodge {
  private readonly wiring: Wiring;
  constructor(store: Store, clock: Clock, ids: IdSource, settings: CoreSettings) {
    this.wiring = { store, clock, ids, settings };
  }
  async mint(prefix: "d" | "s"): Promise<string> {
    return mint(this.wiring, prefix);
  }
  async add(drafts: readonly (readonly [string, string])[], options: AddOptions = {}) {
    return add(this.wiring, drafts, options);
  }
}
