# hermes-skills

Skills for [Hermes Agent](https://hermes-agent.nousresearch.com/docs/), published as a tap.

## Install

One skill, without subscribing to the tap:

```bash
hermes skills install am423/hermes-skills/skills/rust-lang-book
```

Or add the tap and browse it:

```bash
hermes skills tap add am423/hermes-skills
hermes skills search rust
```

Later, `hermes skills check` and `hermes skills update` pick up new versions.

## Skills

### rust-lang-book

A knowledge base distilled from every chapter and appendix of
[The Rust Programming Language](https://github.com/rust-lang/book), pinned to commit `5c23042`
(the text assumes Rust 1.99.1, edition 2024). It gives the agent the Book's rules, decision
guidance, and compiler-error fixes while it writes or reviews Rust.

- `SKILL.md`: the rules worth holding in every Rust session, plus an index of the reference
  files. About 170 lines; it is the only part that loads up front.
- `references/`: 23 chapter files (core model, rules, syntax and API reference, decision rules,
  compiler errors with fixes, idioms, details), plus a cheatsheet of decision tables with an
  error-code index, a review checklist, and a glossary. Each loads only when a question needs it.
- `scripts/check_book_updates.py`: reports which chapters changed upstream since the pinned
  commit, so the notes can be refreshed. Stdlib Python plus `git`; nothing runs on a schedule.

Scope: the Book is an introduction. The skill does not cover the Rustonomicon, the Reference,
the API guidelines, performance tuning, or third-party crates beyond the Book's own examples,
and it tells the agent to say so.

How it was checked: every error code and backticked identifier in the chapter files was matched
against the Book's text and listings by script, and the newer syntax the notes rely on
(`&raw const`, `unsafe extern`, `#[unsafe(no_mangle)]`, `let...else`, `if let` chains) was
compiled with rustc 1.99.1. The chapter files were not all proofread line by line; corrections
are welcome as issues or pull requests.

## License and attribution

The skills in this repository are MIT licensed; see `LICENSE`.

`rust-lang-book` is a set of original notes about *The Rust Programming Language* by Steve
Klabnik, Carol Nichols, and Chris Krycho, with contributions from the Rust community. The Book
is copyright The Rust Project Developers and is dual licensed under MIT and Apache 2.0. This
repository is not affiliated with or endorsed by the Rust Project.
