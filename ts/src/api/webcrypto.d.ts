import type { webcrypto } from "node:crypto";

// The WebAuthn X.509 declarations name browser crypto types in the global scope.
declare global {
  type BufferSource = ArrayBufferView | ArrayBuffer;
  type Algorithm = webcrypto.Algorithm;
  type AlgorithmIdentifier = webcrypto.AlgorithmIdentifier;
  type EcKeyImportParams = webcrypto.EcKeyImportParams;
  type RsaHashedImportParams = webcrypto.RsaHashedImportParams;
  type KeyUsage = webcrypto.KeyUsage;
  type EcKeyGenParams = webcrypto.EcKeyGenParams;
  type EcdsaParams = webcrypto.EcdsaParams;
}
