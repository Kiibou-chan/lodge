import { test } from "node:test";
import assert from "node:assert/strict";
import { DatabaseSync } from "node:sqlite";
test("node sqlite", () => { const d = new DatabaseSync(":memory:"); d.exec("create table t(a)"); d.prepare("insert into t values (?)").run(1); assert.deepEqual(d.prepare("select a from t").all(), [{ a: 1 }]); });
