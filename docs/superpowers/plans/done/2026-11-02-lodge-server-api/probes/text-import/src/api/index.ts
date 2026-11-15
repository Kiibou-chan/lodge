import bundle from "./page.html" with { type: "text" };
import script from "./page.js" with { type: "text" };

const page = bundle as unknown as string;

export function asset(path: string): string | null {
  if (path === "/") return page;
  if (path === "/page.js") return script;
  return null;
}
