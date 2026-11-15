export class CliError extends Error {
  override name = "CliError";
  constructor(
    message: string,
    readonly exitCode: 1 | 2 = 2,
  ) {
    super(message);
  }
}
