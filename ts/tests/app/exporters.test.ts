import { expect, test } from "bun:test";
import {
  type Clock,
  EXPORT_INTERVAL_SECONDS,
  Exporters,
  type ExportOutcome,
  type ExportPorts,
  type ExportTarget,
  type ExportTargets,
  exportFiles,
  exportMessage,
  person,
} from "#app";
import { FixedClock, MemoryStore } from "./fakes.ts";

function world(clock: Clock = new FixedClock()) {
  const target: ExportTarget = {
    repository: "/synthetic/repository",
    branch: "records",
    remote: null,
  };
  const targetsMap = new Map([
    ["storage", target],
    ["logs", target],
  ]);
  const targets: ExportTargets = {
    async target(project) {
      return targetsMap.get(project) ?? null;
    },
    async setTarget(project, value, _by) {
      if (value) targetsMap.set(project, value);
      else targetsMap.delete(project);
    },
  };
  const store = new MemoryStore();
  const calls: Parameters<ExportPorts["write"]>[] = [];
  const failures: [string, unknown][] = [];
  const outcomes: (ExportOutcome | Error)[] = [];
  const ports: ExportPorts = {
    clock,
    targets,
    storeFor: () => store,
    async write(...args): Promise<ExportOutcome> {
      calls.push(args);
      const outcome = outcomes.shift() ?? { kind: "committed", commit: String(calls.length) };
      if (outcome instanceof Error) throw outcome;
      return outcome;
    },
    failed: (project, error) => {
      failures.push([project, error]);
    },
  };
  return { exporter: new Exporters(ports), store, calls, failures, outcomes, targets, target };
}

test("first_write_exports_at_once", async () => {
  const clock = new FixedClock();
  const w = world(clock);
  const files = new Map([["lodge/attachments/d-123456/data.csv", "raw\udcff"]]);
  await w.store.publish((await w.store.trees())[0], files, "attachment");
  await w.exporter.written("storage");
  const expected = exportFiles((await w.store.trees())[0], await w.store.attachmentTexts());
  expect(w.calls).toEqual([[w.target, expected, exportMessage(expected)]]);
  expect(clock.slept).toEqual([]);
  expect(EXPORT_INTERVAL_SECONDS).toBe(60);
  await w.exporter.settled();
});

class HeldClock extends FixedClock {
  release: () => void = () => {
    throw new Error("no sleep pending");
  };
  sleeping: Promise<void>;
  private signal: () => void = () => {};
  constructor() {
    super();
    this.sleeping = new Promise((resolve) => {
      this.signal = resolve;
    });
  }
  override async sleep(seconds: number): Promise<void> {
    this.slept.push(seconds);
    await new Promise<void>((resolve) => {
      this.release = resolve;
      this.signal();
    });
    this.start = { ...this.start, epochMs: this.start.epochMs + seconds * 1000 };
  }
}

test("writes_within_a_minute_share_one_commit", async () => {
  const clock = new HeldClock();
  const w = world(clock);
  await w.exporter.written("storage");
  clock.start = { ...clock.start, epochMs: clock.start.epochMs + 10000 };
  let ended = false;
  const second = w.exporter.written("storage").then(() => {
    ended = true;
  });
  await clock.sleeping;
  const third = w.exporter.written("storage");
  const fourth = w.exporter.written("storage");
  await w.store.publish(
    (await w.store.trees())[0],
    new Map([["lodge/attachments/d-123456/latest.csv", "latest"]]),
    "latest",
  );
  expect(w.calls.length).toBe(1);
  expect(ended).toBe(false);
  let settled = false;
  const settling = w.exporter.settled().then(() => {
    settled = true;
  });
  await Promise.resolve();
  expect(settled).toBe(false);
  clock.release();
  await Promise.all([second, third, fourth, settling]);
  expect(w.calls.length).toBe(2);
  expect(w.calls[1]?.[1].get("lodge/attachments/d-123456/latest.csv")).toBe("latest");
  expect(clock.slept).toEqual([50]);
});

test("write_a_minute_after_exports_at_once", async () => {
  const clock = new FixedClock();
  const w = world(clock);
  await w.exporter.written("storage");
  clock.start = { ...clock.start, epochMs: clock.start.epochMs + 60000 };
  await w.exporter.written("storage");
  expect(w.calls.length).toBe(2);
  expect(clock.slept).toEqual([]);
});

test("no_target_writes_nothing", async () => {
  const w = world();
  await w.exporter.written("unknown");
  expect(w.calls).toEqual([]);
});

test("unchanged_counts_no_commit", async () => {
  const clock = new FixedClock();
  const w = world(clock);
  w.outcomes.push({ kind: "unchanged" });
  await w.exporter.written("storage");
  await w.exporter.written("storage");
  expect(w.calls.length).toBe(2);
  expect(clock.slept).toEqual([]);
});

test("moved_retries_a_minute_later", async () => {
  const clock = new FixedClock();
  const w = world(clock);
  w.outcomes.push({ kind: "moved" });
  await w.exporter.written("storage");
  expect(w.calls.length).toBe(2);
  expect(clock.slept).toEqual([60]);
  expect(w.failures).toEqual([]);
});

test("failure_is_reported_and_retried", async () => {
  const clock = new FixedClock();
  const w = world(clock);
  const error = new Error("boom");
  w.outcomes.push(error);
  await w.exporter.written("storage");
  expect(w.failures).toEqual([["storage", error]]);
  expect(clock.slept).toEqual([60]);
  expect(w.calls.length).toBe(2);
});

test("projects_batch_apart", async () => {
  const clock = new FixedClock();
  const w = world(clock);
  await Promise.all([w.exporter.written("storage"), w.exporter.written("logs")]);
  expect(w.calls.length).toBe(2);
  expect(clock.slept).toEqual([]);
});

test("start_exports_projects_with_a_target", async () => {
  const w = world();
  await w.targets.setTarget("logs", null, person("ana"));
  await w.exporter.start(["storage", "logs", "unknown"]);
  expect(w.calls.length).toBe(1);
  await w.exporter.settled();
});
