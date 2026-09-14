# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2026-09-14

### Added

- **Open.** A saved JSON session can now be read back into the window from the
  footer, which is what the Save option had been promising. A file that is not
  a session, or holds a non-positive measurement, is refused with a message
  rather than half-loaded.

### Changed

- **The energy axis starts logarithmic.** That is the view in which Liu's
  method is a straight line and the one every screenshot shows; a new user no
  longer has to find Settings to see it.

### Fixed

- **The threshold uncertainty now uses the whole covariance of the fit.** The
  slope and intercept of a least-squares line are correlated, and the earlier
  propagation treated them as independent, although the documentation said
  otherwise. A test checks the result against an independent computation of
  the covariance matrix.

## [1.0.0] - 2026-09-13

First public release. The tool has been in use since May 2026; this is the point
at which somebody else could pick it up.

### Added

- **Liu's method, end to end.** Enter (pulse energy, crater diameter) pairs and
  read the ablation threshold fluence and the Gaussian beam waist, each with a
  1σ uncertainty propagated from the regression covariance, plus the R² of the
  fit.
- **Error bars from repeats.** Measurements sharing a pulse energy are grouped
  automatically and drawn with their sample standard deviation.
- **A chart that makes the method obvious**, with a switchable logarithmic or
  linear energy axis. On the logarithmic axis the fit is a straight line, which
  is the whole point of the technique.
- **Five languages**: English, Chinese, Spanish, French and Russian, switchable
  from the header. English is the default.
- **Light and dark themes**, switchable from Settings.
- **Save** as a JSON session that reopens, or as a PNG of the chart with the
  data table drawn underneath it.
- **An Instructions dialog** deriving every quantity from the fitted slope and
  intercept, with the error-propagation expression for each, and a diagram of
  the beam geometry.
- **A one-file portable executable.** No installer and no Python on the target
  machine. `build.bat` builds it locally; pushing a version tag builds it on a
  clean Windows runner and attaches it to a GitHub release.
- **Demo data on first launch** — six greyed-out points, dismissed by the first
  real measurement, so that the window is never blank and never ambiguous about
  whether the data is yours.

### Fixed

- **The Gaussian-beam diagram is now credited.** It is adapted from a Wikimedia
  Commons figure under CC BY-SA 3.0, which requires attribution; the credit
  appears in the About dialog, so it travels inside the executable, and in
  [NOTICE](NOTICE).
- Lint findings across the codebase: modern `X | None` annotations, imports from
  `collections.abc`, and sorted imports. Qt's model API requires a call in a
  default argument, so `B008` is ignored for `data_table.py` with a note saying
  why rather than being worked around.

[1.0.1]: https://github.com/ashbmstu/Liu/releases/tag/v1.0.1
[1.0.0]: https://github.com/ashbmstu/Liu/releases/tag/v1.0.0
