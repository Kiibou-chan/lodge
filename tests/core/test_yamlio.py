import pytest

from lodge.core import YamlError, load_yaml


@pytest.mark.parametrize(
    "scalar", ["yes", "no", "on", "~", "null", "14:14", "2026-10-29", "1234", "0x10", "1.5", "true"]
)
def test_yaml_scalars_stay_strings(scalar: str) -> None:
    assert load_yaml(f"key: {scalar}\n") == {"key": scalar}
    assert load_yaml(f"[{scalar}, b]") == [scalar, "b"]


def test_empty_value_is_an_empty_string() -> None:
    assert load_yaml("key:\n") == {"key": ""}


def test_nested_flow_and_block_collections_load() -> None:
    text = "a: {b: c}\nd:\n  - {e: f}\n  - g\n"
    assert load_yaml(text) == {"a": {"b": "c"}, "d": [{"e": "f"}, "g"]}


@pytest.mark.parametrize(
    "text", ["key: !!int 5\n", "key: !!set {a}\n", "key: !!python/name:os.system\n"]
)
def test_explicit_tags_beyond_text_are_refused(text: str) -> None:
    with pytest.raises(YamlError, match="tag"):
        load_yaml(text)


def test_bad_yaml_carries_the_line() -> None:
    with pytest.raises(YamlError) as caught:
        load_yaml("a: b\nc: d: e\n")
    assert caught.value.line == 2


def test_duplicate_key_is_an_error_naming_it() -> None:
    with pytest.raises(YamlError, match="'title'") as caught:
        load_yaml("title: a\nscope: b\ntitle: c\n")
    assert caught.value.line == 3


def test_unreadable_character_carries_the_line() -> None:
    with pytest.raises(YamlError) as caught:
        load_yaml("a: b\nc: \x01\n")
    assert caught.value.line == 2


def test_two_documents_are_an_error() -> None:
    with pytest.raises(YamlError):
        load_yaml("a: b\n---\nc: d\n")


def test_deep_nesting_is_an_error_not_a_crash() -> None:
    with pytest.raises(YamlError, match="nested"):
        load_yaml("a: " + "[" * 5000 + "]" * 5000)


def test_surrogate_pair_escapes_join_into_one_character() -> None:
    assert load_yaml('a: "Ship it \\ud83d\\ude00"') == {"a": "Ship it \U0001f600"}
    assert load_yaml('["\\ud83d\\ude00"]') == ["\U0001f600"]
    assert load_yaml('"\\ud83d\\ude00": b') == {"\U0001f600": "b"}


def test_lone_surrogate_escape_stays_lone() -> None:
    assert load_yaml('a: "\\ud83d"') == {"a": "\ud83d"}
    assert load_yaml('a: "\\ude00\\ud83d"') == {"a": "\ude00\ud83d"}
