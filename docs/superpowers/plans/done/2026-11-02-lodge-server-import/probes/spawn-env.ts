process.env.FOO_PROBE = "mutated";
const a = Bun.spawnSync(["sh", "-c", "echo [$FOO_PROBE]"]);
const b = Bun.spawnSync(["sh", "-c", "echo [$FOO_PROBE]"], { env: { ...process.env } });
console.log("no env:", a.stdout.toString().trim(), "explicit env:", b.stdout.toString().trim());
