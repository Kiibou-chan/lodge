import { pyRepr } from "#core";

interface Argument {
  readonly name: string;
  readonly options: readonly string[];
  readonly metavar: string;
  readonly nargs: string | number | null;
  readonly required: boolean;
  readonly choices: readonly string[] | null;
  readonly default: unknown;
  readonly convert?: (text: string) => unknown;
}
export interface Declaration {
  readonly usage: string;
  readonly help: string;
  readonly actions: readonly Argument[];
}
export interface Exit {
  readonly kind: "exit";
  readonly code: number;
  readonly out: string;
  readonly err: string;
}
const TOP_USAGE = "usage: lodge [-h] [--version] COMMAND ...\n";
export function exit(code: number, out = "", err = ""): Exit {
  return { kind: "exit", code, out, err };
}
export function usageError(message: string, name = "", usage = TOP_USAGE): Exit {
  return exit(2, "", `${usage}lodge${name ? ` ${name}` : ""}: error: ${message}\n`);
}

export function positive(text: string): number {
  if (!/^[0-9]+$/u.test(text) || Number(text) < 1)
    throw new Error(`${pyRepr(text)} is not a positive whole number`);
  return Number(text);
}

export function argumentsOf(
  argv: readonly string[],
  name: string,
  decl: Declaration,
  leadingExtras: readonly string[] = [],
): { readonly kind: "arguments"; readonly values: Record<string, unknown> } | Exit {
  const values: Record<string, unknown> = {};
  const seen = new Set<string>();
  const positional = decl.actions.filter((a) => !a.options.length);
  const options = decl.actions.filter((a) => a.options.length);
  for (const a of decl.actions) values[a.name] = Array.isArray(a.default) ? [] : a.default;
  const words: { readonly word: string; readonly index: number }[] = [];
  const extras: { readonly word: string; readonly index: number }[] = [];
  let ended = false;
  const error = (message: string) => usageError(message, name, decl.usage);
  const looksOption = (word: string) =>
    word.startsWith("-") && word !== "-" && !/^-(?:\d+|\d*\.\d+)$/u.test(word);
  function assign(a: Argument, value: string, label: string): Exit | null {
    if (a.choices && !a.choices.includes(value))
      return error(
        `argument ${label}: invalid choice: ${pyRepr(value)} (choose from ${a.choices.join(", ")})`,
      );
    if (a.convert) {
      try {
        values[a.name] = a.convert(value);
      } catch (error) {
        if (!(error instanceof Error)) throw error;
        return usageError(`argument ${label}: ${error.message}`, name, decl.usage);
      }
    } else if (a.nargs === "+" || Array.isArray(a.default)) {
      const prior = values[a.name];
      values[a.name] = [...(Array.isArray(prior) ? prior : []), value];
    } else values[a.name] = value;
    seen.add(a.name);
    return null;
  }
  let positionalIndex = 0;
  function consumeWords(): Exit | null {
    let position = 0;
    while (position < words.length && positionalIndex < positional.length) {
      const a = positional[positionalIndex++];
      if (!a) break;
      const take = a.nargs === "+" ? words.length - position : 1;
      for (let n = 0; n < take; n++) {
        const failed = assign(a, words[position++]?.word ?? "", a.metavar);
        if (failed) return failed;
      }
    }
    extras.push(...words.slice(position));
    words.length = 0;
    return null;
  }
  for (let i = 0; i < argv.length; i++) {
    const word = argv[i] ?? "";
    if (!ended && word === "--") {
      if (
        positionalIndex >= positional.length ||
        (positional.slice(positionalIndex).every((a) => a.nargs !== "+") &&
          words.length > positional.length - positionalIndex)
      )
        extras.push({ word, index: i });
      ended = true;
      continue;
    }
    if (!ended && looksOption(word)) {
      const failedWords = consumeWords();
      if (failedWords) return failedWords;
      const at = word.indexOf("=");
      const key = at < 0 ? word : word.slice(0, at);
      if (key === "-h" || (key.startsWith("--") && "--help".startsWith(key))) {
        if (at >= 0)
          return error(
            `argument -h/--help: ignored explicit argument ${pyRepr(word.slice(at + 1))}`,
          );
        return exit(0, decl.help);
      }
      const exact = options.filter((a) => a.options.includes(key));
      const matches = exact.length
        ? exact
        : options.filter((a) => key.startsWith("--") && a.options.some((o) => o.startsWith(key)));
      if (matches.length > 1)
        return error(
          `ambiguous option: ${key} could match ${matches.flatMap((a) => a.options).join(", ")}`,
        );
      const a = matches[0];
      if (!a) {
        extras.push({ word, index: i });
        continue;
      }
      if (a.nargs === 0) {
        if (at >= 0)
          return error(
            `argument ${a.options[0]}: ignored explicit argument ${pyRepr(word.slice(at + 1))}`,
          );
        values[a.name] = true;
        seen.add(a.name);
        continue;
      }
      const value = at >= 0 ? word.slice(at + 1) : argv[i + 1];
      if (value === undefined || (at < 0 && looksOption(value)))
        return error(`argument ${a.options[0]}: expected one argument`);
      if (at < 0) i++;
      const failed = assign(a, value, a.options[0] ?? key);
      if (failed) return failed;
    } else words.push({ word, index: i });
  }
  const failed = consumeWords();
  if (failed) return failed;
  const missing = decl.actions
    .filter((a) => a.required && !seen.has(a.name))
    .map((a) => a.options[0] ?? a.metavar);
  if (missing.length) return error(`the following arguments are required: ${missing.join(", ")}`);
  const leftover = [
    ...leadingExtras,
    ...extras.sort((a, b) => a.index - b.index).map((a) => a.word),
  ];
  if (leftover.length) return usageError(`unrecognized arguments: ${leftover.join(" ")}`);
  return { kind: "arguments", values };
}
