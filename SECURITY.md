# Security

This is a desktop calculator. It has no network code of any kind: it opens no
sockets, checks for no updates, and sends nothing anywhere. It reads and writes
two things — a JSON session file you choose, and a rotating log at
`%LOCALAPPDATA%\LiuAnalyzer\liu.log`.

## What is worth reporting

**A wrong number.** The way this program can do harm is by producing a
plausible threshold fluence that is incorrect, which then ends up in somebody's
thesis or paper. A sign error in the uncertainty propagation, a grouping bug
that averages the wrong repeats, a fit that silently ignores a point — none of
those are security vulnerabilities, and all of them matter more than one here.
Please report them, with the measurements that produced them.

**Anything the JSON loader will do with a hostile file.** Session files are
meant to be shared between colleagues, so it is fair to ask what happens when
one has been tampered with. The loader parses JSON and constructs dataclasses;
it does not evaluate anything. If you find a way to make it do more than that,
that is a real vulnerability.

## The executable

The released `.exe` is a PyInstaller one-file bundle, which means it unpacks
itself to a temporary directory at startup. That is normal for the format and is
also why some antivirus products flag PyInstaller binaries. If you would rather
not run an unsigned executable, run from source — the instructions are in the
[README](README.md) and the build is reproducible with `build.bat`.

The binary is not code-signed.

## How to report

Use [GitHub's private vulnerability
reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
on this repository. For a wrong number, an ordinary issue is better — it is
easier to discuss in the open and there is nothing to keep quiet.

## What to expect

There is no support commitment and no CVE process. Reports are read in good
faith; fixes depend on maintainer time.
