import { expect, test } from "bun:test";
import { ceremony } from "./signed.ts";

test("1001 sign-in options retain exactly the newest 1000 challenges", async () => {
  const w = await ceremony();
  try {
    expect((await w.register()).status).toBe(200);
    const challenges: string[] = [];
    for (let i = 0; i < 1001; i++) challenges.push(await w.challenge("sign-in-options"));
    for (const [i, challenge] of challenges.entries()) {
      const response = await w.call("sign-in", { response: await w.a.get(challenge) });
      expect(response.status).toBe(i === 0 ? 401 : 200);
    }
  } finally {
    await w.database.close();
  }
});

test("retained sign-in challenge still expires", async () => {
  const w = await ceremony();
  try {
    await w.register();
    const challenge = await w.challenge("sign-in-options");
    await w.options.clock.sleep(300);
    expect((await w.call("sign-in", { response: await w.a.get(challenge) })).status).toBe(401);
  } finally {
    await w.database.close();
  }
});
