import { expect, test } from "bun:test";
import {
  generateAuthenticationOptions, generateRegistrationOptions,
  verifyAuthenticationResponse, verifyRegistrationResponse,
} from "@simplewebauthn/server";
import { isoBase64URL, isoCBOR } from "@simplewebauthn/server/helpers";

const rpID = "lodge.test";
const origin = "https://lodge.test";
const enc = new TextEncoder();
const sha256 = async (b: Uint8Array) => new Uint8Array(await crypto.subtle.digest("SHA-256", b));
const cat = (...p: Uint8Array[]) => { const o = new Uint8Array(p.reduce((n, x) => n + x.length, 0)); let i = 0; for (const x of p) { o.set(x, i); i += x.length; } return o; };
function der(raw: Uint8Array): Uint8Array {
  const int = (b: Uint8Array) => { let i = 0; while (i < b.length - 1 && b[i] === 0) i++; let v = b.slice(i); if (v[0]! & 0x80) v = cat(new Uint8Array([0]), v); return cat(new Uint8Array([2, v.length]), v); };
  const body = cat(int(raw.slice(0, 32)), int(raw.slice(32)));
  return cat(new Uint8Array([0x30, body.length]), body);
}
class SoftAuthenticator {
  credId = crypto.getRandomValues(new Uint8Array(16));
  keys!: CryptoKeyPair; count = 0;
  async create(challenge: string) {
    this.keys = await crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]) as CryptoKeyPair;
    const jwk = await crypto.subtle.exportKey("jwk", this.keys.publicKey);
    const cose = isoCBOR.encode(new Map<number, number | Uint8Array>([[1, 2], [3, -7], [-1, 1], [-2, isoBase64URL.toBuffer(jwk.x!)], [-3, isoBase64URL.toBuffer(jwk.y!)]]));
    const authData = cat(await sha256(enc.encode(rpID)), new Uint8Array([0x45]), new Uint8Array(4), new Uint8Array(16), new Uint8Array([0, 16]), this.credId, cose);
    const clientDataJSON = enc.encode(JSON.stringify({ type: "webauthn.create", challenge, origin }));
    const attestationObject = isoCBOR.encode(new Map<string, unknown>([["fmt", "none"], ["attStmt", new Map()], ["authData", authData]]) as never);
    const id = isoBase64URL.fromBuffer(this.credId);
    return { id, rawId: id, type: "public-key" as const, clientExtensionResults: {}, response: { clientDataJSON: isoBase64URL.fromBuffer(clientDataJSON), attestationObject: isoBase64URL.fromBuffer(attestationObject), transports: ["internal" as const] } };
  }
  async get(challenge: string) {
    this.count++;
    const authData = cat(await sha256(enc.encode(rpID)), new Uint8Array([0x05]), new Uint8Array([0, 0, 0, this.count]));
    const clientDataJSON = enc.encode(JSON.stringify({ type: "webauthn.get", challenge, origin }));
    const sig = new Uint8Array(await crypto.subtle.sign({ name: "ECDSA", hash: "SHA-256" }, this.keys.privateKey, cat(authData, await sha256(clientDataJSON))));
    const id = isoBase64URL.fromBuffer(this.credId);
    return { id, rawId: id, type: "public-key" as const, clientExtensionResults: {}, response: { clientDataJSON: isoBase64URL.fromBuffer(clientDataJSON), authenticatorData: isoBase64URL.fromBuffer(authData), signature: isoBase64URL.fromBuffer(der(sig)) } };
  }
}
test("register and sign in with a software authenticator", async () => {
  const a = new SoftAuthenticator();
  const reg = await generateRegistrationOptions({ rpName: "lodge", rpID, userName: "owner" });
  const r = await verifyRegistrationResponse({ response: await a.create(reg.challenge), expectedChallenge: reg.challenge, expectedOrigin: origin, expectedRPID: rpID });
  expect(r.verified).toBe(true);
  const info = r.registrationInfo!;
  const auth = await generateAuthenticationOptions({ rpID, allowCredentials: [{ id: info.credential.id }] });
  const v = await verifyAuthenticationResponse({ response: await a.get(auth.challenge), expectedChallenge: auth.challenge, expectedOrigin: origin, expectedRPID: rpID, credential: info.credential });
  expect(v.verified).toBe(true);
  expect(v.authenticationInfo.newCounter).toBe(1);
  const bad = await a.get("wrong-challenge");
  await expect(verifyAuthenticationResponse({ response: bad, expectedChallenge: auth.challenge, expectedOrigin: origin, expectedRPID: rpID, credential: info.credential })).rejects.toThrow();
});
