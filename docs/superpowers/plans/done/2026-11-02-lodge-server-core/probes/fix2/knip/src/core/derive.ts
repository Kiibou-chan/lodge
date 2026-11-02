export function orderKey(id: string): string {
  return id;
}
export function derive(ids: readonly string[]): string[] {
  return ids.map(orderKey);
}
export function isAuthor(name: string): boolean {
  return name === "author";
}
