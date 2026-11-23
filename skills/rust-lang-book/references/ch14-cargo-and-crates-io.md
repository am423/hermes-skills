# Ch 14 - More About Cargo and Crates.io

Source: The Rust Programming Language ch. 14 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- Chapter scope: release profiles, publishing libraries to crates.io, workspaces, installing binaries,
  custom Cargo commands. Cargo's own documentation covers the rest (§14.0).
- Release profile: a predefined, customizable set of compiler options. Each profile is configured
  independently of the others. Two main ones: `dev` (used by `cargo build`) and `release` (used by
  `cargo build --release`) (§14.1).
- crates.io is a crate registry that distributes the *source code* of packages, so it primarily hosts
  open source code (§14.2).
- Documentation comment: a comment that generates HTML documentation for public API items, aimed at
  people who want to *use* the crate rather than know how it is *implemented* (§14.2).
- Re-exporting (`pub use`): takes a public item in one location and makes it public in another, as if
  defined there. It decouples the public API structure from the private module structure (§14.2).
- Publishing uploads a specific version; a publish is permanent. crates.io aims to be a permanent
  archive so builds of dependents keep working (§14.2).
- Yanking: blocks new projects from depending on a version while existing dependents keep working (§14.2).
- Workspace: a set of packages that share the same `Cargo.lock` and output directory, for related
  packages developed in tandem (§14.3).
- Binary target: the runnable program created when a crate has `src/main.rs` or another file specified
  as a binary; a library target is not runnable on its own but is included in other programs (§14.4).

## Rules and Semantics

### Release profiles (§14.1)
- Default settings apply for each profile when `Cargo.toml` has no `[profile.*]` section. Adding a
  `[profile.*]` section overrides any subset of the defaults; unspecified settings keep defaults.
- `opt-level` controls the number of optimizations, range 0 to 3. Defaults: `dev` = `0`, `release` = `3`.
- More optimization extends compile time. `dev` favors fast compiles of frequently rebuilt code;
  `release` trades longer compile time for faster code (compiled once, run many times).
- Build output names the profile: `Finished `dev` profile [unoptimized + debuginfo]` versus
  `Finished `release` profile [optimized]`.

### Documentation comments (§14.2)
- `///` documents the item that follows; supports Markdown; placed just before the item.
- `//!` documents the item that *contains* the comment. Typically used at the top of the crate root file
  (`src/lib.rs` by convention) or inside a module to describe the crate or module as a whole. No code
  needs to follow the last `//!` line. Crate-level `//!` text appears on the docs front page above the
  list of public items.
- `cargo doc` runs the `rustdoc` tool and writes HTML to `target/doc`. `cargo doc --open` builds docs for
  the current crate and all its dependencies and opens them in a browser.
- Doc tests: `cargo test` runs code examples in documentation comments as tests, reported under
  `Doc-tests <crate>` with names like `test src/lib.rs - add_one (line 5) ... ok`. A panicking
  `assert_eq!` in an example fails the run, catching docs that drifted from the code.
- Commonly used sections (Markdown headings inside doc comments):
  - `# Examples`: usage code.
  - Panics: scenarios in which the function could panic, so callers can avoid them.
  - Errors: for functions returning `Result`, the kinds of errors and the conditions causing them.
  - Safety: for functions that are `unsafe` to call, why, and the invariants callers must uphold (ch. 20).

### Public API and `pub use` (§14.2)
- Without re-exports, users must write the internal path (`use art::kinds::PrimaryColor;`,
  `use art::utils::mix;`) and the docs front page lists only the modules, not the nested items.
- With `pub use self::kinds::PrimaryColor;` etc. at the crate root, users write `use art::PrimaryColor;`
  and `use art::mix;`; `cargo doc` lists and links the re-exports on the front page.
- The original nested paths remain usable after re-exporting.
- `pub use` can also re-export a dependency's definitions to make them part of your crate's public API.

### crates.io account, metadata, publishing (§14.2)
- Log in to crates.io via a GitHub account (currently required), get an API key from
  `https://crates.io/me/`, then run `cargo login` and paste the key when prompted. The token is stored
  locally in `~/.cargo/credentials.toml`. It is a secret; if shared, revoke it and generate a new one.
- Crate names are allocated first-come, first-served; a taken name cannot be published by anyone else.
  Local names are unrestricted; set `name` under `[package]` to a unique name before publishing.
