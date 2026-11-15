import type { Listed, ThreadShown, ThreadsWaiting } from "#app";
import { formatLevel1, type Thread } from "#core";
import { readLines } from "./output.ts";
export function threadHead(t: Thread, title: string | null | undefined): string {
  const n = t.messages.length;
  return `${t.id} · ${t.state} · ${t.raises} · about ${t.about} · ${n} message${n !== 1 ? "s" : ""} · last by ${t.messages[n - 1]?.by}\n${title ?? `about ${t.about}, not found`}`;
}
export function threadText(shown: ThreadShown): string {
  const t = shown.thread;
  const messages = t.messages.map((message, index) => {
    const prefix = t.state === "closed" && index === t.messages.length - 1 ? "closed by " : "";
    let head = `${prefix}${message.by} · ${message.when}`;
    if (message.where !== null) head += ` · ${message.where}`;
    return head + (message.text ? `\n${message.text}` : "");
  });
  return [
    ...readLines(shown.read),
    `${threadHead(t, shown.about?.title)}\n\n${messages.join("\n\n")}`,
  ].join("\n");
}
export function waitingText(listed: Listed, waiting: ThreadsWaiting): string {
  const agents = waiting.forAgent.map((t) => threadHead(t, waiting.titles.get(t.about)));
  const author = [
    ...listed.items.map(formatLevel1),
    ...waiting.forAuthor.map((t) => threadHead(t, waiting.titles.get(t.about))),
  ];
  return [
    ...readLines(listed.read),
    "waiting for an agent",
    agents.join("\n\n") || "nothing",
    "",
    "waiting for the author",
    author.join("\n\n") || "nothing",
  ].join("\n");
}
