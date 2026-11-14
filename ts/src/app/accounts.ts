export interface ServerSetup {
  readonly origin: string;
  readonly person: string;
  readonly at: string;
}
export interface Passkey {
  readonly id: string;
  readonly publicKey: string;
  readonly counter: number;
  readonly transports: readonly string[];
  readonly created: string;
}
export interface AgentToken {
  readonly id: string;
  readonly project: string;
  readonly role: string | null;
  readonly label: string;
  readonly issued: string;
  readonly revoked: string | null;
}
export interface Accounts {
  setup(): Promise<ServerSetup | null>;
  setUp(setup: ServerSetup): Promise<void>;
  issueSetupCode(hash: string, expires: string): Promise<void>;
  setupCodeValid(hash: string): Promise<boolean>;
  spendSetupCode(hash: string): Promise<boolean>;
  passkeys(): Promise<readonly Passkey[]>;
  addPasskey(passkey: Passkey): Promise<void>;
  usePasskey(id: string, counter: number): Promise<void>;
  startSession(hash: string, expires: string): Promise<void>;
  sessionExpiry(hash: string): Promise<string | null>;
  endSession(hash: string): Promise<void>;
  issueToken(token: AgentToken, hash: string): Promise<void>;
  tokenFor(hash: string): Promise<AgentToken | null>;
  revokeToken(id: string): Promise<boolean>;
  tokens(): Promise<readonly AgentToken[]>;
}
