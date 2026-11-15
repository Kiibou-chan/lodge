import { Database } from "bun:sqlite";
const db = new Database(":memory:");
db.run("create table t (text text not null)");
const lone = "a\udcffb";
db.query("insert into t values (?)").run(lone);
const back = (db.query("select text from t").get() as { text: string }).text;
console.log(`lone surrogate in: U+${lone.charCodeAt(1).toString(16)}; read back: ${[...back].map((c) => `U+${c.codePointAt(0)?.toString(16)}`).join(" ")}; same ${back === lone}`);
