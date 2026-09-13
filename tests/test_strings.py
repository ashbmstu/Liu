"""Tests for liu_analyzer.strings — every language must be complete and well-formed.

A key missing from one language is a KeyError the first time somebody switches
to it, and a mangled placeholder is a crash on Save or About. Neither shows up
when the interface is only ever run in English, so both are checked here.
"""
from __future__ import annotations

import re

import pytest

from liu_analyzer.strings import DEFAULT_LANG, SIGNATURE, STRINGS, get

LANGUAGES = sorted(STRINGS)

# Placeholder -> the keys whose text must contain it in every language.
PLACEHOLDERS = {
    "{scheme}": ("instructions_html",),
    "{version}": ("about_html",),
    "{path}": ("save_ok",),
    "{err}": ("save_error",),
}


def test_english_is_the_default():
    assert DEFAULT_LANG == "en"
    assert get("xx") is STRINGS["en"]


def test_the_expected_languages_are_offered():
    assert set(STRINGS) == {"en", "zh", "es", "fr", "ru"}


@pytest.mark.parametrize("lang", LANGUAGES)
def test_every_language_has_exactly_the_english_keys(lang):
    missing = set(STRINGS["en"]) - set(STRINGS[lang])
    extra = set(STRINGS[lang]) - set(STRINGS["en"])
    assert not missing, f"{lang} is missing {sorted(missing)}"
    assert not extra, f"{lang} has keys English does not: {sorted(extra)}"


@pytest.mark.parametrize("lang", LANGUAGES)
def test_no_translation_is_empty(lang):
    empty = [key for key, text in STRINGS[lang].items() if not text.strip()]
    assert not empty, f"{lang} has empty strings: {empty}"


@pytest.mark.parametrize("lang", LANGUAGES)
def test_placeholders_survive_translation(lang):
    table = STRINGS[lang]
    for placeholder, keys in PLACEHOLDERS.items():
        for key in keys:
            assert placeholder in table[key], f"{lang}.{key} lost {placeholder}"
    # The About and Save messages go through str.format; a stray brace in a
    # translation would raise instead of rendering.
    table["about_html"].format(version="1.0.0")
    table["save_ok"].format(path="x")
    table["save_error"].format(err="x")


@pytest.mark.parametrize("lang", LANGUAGES)
def test_the_menu_can_name_every_language(lang):
    for code in STRINGS:
        assert f"lang_{code}" in STRINGS[lang]


@pytest.mark.parametrize("lang", LANGUAGES)
def test_html_tags_are_balanced(lang):
    for key in ("instructions_html", "about_html"):
        html = STRINGS[lang][key]
        for tag in ("p", "b", "i", "ol", "ul", "li", "table", "tr", "td", "th", "h3", "sub"):
            opened = len(re.findall(rf"<{tag}[\s>]", html))
            closed = html.count(f"</{tag}>")
            assert opened == closed, f"{lang}.{key}: <{tag}> {opened} opened, {closed} closed"


def test_every_language_carries_the_same_signature():
    assert {table["attribution"] for table in STRINGS.values()} == {SIGNATURE}
    assert "ASH" in SIGNATURE
