import {
  type AuthenticationResponseJSON,
  generateAuthenticationOptions,
  generateRegistrationOptions,
  type RegistrationResponseJSON,
  verifyAuthenticationResponse,
  verifyRegistrationResponse,
} from "@simplewebauthn/server";
import { stampOf } from "#app";
import { Args } from "./args.ts";
import { ApiError } from "./errors.ts";
import type { ApiOptions } from "./options.ts";
import { endSession, sessionActor, sessionSecret, startSession } from "./session.ts";
import { hashSecret } from "./tokens.ts";

const MAX_CHALLENGES = 1000;
export const publicOperations = [
  "register-options",
  "register",
  "sign-in-options",
  "sign-in",
  "sign-out",
  "me",
];
const fields: Readonly<Record<string, readonly string[]>> = {
  "register-options": ["setupCode"],
  register: ["setupCode", "response"],
  "sign-in-options": [],
  "sign-in": ["response"],
  "sign-out": [],
  me: [],
};
export interface CeremonyAnswer {
  readonly result: unknown;
  readonly cookie?: string;
}
export function passkeys(options: ApiOptions) {
  const challenges = new Map<string, { kind: string; expires: number }>();
  function spend(kind: string) {
    return (challenge: string) => {
      const issued = challenges.get(challenge);
      challenges.delete(challenge);
      return issued?.kind === kind && issued.expires > options.clock.now().epochMs;
    };
  }
  function remember(challenge: string, kind: string) {
    const now = options.clock.now().epochMs;
    for (const [key, issued] of challenges) {
      if (issued.expires > now) break;
      challenges.delete(key);
    }
    if (challenges.size >= MAX_CHALLENGES) {
      const oldest = challenges.keys().next().value;
      if (oldest !== undefined) challenges.delete(oldest);
    }
    challenges.set(challenge, { kind, expires: now + 300000 });
  }
  async function registrationAccess(args: Args, request: Request): Promise<string | null> {
    const code = args.nullable("setupCode");
    if (code === null) {
      if (request.headers.has("Authorization")) throw new ApiError("unauthorised", "sign in again");
      await sessionActor(options, request);
      return null;
    }
    const hash = hashSecret(code.toLowerCase().replace(/[-\s]/gu, ""));
    if (!(await options.accounts.setupCodeValid(hash)))
      throw new ApiError("unauthorised", "the setup code is wrong, spent, or expired");
    return hash;
  }
  async function verify<T>(fn: () => Promise<T>): Promise<T> {
    try {
      return await fn();
    } catch (error) {
      options.log(
        JSON.stringify(error instanceof Error ? error.message : "passkey verification failed"),
      );
      throw new ApiError("unauthorised", "the passkey was not accepted");
    }
  }
  return async (
    operation: string,
    body: Record<string, unknown>,
    request: Request,
  ): Promise<CeremonyAnswer> => {
    const args = new Args(operation, body);
    args.known(fields[operation] ?? []);
    const setup = await options.accounts.setup();
    const keys = await options.accounts.passkeys();
    if (operation === "me") {
      let signedIn = false;
      if (!request.headers.has("Authorization") && sessionSecret(request) !== null) {
        try {
          await sessionActor(options, request);
          signedIn = true;
        } catch (error) {
          if (!(error instanceof ApiError) || error.kind !== "unauthorised") throw error;
        }
      }
      return {
        result: {
          setUp: keys.length > 0,
          signedIn,
          ...(signedIn ? { person: setup?.person } : {}),
        },
      };
    }
    if (!setup)
      throw new ApiError("unauthorised", "the server is not set up; run lodge server setup");
    const rpID = new URL(setup.origin).hostname;
    if (operation === "register-options") {
      await registrationAccess(args, request);
      const userID = new Uint8Array(new ArrayBuffer(16));
      userID.set(
        new Bun.CryptoHasher("sha256")
          .update(`${setup.origin} ${setup.person}`)
          .digest()
          .subarray(0, 16),
      );
      const result = await generateRegistrationOptions({
        rpName: "lodge",
        rpID,
        userName: setup.person,
        userID,
        attestationType: "none",
        authenticatorSelection: { residentKey: "preferred", userVerification: "required" },
        excludeCredentials: keys.map((k) => ({ id: k.id })),
      });
      remember(result.challenge, "register");
      return { result };
    }
    if (operation === "register") {
      const codeHash = await registrationAccess(args, request);
      const response = args.object("response") as unknown as RegistrationResponseJSON;
      const verified = await verify(() =>
        verifyRegistrationResponse({
          response,
          expectedChallenge: spend("register"),
          expectedOrigin: setup.origin,
          expectedRPID: rpID,
          requireUserVerification: true,
        }),
      );
      if (!verified.verified || !verified.registrationInfo)
        throw new ApiError("unauthorised", "the passkey was not accepted");
      if (codeHash !== null && !(await options.accounts.spendSetupCode(codeHash)))
        throw new ApiError("unauthorised", "the setup code is wrong, spent, or expired");
      const credential = verified.registrationInfo.credential;
      await options.accounts.addPasskey({
        id: credential.id,
        publicKey: Buffer.from(credential.publicKey).toString("base64url"),
        counter: credential.counter,
        transports: credential.transports ?? [],
        created: stampOf(options.clock.now()),
      });
      return { result: null, cookie: await startSession(options) };
    }
    if (operation === "sign-in-options") {
      const result = await generateAuthenticationOptions({
        rpID,
        allowCredentials: keys.map((k) => ({ id: k.id })),
        userVerification: "required",
      });
      remember(result.challenge, "sign-in");
      return { result };
    }
    if (operation === "sign-in") {
      const response = args.object("response") as unknown as AuthenticationResponseJSON;
      const key = keys.find((k) => k.id === response.id);
      if (!key) throw new ApiError("unauthorised", "the passkey was not accepted");
      const verified = await verify(() =>
        verifyAuthenticationResponse({
          response,
          expectedChallenge: spend("sign-in"),
          expectedOrigin: setup.origin,
          expectedRPID: rpID,
          requireUserVerification: true,
          credential: {
            id: key.id,
            publicKey: new Uint8Array(Buffer.from(key.publicKey, "base64url")),
            counter: key.counter,
          },
        }),
      );
      if (!verified.verified) throw new ApiError("unauthorised", "the passkey was not accepted");
      await options.accounts.usePasskey(key.id, verified.authenticationInfo.newCounter);
      return { result: null, cookie: await startSession(options) };
    }
    if (request.headers.has("Authorization"))
      throw new ApiError("forbidden", "only the signed-in person may sign-out");
    await sessionActor(options, request);
    return { result: null, cookie: await endSession(options, request) };
  };
}
