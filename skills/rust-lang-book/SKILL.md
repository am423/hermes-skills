---
name: rust-lang-book
description: Write and review idiomatic Rust per The Rust Book.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [Rust, Cargo, Ownership, Idioms, Code-Review, Reference]
    category: software-development
    homepage: https://github.com/am423/hermes-skills
---

# The Rust Programming Language (Book) Knowledge Base

Distilled notes on every chapter and appendix of *The Rust Programming Language*
(github.com/rust-lang/book, pinned in `assets/source-pin.json`; the text assumes Rust 1.99.1,
edition 2024): rules, syntax, decision guidance, compiler errors and their fixes, and small details.
The core rules below apply to all Rust work; chapter files load on demand. It covers what the Book
covers and no more: the Book is an introduction, so crate selection beyond its examples, the
Rustonomicon, the Reference, API guidelines, and performance tuning are outside it. Say so and
consult those sources with `web_extract` rather than stretching these notes.

## When to Use

- Writing, reviewing, refactoring, or debugging any Rust code or `Cargo.toml`.
- "Why does the borrow checker reject this", any `E0xxx` compiler error, lifetime questions.
- Choosing between Rust features: `Box`/`Rc`/`RefCell`/`Arc`/`Mutex`, enum vs trait object vs
  generics, `panic!` vs `Result`, threads vs async, `match` vs `if let` vs `let...else`.
