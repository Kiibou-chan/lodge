import { type CoreSettings, parseCoreSettings, SettingsError } from "#core";

export class LodgeError extends Error {
  readonly exitCode: number = 2;
  constructor(message: string, options?: ErrorOptions) {
    super(message, options);
    this.name = new.target.name;
  }
}
export class NotFound extends LodgeError {}
export class Conflict extends LodgeError {
  override readonly exitCode: number = 1;
}
export class StaleList extends Conflict {}
export function coreSettings(table: Readonly<Record<string, unknown>>): CoreSettings {
  try {
    return parseCoreSettings(table);
  } catch (error) {
    if (!(error instanceof SettingsError)) throw error;
    throw new LodgeError(`.lodge.toml: ${error.message}`, { cause: error });
  }
}
