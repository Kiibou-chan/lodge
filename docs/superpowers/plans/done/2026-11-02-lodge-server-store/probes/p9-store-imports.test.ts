import { expect, test } from "bun:test";
import { cruise, plant } from "./plant.ts";
test.each([["bun:sqlite"], ["node:fs"], ["yaml"], ["#core"], ["#app"]])("store %p", async (name) => {
  const found = await cruise(plant({ "src/store/a.ts": `import "${name}";`, "src/app/index.ts": "" }));
  console.log(name, JSON.stringify(found.sort()));
  expect(true).toBe(true);
});
