import bundle from "./page.html" with { type: "text" };
// @ts-expect-error TypeScript resolves ./page.js to page.ts, which has the same stem.
import script from "./page.js" with { type: "text" };

const PAGE = bundle as unknown as string;
const SCRIPT: string = script;

export { PAGE, SCRIPT };
