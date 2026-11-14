export const AUTHOR_ONLY: ReadonlySet<string> = new Set(["author"]);

export function roleWords(by: string, people: ReadonlySet<string>): string {
  return `decided_by is ${by}; ${people.has("author") ? "write author" : "name a person of the project"} exactly, with a quote, or use your own role`;
}
export function quoteWords(person: string): string {
  return `decided_by is ${person}, but there is no quote; add quote: {text, where, when} with ${person === "author" ? "the author's" : `${person}'s`} words, or record it under your own role`;
}
export function confirmsWords(by: string, people: ReadonlySet<string>): string {
  return `confirms is for ${people.has("author") ? "author decisions" : "a person's decisions"}, but decided_by is ${by}`;
}
export function reasoningWords(person: string | null): string {
  return person === null
    ? "agent decision"
    : person === "author"
      ? "author decision"
      : `decision of ${person}`;
}
export function messageWords(person: string): string {
  return person === "author"
    ? "an author message needs where"
    : `a message by ${person} needs where`;
}
export function confirmationWords(person: string): string {
  return person === "author" ? "The author" : person;
}
