# Ch 12 - An I/O Project: Building a Command Line Program

Source: The Rust Programming Language ch. 12 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- Project: `minigrep`, a simple `grep` clone. Takes a query string and a file path, reads the file, prints
  the lines containing the query. Invoked as `cargo run -- searchstring example-filename.txt` (§12.0-12.1).
- Rust suits CLI tools because of speed, safety, single binary output, and cross-platform support (§12.0).
- Chapter combines: code organization (ch. 7), vectors/strings (ch. 8), error handling (ch. 9), traits and
  lifetimes (ch. 10), tests (ch. 11); previews closures, iterators (ch. 13), trait objects (ch. 18).
- Central structural model for binary projects, "separation of concerns" (§12.3):
  - `src/main.rs` handles *running* the program; `src/lib.rs` holds the *logic* of the task.
  - `main` cannot be tested directly, so logic is moved out of it; what remains must be small enough to
    verify by reading.
- CLI configuration sources: command line arguments (per invocation) and environment variables (set once
  per terminal session) (§12.1, §12.5).
- Two output streams: standard output (`stdout`) for general information, standard error (`stderr`) for
  error messages, so users can redirect successful output to a file and still see errors (§12.6).

## Rules and Semantics

### Command line arguments (§12.1)
- `std::env::args()` returns an iterator over the arguments; `.collect()` turns it into a collection.
- `collect` usually needs a type annotation (`let args: Vec<String> = ...`) because Rust cannot infer
  which kind of collection is wanted; one of the few places annotations are often required.
- `args[0]` is the program name (e.g. `"target/debug/minigrep"`), matching the C argument list; real
  arguments start at index 1. The name is useful for messages or alias-dependent behavior.
- `std::env::args` panics if any argument contains invalid Unicode. `std::env::args_os` instead yields
  `OsString` values, which differ per platform and are more complex to work with than `String`.
- With `cargo run`, the `--` separator marks the following arguments as the program's, not Cargo's.

### Reading a file (§12.2)
- `fs::read_to_string(file_path)` opens the file and returns `std::io::Result<String>` with its contents.

### Responsibilities of `main` after refactoring (§12.3)
`main` should be limited to:
1. Calling the command line parsing logic with the argument values.
2. Setting up any other configuration.
3. Calling a `run` function.
4. Handling the error if `run` returns one.

### Error handling design (§12.3)
- `panic!` suits a programming problem, not a usage problem; for bad user input return a `Result`.
- A panic prints programmer-oriented text (`thread 'main' ... panicked at`, `RUST_BACKTRACE` note), e.g.
  `index out of bounds: the len is 1 but the index is 1` when indexing `args` without enough arguments.
- `Config::build(args: &[String]) -> Result<Config, &'static str>`: error values are string literals
  with the `'static` lifetime; check `args.len() < 3` and `return Err("not enough arguments")`.
- `unwrap_or_else` (on `Result<T, E>`): on `Ok` returns the inner value like `unwrap`; on `Err` calls the
  closure, passing the inner error as the closure argument between the vertical pipes (`|err|`).
- `process::exit(code)` stops the program immediately and returns the number as the exit status code.
  A nonzero exit status conventionally signals an error state to the calling process.
- `run(config: Config) -> Result<(), Box<dyn Error>>` (with `use std::error::Error;`):
  - `Box<dyn Error>` is a trait object: the function returns some type implementing `Error` without
    naming it, so different error cases may return different error types. `dyn` is short for dynamic.
  - `?` replaces `expect`: returns the error from the current function to the caller instead of panicking.
  - `Ok(())` is the idiomatic way to say the function is called for its side effects only.
- Ignoring the returned `Result` compiles but warns: `unused `Result` that must be used`
  (`#[warn(unused_must_use)]`, part of `#[warn(unused)]`, on by default).

### Library crate split (§12.3)
- In this text only the search logic moves to `src/lib.rs` (`pub fn search`, later
  `pub fn search_case_insensitive`); `Config`, `Config::build`, and `run` stay in `src/main.rs`.
- `pub` makes `search` part of the library crate's public API; the binary crate imports it by package
  name: `use minigrep::search;` then `use minigrep::{search, search_case_insensitive};`.

