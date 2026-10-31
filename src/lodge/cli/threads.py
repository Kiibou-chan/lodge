"""Thread command grammar and execution."""

import argparse
from collections.abc import Callable
from dataclasses import dataclass

from lodge.app import AddOutcome, Lodge, LodgeError
from lodge.cli.files import read_file
from lodge.cli.output import check_lines, read_lines
from lodge.cli.thread_output import thread_head, thread_text
from lodge.core import Raises


@dataclass(frozen=True)
class Threads:
    pass


@dataclass(frozen=True)
class ThreadCommand:
    ref: str


@dataclass(frozen=True)
class Ask:
    ref: str
    kind: Raises
    by: str
    where: str | None
    when: str | None
    file: str


@dataclass(frozen=True)
class Reply:
    ref: str
    by: str
    where: str | None
    when: str | None
    file: str


@dataclass(frozen=True)
class Close:
    ref: str
    by: str
    where: str | None
    when: str | None
    file: str | None


ThreadCommands = Threads | ThreadCommand | Ask | Reply | Close


def add_thread_commands(add: Callable[[str, str, object], argparse.ArgumentParser]) -> None:
    add("threads", "list the open threads: doubts and questions on records", lambda _: Threads())
    sub = add("thread", "show one thread with its messages", lambda a: ThreadCommand(a.ref))
    sub.add_argument("ref")
    for name, help_text in (
        ("ask", "open a thread on a record: a doubt or a question"),
        ("reply", "add a message to an open thread"),
        ("close", "close a thread, with a closing message"),
    ):
        sub = add(name, help_text, _message_command)
        sub.set_defaults(thread_action=name)
        sub.add_argument("ref")
        if name == "ask":
            sub.add_argument("--kind", required=True, choices=("doubt", "question"))
        sub.add_argument("--by", required=True)
        sub.add_argument("--where")
        sub.add_argument("--when")
        sub.add_argument("file", metavar="FILE", nargs="?" if name == "close" else None)


def _message_command(args: argparse.Namespace) -> Ask | Reply | Close:
    if args.by == "author":
        if args.where is None or args.when is None:
            raise LodgeError(
                "a message by author needs --where and --when, "
                "the place and time of the author's words"
            )
    elif args.where is not None or args.when is not None:
        raise LodgeError("--where and --when are for messages by author")
    if args.thread_action == "ask":
        return Ask(args.ref, Raises(args.kind), args.by, args.where, args.when, args.file)
    cls = Reply if args.thread_action == "reply" else Close
    return cls(args.ref, args.by, args.where, args.when, args.file)


def run_thread(command: ThreadCommands, lodge: Lodge) -> int:
    if isinstance(command, Threads):
        listed = lodge.threads()
        heads = [thread_head(t, listed.titles.get(t.about, "")) for t in listed.items]
        print("\n".join([*read_lines(listed.read), "\n\n".join(heads) or "no open threads"]))
        return 0
    if isinstance(command, ThreadCommand):
        print(thread_text(lodge.thread(command.ref)))
        return 0
    text = "" if command.file is None else read_file(command.file, "not UTF-8 text", False)
    if isinstance(command, Ask):
        written = lodge.ask(
            command.ref, command.kind, command.by, text, command.where, command.when
        )
    else:
        write = lodge.reply if isinstance(command, Reply) else lodge.close
        written = write(command.ref, command.by, text, command.where, command.when)
    if written.outcome is AddOutcome.CHECK_FAILED:
        print("\n".join([*check_lines(written.check), "not published: the check failed"]))
        return 1
    print(f"{written.outcome.value} {' '.join(written.ids)}")
    return 0