- `description` and `license` are required for publishing. Without them `cargo publish` warns
  (`manifest has no description, license, license-file, documentation, homepage or repository.`) and
  the registry rejects with `status 400 Bad Request ... missing or empty metadata fields: description,
  license`.
- `license` takes an SPDX license identifier (e.g. `MIT`); multiple identifiers are joined with `OR`.
  For a license not in SPDX, put its text in a file in the project and use `license-file` instead of
  `license`.
- A published version can never be overwritten and the code cannot be deleted except in certain
  circumstances. There is no limit on the number of versions you can publish.
- New version: change `version` in `Cargo.toml` following Semantic Versioning rules, then `cargo publish`.
- Yank: run in the crate's directory. Projects with an existing `Cargo.lock` do not break; newly
  generated `Cargo.lock` files will not use the yanked version. `--undo` reverses a yank. A yank does
  not delete any code.

### Workspaces (§14.3)
- The workspace root `Cargo.toml` has no `[package]` section; it starts with `[workspace]`, here with
  `resolver = "3"` (the latest resolver algorithm per the text) and a `members` list.
- Running `cargo new` inside a workspace automatically adds the new package to `members`
  (`Adding `adder` as member of workspace at ...`).
- One top-level `target` directory holds all compiled artifacts; members have no `target` of their own,
  even when `cargo build` is run from inside a member directory. Sharing it avoids each crate
  recompiling the others.
- Cargo does not assume workspace crates depend on each other: declare path dependencies explicitly.
- One top-level `Cargo.lock` means all crates use the same version of each dependency, so they stay
  compatible. If members specify compatible versions, Cargo resolves them to one version and downloads
  no extra copies; if incompatible, Cargo resolves each but still tries to use as few versions as
  possible.
- An external dependency is usable only in members that list it in their own `Cargo.toml`, even if
  another member already depends on it.
- `cargo test` at the root runs the tests of all crates in the workspace; `-p <name>` limits it to one.
- Each workspace crate must be published separately; `-p` selects the crate to publish.

### `cargo install` and custom commands (§14.4-14.5)
- `cargo install` installs binary crates locally; only packages with binary targets can be installed.
- Binaries go in the installation root's `bin` folder: `$HOME/.cargo/bin` when Rust was installed with
  rustup and nothing is customized. That directory must be in `$PATH` to run the tools.
- A binary in `$PATH` named `cargo-something` can be run as `cargo something`, and such custom commands
  are listed by `cargo --list`. They can be installed with `cargo install`.

## Syntax and API Reference

```toml
[profile.dev]
opt-level = 1            # override; default dev = 0, release = 3
```

```toml
[package]
name = "guessing_game"
version = "0.1.0"
edition = "2024"
description = "A fun game where you guess what number the computer has chosen."
license = "MIT OR Apache-2.0"
```

```toml
# workspace root Cargo.toml          # adder/Cargo.toml
[workspace]                          [dependencies]
resolver = "3"                       add_one = { path = "../add_one" }
members = ["adder", "add_one"]
```

```rust
//! # My Crate
//!
//! `my_crate` is a collection of utilities ...

/// Adds one to the number given.
///
/// # Examples
///
/// ```
/// let answer = my_crate::add_one(5);
/// assert_eq!(6, answer);
/// ```
pub fn add_one(x: i32) -> i32 { x + 1 }
```

```rust
pub use self::kinds::PrimaryColor;   // re-export at crate root
pub use self::utils::mix;
```

| Command | Effect (section) |
|---|---|
| `cargo build` / `cargo build --release` | build with `dev` / `release` profile (§14.1) |
| `cargo doc`, `cargo doc --open` | generate HTML docs in `target/doc`; also open them (§14.2) |
| `cargo test` | also runs doc tests; whole workspace at a workspace root (§14.2, §14.3) |
| `cargo login` | store crates.io API token (§14.2) |
| `cargo publish` | upload the current version (§14.2) |
| `cargo yank --vers 1.0.1` | yank a version (§14.2) |
| `cargo yank --vers 1.0.1 --undo` | undo the yank (§14.2) |
| `cargo new adder`, `cargo new add_one --lib` | create workspace members (§14.3) |
| `cargo run -p adder` | run one package's binary from the workspace root (§14.3) |
| `cargo test -p add_one` | test one workspace crate (§14.3) |
| `cargo install ripgrep` | install a binary crate (executable `rg`) (§14.4) |
| `cargo --list` | list subcommands, including custom ones (§14.5) |

## Decision Rules

- Raise `opt-level` in `[profile.dev]` when you want more optimization during development than the
  default but fewer than a release build; keep it low when compiling often (§14.1).
- Use `///` for items and `//!` for the enclosing crate or module; use `//!` to explain the container's
  overall purpose and help users understand the crate's organization (§14.2).