### Lifetimes in `search` (§12.4)
- `pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str>`: the returned slices borrow from
  `contents`, not `query`, so only `contents` is tied to the return value; the result lives as long as
  the data passed in `contents`.
- `contents.lines()` returns an iterator over lines; `line.contains(query)` tests for a substring.

### Environment variables (§12.5)
- `env::var("IGNORE_CASE")` returns a `Result`: `Ok` holding the value if the variable is set to any
  value, `Err` if it is not set. `.is_ok()` tests only set-vs-unset when the value is irrelevant.
- `to_lowercase` creates new data, so the result is a `String`, not a slice; pass `&query` to `contains`
  because `contains` takes a string slice. It handles basic Unicode but is not 100 percent accurate.

### Standard error (§12.6)
- `println!` can only print to standard output; `eprintln!` prints to the standard error stream.
- Shell `>` redirects only standard output: `cargo run > output.txt`.

## Syntax and API Reference

Final shape of `src/main.rs` (§12.3, §12.5, §12.6):

```rust
fn main() {
    let args: Vec<String> = env::args().collect();
    let config = Config::build(&args).unwrap_or_else(|err| {
        eprintln!("Problem parsing arguments: {err}");
        process::exit(1);
    });
    if let Err(e) = run(config) {
        eprintln!("Application error: {e}");
        process::exit(1);
    }
}
```

```rust
let ignore_case = env::var("IGNORE_CASE").is_ok();        // set-or-unset check
let contents = fs::read_to_string(config.file_path)?;      // propagate io error
let results = if config.ignore_case {
    search_case_insensitive(&config.query, &contents)
} else {
    search(&config.query, &contents)
};
```

| Item | Use (section) |
|---|---|
| `std::env::args`, `std::env::args_os` | argument iterators: `String` / `OsString` (§12.1) |
| `Iterator::collect` | iterator -> collection; annotate target type (§12.1) |
| `dbg!(args)` | debug-print a value with file/line (§12.1 listing) |
| `std::fs::read_to_string` | whole file -> `std::io::Result<String>` (§12.2) |
| `Result::unwrap_or_else(closure)` | unwrap or run custom non-panic handling (§12.3) |
| `std::process::exit(1)` | exit immediately with status code (§12.3) |
| `std::error::Error`, `Box<dyn Error>` | flexible error return type (§12.3) |
| `unimplemented!()` | placeholder body; panics with "not implemented" (§12.3-12.4) |
| `str::lines`, `str::contains`, `str::to_lowercase` | line iteration, substring test, lowercase (§12.4-5) |
| `std::env::var` | read an environment variable -> `Result` (§12.5) |
| `eprintln!` | print to stderr (§12.6) |

Shell usage (§12.5-12.6): `IGNORE_CASE=1 cargo run -- to poem.txt`; PowerShell:
`$Env:IGNORE_CASE=1; cargo run -- to poem.txt` (persists for the session; unset with
`Remove-Item Env:IGNORE_CASE`); `cargo run -- to poem.txt > output.txt`.

## Decision Rules

- Split a binary when `main` grows: (1) create `main.rs` + `lib.rs` and move program logic to `lib.rs`;
  (2) keep CLI parsing in `main` while it is small; (3) once parsing gets complicated, extract it from
  `main` into other functions or types (§12.3).
- Return a tuple that is immediately destructured -> sign of a missing abstraction; use a struct with
  meaningfully named fields (§12.3).
- A free function whose purpose is building an instance (`parse_config`) -> make it an associated
  function on the type (§12.3).
- Name a fallible constructor `build`, not `new`: many programmers expect `new` never to fail (§12.3).
- `unwrap_or_else` when the success value is needed; `if let Err(e) = run(config)` when the `Ok` value
  is `()` and only the error matters (§12.3).
- `clone` vs references: cloning a few small strings once is an acceptable trade of a little performance
  for simplicity (no lifetimes to manage). Prefer a working, slightly inefficient program over
  hyperoptimizing on the first pass; ch. 13 shows more efficient methods (§12.3).
