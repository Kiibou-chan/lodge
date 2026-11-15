const s = Bun.serve({ hostname: "127.0.0.1", port: 0, fetch: async (req) => new Response(JSON.stringify(await req.json()), { headers: { "lodge-version": "0.3.0" } }) });
const p = Bun.spawn(["./client-bin", `http://127.0.0.1:${s.port}`], { env: { PATH: "/usr/bin:/bin" }, stdout: "pipe" });
console.log("async spawn:", await p.exited, (await new Response(p.stdout).text()).trim());
s.stop(true);