- Use `pub use` when the internal hierarchy that suits development is inconvenient for users (deeply
  nested types, many nested modules) instead of rearranging internal organization (§14.2).
- Yank when a published version is broken; it is not a removal tool (§14.2).
- Move to a workspace when a package's library keeps growing and should be split into multiple library
  crates, or when crates are often changed together and need coordination (§14.3).
- `cargo install` is a convenience for Rust developers to get tools shared on crates.io, not a
  replacement for system packages (§14.4).

## Pitfalls and Compiler Errors

- `cargo publish` without `description`/`license` fails with the 400 Bad Request metadata error (§14.2).
- Publishing is permanent: check before publishing. Accidentally uploaded secrets cannot be deleted by
  yanking; reset those secrets immediately (§14.2).
- Sharing the crates.io API token: revoke and regenerate (§14.2).
- Doc examples that no longer match the code fail under `cargo test`; outdated examples are called
  worse than none (§14.2).
- E0432 `unresolved import `rand`` / `no external crate `rand`` when a workspace member uses a crate
  that only another member declares. Fix: add the dependency to that member's `Cargo.toml` (§14.3).
- `use rand;` without using it gives `warning: unused import: `rand`` (`#[warn(unused_imports)]`, part
  of `#[warn(unused)]`, on by default); the output suggests `cargo fix --lib -p add_one` (§14.3).
- Forgetting the explicit path dependency between workspace members: membership alone does not make
  one crate visible to another (§14.3).
- Trying to `cargo install` a library-only package: only binary targets are installable (§14.4).
- Installed tools not found: `$HOME/.cargo/bin` is not in `$PATH` (§14.4).

## Idioms and Best Practices

- Invest in accurate documentation; include examples, since they double as tests (§14.2).
- Treat Panics / Errors / Safety as a checklist of what users want to know; most doc comments do not
  need every section (§14.2).
- Keep `description` to a sentence or two, because it appears with the crate in search results (§14.2).
- Many in the Rust community dual-license like Rust itself: `MIT OR Apache-2.0` (§14.2).
- Search crates.io for the desired name before attempting to publish (§14.2).
- Designing a public API is "more an art than a science": iterate, and look at how installed crates'
  internal structure differs from their public API (§14.2).
- Workspaces let you work with smaller, easier-to-understand components instead of one big blob (§14.3).
- Check a crate's README to learn whether it is a library, has a binary target, or both (§14.4).
- Share useful code on crates.io: the standard library is small and stable, while crates evolve on a
  timeline different from the language's (§14.5).

## Details Worth Knowing

- Full profile options and defaults: `https://doc.rust-lang.org/cargo/reference/profiles.html` (§14.1).
- Other package metadata is described in Cargo's documentation; the publish warning also names
  `documentation`, `homepage`, and `repository` fields (§14.2).
- `cargo publish` output stages: Packaging, Verifying (compiles the packaged crate under
  `target/package/<name>-<version>`), Uploading, then waits for availability at registry `crates-io`
  (§14.2).
- Workspace layout shown is "one common way" among several: root `Cargo.toml` + `Cargo.lock` +
  `target`, with member directories `adder/` (binary) and `add_one/` (library) (§14.3).
- A member library is called by crate path, e.g. `add_one::add_one(num)` (§14.3).
- Workspace test output has one section per crate target plus `Doc-tests` for libraries (§14.3).
- `cargo install ripgrep` builds with the `release` profile; the output line `Installing ~/.cargo/bin/rg`
  shows the binary's location and name (§14.4).
- The example dependency version in this text is `rand = "0.10.1"` (§14.3).
- Cross references: doc tests appear in `cargo test` output described in ch. 11; workspaces extend the
  binary + library package built in ch. 12; unsafe is covered in ch. 20.
