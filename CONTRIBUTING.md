# Contributing to Liu Threshold Analyzer

Thank you for considering a contribution. This is a small tool with a narrow
job, and the most valuable thing anyone can send is a case where it gets the
physics wrong.

## Before you open a pull request

```bat
pytest tests
ruff check .
```

CI runs both, plus a check that the links in the documentation resolve. The
test suite covers the analysis and persistence layers, which import nothing
from Qt and so run anywhere, and checks that every translation is complete.
There is no automated test of the interface; `python tools\screenshots.py`
builds every widget and draws the chart, which is the closest thing to one.

If your change touches `analysis.py`, please add a test with numbers in it.
A dataset with a known answer — from a paper, a reference instrument, or a
synthetic beam you generated — is worth more than any amount of discussion
about the algebra.

## The shape of the code

`analysis.py` and `models.py` must keep importing nothing from Qt. That
separation is what lets the mathematics be used from a script or a notebook,
and what lets the tests run on a machine with no display. Please do not reach
for a widget from inside them.

## Translations

Everything a user reads lives in `strings.py`, in five languages: English,
Chinese, Spanish, French and Russian. English is the default, and the one the
others are translated from.

A change that adds visible text needs the new key in every language. If you
cannot write one of them, put the English in its place rather than leaving the
key out, and say so in the pull request so that a speaker can fix it later.
`tests/test_strings.py` fails when a key is missing or when a placeholder such
as `{version}` has been lost in translation.

To add a language:

1. Copy the `en` block in `strings.py` under the new language code and
   translate it.
2. Give it a short `header_lang` label; that is what the top bar shows.
3. Add the language's name, written in that language, to `_LANGUAGE_NAMES`.
4. Add the code to `test_the_expected_languages_are_offered`.

The chart is drawn by matplotlib, whose own fonts cover Latin, Greek and
Cyrillic. A language in any other script also needs a system font for it in
the fallback list at the top of `widgets/chart_canvas.py`, as Chinese has.

## Code style

- Python 3.11, 4-space indent.
- `ruff` with the configuration in `pyproject.toml` is the arbiter. Line length
  100, and `E501` is not enforced.
- Type annotations on anything in the analysis layer.
- Comments explain why, not what.

## Reporting a problem

Useful reports include the measurements themselves. A screenshot of the chart
plus the (energy, diameter) pairs you typed in lets anyone reproduce the fit
exactly — that is usually enough to settle whether the tool or the data is at
fault.

Also say which Windows version, which interface language, and whether you ran
the `.exe` or the source.

## Commit messages

Use an imperative subject line under about 72 characters, with no type prefix.
In the body, explain the reasoning.
