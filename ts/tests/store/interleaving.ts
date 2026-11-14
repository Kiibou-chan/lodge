import { AddOutcome, type Lodge, PublishOutcome, type Store } from "#app";
import type { Tree } from "#core";

class Forwarding implements Store {
  constructor(protected readonly inner: Store) {}
  commit(paths: readonly string[], message: string) {
    return this.inner.commit(paths, message);
  }
  trees() {
    return this.inner.trees();
  }
  attachmentTexts() {
    return this.inner.attachmentTexts();
  }
  freshness() {
    return this.inner.freshness();
  }
  gate(current: Tree) {
    return this.inner.gate(current);
  }
  publish(base: Tree, writes: ReadonlyMap<string, string>, message: string) {
    return this.inner.publish(base, writes, message);
  }
}
export class Interleaved extends Forwarding {
  readonly outcomes: PublishOutcome[] = [];
  private fired = false;
  constructor(
    inner: Store,
    private readonly during: Lodge,
    private readonly drafts: readonly (readonly [string, string])[],
  ) {
    super(inner);
  }
  override async trees(): Promise<readonly [Tree, Tree]> {
    const read = await this.inner.trees();
    if (!this.fired) {
      this.fired = true;
      if ((await this.during.add(this.drafts)).outcome !== AddOutcome.PUBLISHED)
        throw new Error("the interleaved add did not publish");
    }
    return read;
  }
  override async publish(base: Tree, writes: ReadonlyMap<string, string>, message: string) {
    const outcome = await this.inner.publish(base, writes, message);
    this.outcomes.push(outcome);
    return outcome;
  }
}
export class Interleaving extends Forwarding {
  attempts = 0;
  readonly publishes: (readonly [ReadonlyMap<string, string>, string])[] = [];
  private readonly rejections: ReadonlyMap<string, string>[] = [];
  private readonly moves: ReadonlyMap<string, string>[] = [];
  rejectNext(...changes: ReadonlyMap<string, string>[]): void {
    this.rejections.push(...changes);
  }
  movesAfterRead(change: ReadonlyMap<string, string>): void {
    this.moves.push(change);
  }
  async files(): Promise<ReadonlyMap<string, string>> {
    const [current] = await this.inner.trees();
    return new Map([...current.files, ...(await this.inner.attachmentTexts())]);
  }
  private async land(change: ReadonlyMap<string, string>): Promise<void> {
    const [base] = await this.inner.trees();
    if ((await this.inner.publish(base, change, "interleaving")) !== PublishOutcome.PUBLISHED)
      throw new Error("the interleaved change did not publish");
  }
  override async trees(): Promise<readonly [Tree, Tree]> {
    const read = await this.inner.trees();
    const move = this.moves.shift();
    if (move !== undefined) await this.land(move);
    return read;
  }
  override async publish(base: Tree, writes: ReadonlyMap<string, string>, message: string) {
    this.attempts += 1;
    const change = this.rejections.shift();
    if (change !== undefined) await this.land(change);
    const outcome = await this.inner.publish(base, writes, message);
    if (outcome === PublishOutcome.PUBLISHED) this.publishes.push([new Map(writes), message]);
    return outcome;
  }
}
