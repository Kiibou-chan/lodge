"""A stand-in for ssh: runs the command locally; the first receive-pack's report is dropped.

`FAKESSH_AFTER`, when set, is a shell command run once the push has landed.

Used through `GIT_SSH_COMMAND` so that a push lands on the remote while the client sees it fail.
"""

import os
import subprocess
import sys
import threading
from typing import IO

command = sys.argv[-1]
marker = os.environ["FAKESSH_MARKER"]
child = subprocess.Popen(["sh", "-c", command], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
assert child.stdin is not None and child.stdout is not None
sink: IO[bytes] = child.stdin
source: IO[bytes] = child.stdout


def pump() -> None:
    while chunk := os.read(0, 65536):
        sink.write(chunk)
        sink.flush()
    sink.close()


threading.Thread(target=pump, daemon=True).start()
out = sys.stdout.buffer
if "receive-pack" not in command or os.path.exists(marker):
    while chunk := source.read1(65536):  # type: ignore[attr-defined]
        out.write(chunk)
        out.flush()
    sys.exit(child.wait())
open(marker, "w").close()
while True:
    size = source.read(4)
    out.write(size)
    out.flush()
    if size == b"0000" or not size:
        break
    out.write(source.read(int(size, 16) - 4))
    out.flush()
source.read()
child.wait()
after = os.environ.get("FAKESSH_AFTER")
if after:
    subprocess.run(["sh", "-c", after], check=True)
sys.exit(1)
