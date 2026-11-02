const empty = process.argv[2];
for (const PATH of ["", empty]) {
  try {
    const r = Bun.spawnSync(["git", "--version"], { env: { ...process.env, PATH }, stdin: "ignore", stdout: "pipe", stderr: "pipe" });
    console.log(JSON.stringify(PATH), "exit", r.exitCode, r.stdout.toString().trim());
  } catch (e) { const x = e as NodeJS.ErrnoException; console.log(JSON.stringify(PATH), "threw", x.code, x.message); }
}
const r = Bun.spawnSync(["git", "hash-object", "--stdin"], { stdin: new TextEncoder().encode("a\n"), env: { ...process.env, LC_ALL: "C" } });
console.log("hash", r.stdout.toString().trim());
const s = Bun.spawnSync(["sh", "-c", "ls -l /proc/self/fd/0 /proc/self/fd/1 /proc/self/fd/2"], { stdin: new TextEncoder().encode("x"), stdout: "pipe", stderr: "pipe" });
console.log(s.stdout.toString().replace(/.*-> /gm, "").trim());
