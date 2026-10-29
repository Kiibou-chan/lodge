import tomllib

import pytest

from lodge.core import CoreSettings, LengthGuidance, SettingsError, parse_core_settings


def test_settings_defaults_when_empty() -> None:
    settings = parse_core_settings({})
    assert settings == CoreSettings(length=LengthGuidance(), import_sources=())
    assert settings.length == LengthGuidance(100, 80, 150, 1000)


def test_settings_reads_every_key() -> None:
    table = tomllib.loads(
        "[length]\n"
        "title_chars = 60\n"
        "decision_statement_words = 40\n"
        "spec_statement_words = 90\n"
        "reasoning_words = 500\n"
        "[import]\n"
        'sources = ["docs/old.md", "notes.md"]\n'
    )
    settings = parse_core_settings(table)
    assert settings == CoreSettings(
        length=LengthGuidance(60, 40, 90, 500), import_sources=("docs/old.md", "notes.md")
    )
    assert settings.length.title_chars == 60
    assert settings.length.decision_statement_words == 40
    assert settings.length.spec_statement_words == 90
    assert settings.length.reasoning_words == 500
    assert settings.import_sources == ("docs/old.md", "notes.md")


def test_settings_keeps_the_defaults_of_keys_left_out() -> None:
    settings = parse_core_settings({"length": {"reasoning_words": 300}})
    assert settings.length == LengthGuidance(100, 80, 150, 300)


def test_settings_rejects_unknown_key_naming_it() -> None:
    with pytest.raises(SettingsError, match=r"length\.title"):
        parse_core_settings(tomllib.loads("[length]\ntitle = 5\n"))


def test_settings_rejects_unknown_import_key_and_section() -> None:
    with pytest.raises(SettingsError, match=r"import\.source"):
        parse_core_settings({"import": {"source": []}})
    with pytest.raises(SettingsError, match=r"\[lenght\]"):
        parse_core_settings({"lenght": {}})
    with pytest.raises(SettingsError, match="colour"):
        parse_core_settings({"colour": "red"})


def test_settings_leaves_the_tables_of_other_packages_alone() -> None:
    assert parse_core_settings({"store": {"mode": "branch"}, "hook": {}}) == parse_core_settings({})


@pytest.mark.parametrize("value", [0, -3, True, "80", 1.5])
def test_settings_rejects_a_length_that_is_not_a_positive_integer(value: object) -> None:
    with pytest.raises(SettingsError, match=r"length\.title_chars"):
        parse_core_settings({"length": {"title_chars": value}})


@pytest.mark.parametrize("value", ["docs/a.md", [1], [""], 7])
def test_settings_rejects_sources_that_are_not_a_list_of_strings(value: object) -> None:
    with pytest.raises(SettingsError, match=r"import\.sources"):
        parse_core_settings({"import": {"sources": value}})


def test_settings_rejects_a_section_that_is_not_a_table() -> None:
    with pytest.raises(SettingsError, match="length"):
        parse_core_settings({"length": 5})
