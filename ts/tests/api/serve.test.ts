import { expect, mock, spyOn, test } from "bun:test";
import { listen } from "#api";

test.each(["SIGINT", "SIGTERM"] as const)(
  "%s starts graceful shutdown and a repeated signal forces it",
  async (first) => {
    const second = first === "SIGINT" ? "SIGTERM" : "SIGINT";
    const before = [process.listenerCount("SIGINT"), process.listenerCount("SIGTERM")] as const;
    const stopped = Promise.withResolvers<void>();
    const stop = mock((_force?: boolean) => stopped.promise);
    const serve = spyOn(Bun, "serve").mockReturnValue({ stop } as unknown as ReturnType<
      typeof Bun.serve
    >);
    const fetch = async () => new Response("ok");
    const listening = listen(fetch, "127.0.0.1", 8787);
    let settled = false;
    const done = listening.finally(() => {
      settled = true;
    });
    try {
      expect(serve).toHaveBeenCalledWith({
        fetch,
        hostname: "127.0.0.1",
        port: 8787,
        maxRequestBodySize: 8 * 1024 * 1024,
      });
      expect(process.listenerCount("SIGINT")).toBe(before[0] + 1);
      expect(process.listenerCount("SIGTERM")).toBe(before[1] + 1);
      process.emit(first);
      expect(stop).toHaveBeenCalledTimes(1);
      expect(stop).toHaveBeenNthCalledWith(1);
      await Promise.resolve();
      expect(settled).toBe(false);
      process.emit(second);
      expect(stop).toHaveBeenCalledTimes(2);
      expect(stop).toHaveBeenNthCalledWith(2, true);
      await Promise.resolve();
      expect(settled).toBe(false);
      stopped.resolve();
      await done;
      expect(process.listenerCount("SIGINT")).toBe(before[0]);
      expect(process.listenerCount("SIGTERM")).toBe(before[1]);
    } finally {
      if (process.listenerCount(first) > before[first === "SIGINT" ? 0 : 1]) process.emit(first);
      stopped.resolve();
      await done;
      serve.mockRestore();
    }
  },
);

test("a rejected graceful stop removes both signal handlers and preserves the error", async () => {
  const before = [process.listenerCount("SIGINT"), process.listenerCount("SIGTERM")] as const;
  const stopped = Promise.withResolvers<void>();
  const stop = mock(() => stopped.promise);
  const serve = spyOn(Bun, "serve").mockReturnValue({ stop } as unknown as ReturnType<
    typeof Bun.serve
  >);
  const error = new Error("shutdown failed");
  const listening = listen(async () => new Response("ok"), "127.0.0.1", 8787);
  const outcome = listening.catch((reason: unknown) => reason);
  try {
    process.emit("SIGTERM");
    expect(stop).toHaveBeenCalledTimes(1);
    expect(stop).toHaveBeenCalledWith();
    stopped.reject(error);
    expect(await outcome).toBe(error);
    expect(process.listenerCount("SIGINT")).toBe(before[0]);
    expect(process.listenerCount("SIGTERM")).toBe(before[1]);
  } finally {
    stopped.resolve();
    await outcome;
    serve.mockRestore();
  }
});
