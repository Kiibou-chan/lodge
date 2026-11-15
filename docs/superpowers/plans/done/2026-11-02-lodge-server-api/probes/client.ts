const url = process.argv[2]!;
const r = await fetch(`${url}/api/v1/echo`, { method: "POST", headers: { "content-type": "application/json", authorization: "Bearer t" }, body: JSON.stringify({ a: "é\u{1F600}" }) });
console.log(r.status, r.headers.get("lodge-version"), await r.text());
