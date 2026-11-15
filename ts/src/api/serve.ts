export function withoutYamlLogging(env: Record<string, string | undefined>): void {
  delete env["LOG_TOKENS"];
  delete env["LOG_STREAM"];
}

export function listen(
  fetch: (request: Request) => Promise<Response>,
  host: string,
  port: number,
): Promise<void> {
  const server = Bun.serve({ fetch, hostname: host, port });
  return new Promise((resolve, reject) => {
    let stopping = false;
    const stop = () => {
      if (stopping) return;
      stopping = true;
      void server.stop().then(
        () => {
          cleanup();
          resolve();
        },
        (error: unknown) => {
          cleanup();
          reject(error);
        },
      );
    };
    const cleanup = () => {
      process.off("SIGINT", stop);
      process.off("SIGTERM", stop);
    };
    process.on("SIGINT", stop);
    process.on("SIGTERM", stop);
  });
}