- Designing module layout, tests, docs, workspaces, release profiles, publishing a crate.
- Writing `unsafe`, FFI, macros, advanced traits and types.
- Don't use for: questions about a specific third-party crate's API (read that crate's docs).

## Prerequisites

- A Rust toolchain from `rustup` (ships `cargo`, `rustfmt`, Clippy). Check through the `terminal`
  tool: `rustc --version` and `cargo --version`. New projects use `edition = "2024"`.
- `git` and Python 3 only for `scripts/check_book_updates.py` (stdlib only; it clones
  github.com/rust-lang/book into the Hermes cache directory).

## How to Run

1. Apply the core rules below while writing.
2. Before answering a detailed question or making a design choice, load the matching file:
   `skill_view(name="rust-lang-book", file_path="references/<file>")`. Reference files cost nothing
   until loaded; load the one chapter the question needs, not all of them.
3. Unsure which file: load `references/cheatsheet.md` (decision tables, error-code index) or
   `references/glossary.md` (term to file).
4. Before calling Rust work finished, walk `references/review-checklist.md`.

## Quick Reference

### Core rules (hold in every Rust session)

- Ownership: each value has one owner; when the owner goes out of scope the value is dropped.
  Assigning or passing a non-`Copy` value moves it and invalidates the source.
- Borrowing: at any time either one `&mut T` or any number of `&T`; references must always be
  valid. A reference's scope ends at its last use.
- Take `&str` / `&[T]` / `&T` parameters unless the function needs ownership; return owned values
  for data the function creates. `clone` is a deliberate deep copy, not a borrow-checker escape.
- Lifetime annotations describe relationships between references; they never extend a lifetime.
  A suggested `'static` usually signals a dangling reference, not a fix.
- Variables are immutable by default; use `mut` or shadowing on purpose. Blocks, `if`, `match`, and
  `loop` are expressions; the last expression without a semicolon is the value.
- Encode absence as `Option<T>` and failure as `Result<T, E>`; propagate with `?`. `panic!` is for
  broken invariants, examples, prototypes, and tests. Prefer `expect` with a reason over `unwrap`.
- `match` is exhaustive; use `if let` for one case and `let...else` to extract-or-bail.
- Prefer enums when the set of variants is closed, generics with trait bounds for static dispatch,
  and `dyn Trait` only when the set of types is open or heterogeneous.
- Prefer iterator adapter chains to index loops and mutable accumulators: same speed.
- Compile-time checks are the default; reach for `RefCell<T>`, `Rc<T>`, `Arc<Mutex<T>>`, and
  `unsafe` only when the compiler cannot verify something you know holds.
- Keep `main.rs` thin and put logic in `lib.rs` so it can be tested; unit tests live beside the
  code in `#[cfg(test)] mod tests`, integration tests in `tests/`.
- Everything is private by default; design the public API with `pub` and `pub use`.
- Threads for CPU-bound parallel work, async for I/O-bound concurrent work; `Send` and `Sync`
  make data races compile errors.
- The installed compiler is the arbiter: when these notes, memory, and `rustc` disagree, compile
  a minimal example and go with what `rustc` accepts.

### Reference index

| File | Load this when ... |
|---|---|
| `references/cheatsheet.md` | choosing between features; looking up which chapter explains an `E0xxx` code |
| `references/review-checklist.md` | reviewing or finishing Rust code: yes/no checks per topic with chapter refs |
| `references/glossary.md` | a Rust term needs a definition or you need the file that covers it |
| `references/ch01-02-toolchain-and-first-program.md` | rustup, `rustc`, Cargo basics, `Cargo.toml`/`Cargo.lock`, adding a crate, the guessing game |
| `references/ch03-common-concepts.md` | variables, `const`, shadowing, scalar and compound types, overflow, functions, expressions, loops |
| `references/ch04-ownership.md` | moves, `Copy`, `clone`, references, borrow rules, slices, stack vs heap |
| `references/ch05-structs.md` | struct forms, update syntax, `impl` blocks, methods, `self` receivers, `Debug`, `dbg!` |
| `references/ch06-enums-and-matching.md` | enums, `Option<T>`, `match`, `if let`, `let...else` |
| `references/ch07-packages-crates-modules.md` | packages, crates, modules, paths, `pub`, `use`, `pub use`, file layout |
| `references/ch08-collections.md` | `Vec<T>`, `String` and UTF-8, `HashMap<K, V>`, the entry API |
| `references/ch09-error-handling.md` | `panic!`, backtraces, `Result`, `?`, `unwrap`/`expect`, when to panic, validation types |
| `references/ch10-generics-traits-lifetimes.md` | generics, traits, bounds, `impl Trait`, `where`, lifetimes, elision rules |
| `references/ch11-testing.md` | test attributes and macros, `cargo test` flags, unit vs integration test layout |
| `references/ch12-cli-project.md` | structuring a CLI binary, args, files, env vars, stderr, TDD workflow |
| `references/ch13-closures-and-iterators.md` | closures, capture modes, `Fn`/`FnMut`/`FnOnce`, the `Iterator` trait, adapters, performance |
| `references/ch14-cargo-and-crates-io.md` | release profiles, doc comments, publishing, yanking, workspaces, `cargo install` |
| `references/ch15-smart-pointers.md` | `Box`, `Deref`, `Drop`, `Rc`, `RefCell`, `Weak`, reference cycles |
| `references/ch16-concurrency.md` | threads, `move` closures, channels, `Mutex`, `Arc`, `Send`/`Sync` |
| `references/ch17-async.md` | `async`/`await`, futures, tasks, the `trpl` crate, join/select, streams, `Pin`/`Unpin` |
| `references/ch18-oop-and-trait-objects.md` | encapsulation, `dyn Trait`, dynamic dispatch, state pattern vs types |
| `references/ch19-patterns.md` | every place patterns appear, refutability, full pattern syntax table |
| `references/ch20-unsafe.md` | unsafe superpowers, raw pointers, `unsafe fn`, FFI with `extern`, `static mut`, Miri |
| `references/ch20-advanced-traits-types-functions.md` | associated types, operator overloading, disambiguation, supertraits, newtype, aliases, `!`, DSTs, `fn` pointers, returning closures |
| `references/ch20-macros.md` | `macro_rules!`, derive, attribute-like and function-like procedural macros |
| `references/ch21-web-server-project.md` | TCP/HTTP by hand, thread-pool design, graceful shutdown with `Drop` |
| `references/appendix-reference.md` | keyword list, operator and symbol tables, derivable traits, `cargo fmt`/`fix`/`clippy`, editions, release channels |

### Commands the Book relies on (through the `terminal` tool)

- `cargo new <name>` / `cargo new <name> --lib`, `cargo add <crate>`
- `cargo check`, `cargo build`, `cargo build --release`, `cargo run`
- `cargo test`, `cargo test -- --test-threads=1`, `cargo test -- --ignored`
- `cargo fmt`, `cargo fix`, `cargo clippy`, `cargo doc --open`
- `cargo +nightly miri test` (after `rustup +nightly component add miri`)

## Procedure

### Writing or reviewing Rust

1. Identify the topics the task touches and load those reference files (index above). For a
   compiler error, find the code in `references/cheatsheet.md`, then load the chapter file.
2. Decide data shapes and ownership first (cheatsheet tables), then write the code.
3. Check the result through the `terminal` tool: `cargo fmt`, `cargo clippy`, `cargo test`.
   Done when all three finish with no errors and no warnings you have not explained.
4. Walk the sections of `references/review-checklist.md` that apply to the change. Done when
   every "no" is either fixed or reported with its reason.
5. When the notes do not cover something, say so and consult the official docs with
   `web_extract`; do not present outside knowledge as the Book's guidance.

### Updating From Upstream (manual; nothing is scheduled)

1. Through the `terminal` tool:
   `python3 ${HERMES_SKILL_DIR}/scripts/check_book_updates.py check`. `"up_to_date": true`
   means stop.
2. For each file under `changed_references`, run the same script with
   `diff <reference-file>` and revise that reference with
   `skill_manage` patch. Skip diffs that only reword prose. `sources <reference-file>` lists the
   upstream files behind a reference.
3. An `UNMAPPED` entry is a new chapter file: write a new reference in the same format, add its
   prefix to `SRC_MAP` in the script, and add a row to the index above.
4. Re-check `references/cheatsheet.md`, `references/review-checklist.md`,
   `references/glossary.md`, and the core rules for anything now stale.
5. Only then run the script with `pin` (it rewrites `assets/source-pin.json`) and bump `version`.

## Pitfalls

- These notes follow the pinned text, which is newer than much remembered Rust. Trust the notes
  over memory: raw pointers use `&raw const` / `&raw mut`; extern blocks are `unsafe extern`;
  the attribute is `#[unsafe(no_mangle)]`; references to `static mut` hit the `static_mut_refs`
  lint; workspaces use `resolver = "3"`; the book's `rand` examples use
  `rand::rng().random_range(..)`; trait objects are governed by "dyn compatibility".
- `trpl` in ch. 17 is the Book's teaching crate, not a production recommendation; map its
  functions to the chosen runtime's equivalents.
- The Book can lag the compiler. Its ch. 19 says `if let` cannot chain a condition with `&&`;
  rustc 1.99.1 on edition 2024 compiles it. `references/ch19-patterns.md` marks this as a compiler
  check, separate from the Book's text.
- Chapter 21's prose and its final listing disagree on `Vec::drain` vs `Option::take` for joining
  workers; the reference records both.
- Compiler messages quoted in the references come from the Book's captured output; wording can
  shift between compiler versions while the error code stays stable.
- Section refs such as `§10.3` mean chapter 10, section file 3 (`src/ch10-03-*.md` upstream).

## Verification

Through the `terminal` tool:
`python3 ${HERMES_SKILL_DIR}/scripts/check_book_updates.py check` prints the pinned commit and
whether upstream has moved. `search_files(pattern="*.md", target="files",
path="${HERMES_SKILL_DIR}/references")` should list the 26 files in the index above.
