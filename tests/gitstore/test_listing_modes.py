"""Branch reads resolve, fetch, and accept once before listings and selected texts."""

from pathlib import Path
from unittest.mock import patch

from fakes import MemoryStore

from gitstore.repos import BRANCH, CHECKOUT, Ticker, bare_remote, git, initialised, publish_one
from gitstore.test_identity import RECORD, agrees, prepared
from lodge.gitstore import open_store
from lodge.gitstore.accepted import ACCEPTED


def test_branch_mode_ident_is_the_tip_tree(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    publish_one(repo, clock, {RECORD: "Branch berth.\n"})
    store = open_store(repo, BRANCH, clock)
    listing = agrees(store)
    assert store.identities() == (listing.ident, listing.ident)
    assert listing.ident == git(repo, "rev-parse", "origin/lodge:lodge")
    assert git(repo, "rev-parse", ACCEPTED) == listing.rev
    # Neither listing nor text retrieval resolves a new tip or fetches again.
    expected = store.listings()
    publish_one(repo, clock, {RECORD: "Later tip.\n"})
    with patch("lodge.gitstore.git.attempt", side_effect=AssertionError("re-resolved revision")):
        assert store.listings() == expected
    assert store.texts(listing, [RECORD]) == {RECORD: "Branch berth.\n"}
    assert agrees(store).ident != listing.ident


def test_rewritten_branch_publishes_the_accepted_tree(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    original = git(repo, "rev-parse", "origin/lodge")
    publish_one(repo, clock, {RECORD: "Accepted berth.\n"})
    accepted = git(repo, "rev-parse", ACCEPTED)
    store = open_store(repo, BRANCH, clock)
    store.identities()
    git(repo, "push", "--force", "origin", f"{original}:refs/heads/lodge")
    clock.advance(61)
    current = agrees(store)
    published = store.listings()[1]
    assert current.ident == git(repo, "rev-parse", "origin/lodge:lodge")
    assert published.ident == git(repo, "rev-parse", f"{accepted}:lodge")
    assert current.ident != published.ident
    assert store.texts(published, [RECORD]) == {RECORD: "Accepted berth.\n"}
    assert git(repo, "rev-parse", ACCEPTED) == accepted
    assert "was rewritten" in (store.freshness() or "")


def test_missing_published_message_matches_exact(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    store.trees()
    git(repo, "checkout", "-b", "feature")
    git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    git(repo, "branch", "-D", "main")
    store.identities()
    exact = open_store(repo, CHECKOUT, Ticker())
    exact.trees()
    assert exact.freshness() is not None
    assert store.freshness() == exact.freshness()


def test_memory_listing_keeps_attachment_presence() -> None:
    store = MemoryStore(staged=True)
    attachment = "lodge/attachments/d-aaaaaa/log.txt"
    store.files[attachment] = "First evidence.\n"
    store.published[attachment] = "Published evidence.\n"
    before = store.identities()
    current, published = store.listings()
    assert current.attachments == published.attachments == {attachment}
    assert attachment not in current.blobs
    store.files[attachment] = "Edited evidence.\n"
    assert store.identities() == before
    del store.files[attachment]
    assert store.identities()[0] != before[0]
    assert not store.listings()[0].attachments