- Environment variable vs CLI option: use an env var for a setting users want to set once and have
  apply to every run in that session. Programs accepting both must decide which takes precedence (§12.5).
- Bring the parent module into scope (`use std::env;` then `env::args()`) for functions nested in more
  than one module: less ambiguous than a bare `args`, and gives access to other `env` functions (§12.1).

## Pitfalls and Compiler Errors

- E0106 `missing lifetime specifier` on `pub fn search(query: &str, contents: &str) -> Vec<&str>`: the
  compiler cannot tell which parameter the return value borrows from. Its help text suggests putting
  `'a` on every parameter and the output, which the book calls incorrect here; annotate only `contents`
  and the return type (§12.4).
- Indexing `args[1]`/`args[2]` without a length check panics with an index-out-of-bounds message meant
  for programmers (§12.3).
- Generic `expect("Should have been able to read the file")` gives the same message for every failure
  cause (missing file, no permission); propagate the real error instead (§12.3).
- Scattered error handling: keep all error-handling code in one place so maintainers consult a single
  spot and messages stay meaningful to end users (§12.3).
- A function with multiple responsibilities gets harder to reason about, test, and change; many variables
  in scope obscure each one's purpose (§12.3).
- Taking ownership of values in `args` from a function that only borrows `args` would violate the
  borrowing rules; `Config` therefore owns cloned `String`s (§12.3).
- Printing errors with `println!` sends them into redirected output files (§12.6).
- `search` collects all results into a vector before anything is printed, so output can be slow for
  large files; an iterator-based fix is discussed in ch. 13 (§12.3).

## Idioms and Best Practices

- Refactor early and in small incremental steps, rerunning the program after each step to localize the
  cause of any problem; refactoring is easier on smaller amounts of code (§12.2-12.3).
- Refactoring sequence used: extract `parse_config` -> group values in `Config` struct -> turn into
  `Config::new` -> add length check with `panic!` -> return `Result` and rename to `Config::build` ->
  handle in `main` with `unwrap_or_else` + `process::exit(1)` -> extract `run` -> make `run` return
  `Result<(), Box<dyn Error>>` using `?` -> handle with `if let Err` -> move search logic to `src/lib.rs`
  (§12.3).
- Group configuration variables into one struct so their purpose and relationship are explicit (§12.3).
- Each function should be responsible for one idea/task (§12.2-12.3).
- TDD loop (§12.4): (1) write a failing test and confirm it fails for the expected reason; (2) write or
  modify just enough code to pass; (3) refactor while tests keep passing; (4) repeat. Writing the test
  first helps drive design and keeps coverage high.
- TDD mechanics shown: start with `unimplemented!()`, then a stub returning `vec![]` so the test compiles
  and fails on the assertion, then the real implementation (§12.4).
- When adding a variant of existing behavior, tighten the old test too (add a `"Duct tape."` line to the
  case-sensitive test) so existing behavior is not broken by accident; rename tests to clarify the
  distinction (`one_result` -> `case_sensitive`, new `case_insensitive`) (§12.5).
- Shadow a parameter with its transformed version: `let query = query.to_lowercase();` (§12.5).
- Well-behaved CLI programs send error messages to stderr and exit nonzero on failure (§12.3, §12.6).
- Multi-line test fixture: `"\` right after the opening quote avoids a leading newline (§12.4).

## Details Worth Knowing

- Existing crates on crates.io can help with argument parsing; the chapter implements it by hand for
  learning (§12.1).
- `ripgrep` by Andrew Gallant is a fully featured, very fast `grep` in Rust (§12.0).
- `search` algorithm: iterate lines, check `contains`, `push` matches onto a `let mut results =
  Vec::new();`, return the vector (§12.4).
- Because refactoring concentrated error printing in `main`, switching to `eprintln!` touched only two
  call sites (§12.6).
- The `std::env` module has more features for environment variables; see its documentation (§12.5).
- Suggested exercise: support both a CLI argument and an env var for case sensitivity and choose a
  precedence (§12.5).
- Forward references: closures and iterators (ch. 13, which revisits `Config::build` and `search`),
  trait objects (ch. 18).
