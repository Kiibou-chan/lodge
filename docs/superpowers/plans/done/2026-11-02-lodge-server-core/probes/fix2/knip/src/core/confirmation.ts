import { orderKey } from "./derive.ts";
export function confirmableIds(ids: readonly string[]): string[] {
  return ids.map(orderKey);
}
