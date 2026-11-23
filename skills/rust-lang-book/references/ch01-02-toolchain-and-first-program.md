# Ch 0-2 - Introduction, Toolchain, Cargo Basics, Guessing Game

Source: The Rust Programming Language ch. 0-2 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).
Section refs: §0 = Foreword/Introduction, §1.1 Installation, §1.2 Hello World, §1.3 Hello Cargo,
§2 Guessing Game (single section file).

## Core Model

- **Rust's pitch (§0):** high-level ergonomics and low-level control (e.g. memory usage) together; the
  compiler is a gatekeeper that refuses to compile subtle bugs, including concurrency bugs.
- **Zero-cost abstractions (§0):** higher-level features compile to code as fast as hand-written
  low-level code; goal is that safe code is also fast code.
- **Ahead-of-time compiled (§1.2):** compile and run are separate steps; the resulting executable runs
  on a machine without Rust installed.
- **Toolchain roles (§0, §1):** `rustup` manages Rust versions and tools; `rustc` is the compiler;
  `cargo` is build system + package manager; `rustfmt` formats; `rust-analyzer` powers IDE support.
- **Crate (§1.3, §2):** a collection of Rust source files. *Binary crate* = an executable; *library
  crate* = code meant to be used by other programs, not executable on its own (e.g. `rand`).
- **Dependencies (§1.3):** libraries your code needs; Cargo downloads and builds them.
- **Prelude (§2):** set of std items brought into every program's scope automatically; anything else
  needs an explicit `use`.
- **Variables (§2):** `let` binds a name to a value; immutable by default, `mut` opts into mutability.
- **References (§2):** `&` lets several parts of code access one piece of data without copying it;
  references are also immutable by default, so `&mut guess`, not `&guess`, to allow mutation.
- **`Result` (§2):** an enum (type with a fixed set of states called *variants*) encoding
  error-handling info. `Ok` holds the successfully produced value; `Err` holds how/why it failed.
- **`match` (§2):** made of *arms*; each arm is a *pattern* plus code to run when the value fits.
  Patterns are checked in order and the `match` ends after the first arm that matches.
- **Type system (§2):** strong and static, with type inference.

## Rules and Semantics

### Program structure (§1.2)
- `main` is always the first code run in every executable Rust program.
- Function bodies must be wrapped in curly brackets; parameters go inside `()`.
- A trailing `!` means a macro call, not a function call; macros don't always follow function rules.
- A `;` ends an expression so the next can begin; most lines of Rust end with one.
- Source files always use the `.rs` extension.

### Cargo project layout and builds (§1.3)
- `cargo new <name>` creates a directory with `Cargo.toml`, `src/main.rs` (a generated "Hello, world!")
  and a new Git repo with `.gitignore`.
- Git files are not generated when run inside an existing Git repo; `cargo new --vcs=git` overrides.
- Cargo expects source files inside `src/`; the top level is for README, license, config, and other
  non-code files.
- `Cargo.toml` is TOML. `[package]` configures the package (`name`, `version`, `edition`);
  `[dependencies]` lists crates. Everything after a section header belongs to it until the next header.
- Default build is a debug build: output lands in `target/debug/` (`target\debug\<name>.exe` on
  Windows), not the current directory.
- First `cargo build` creates `Cargo.lock` at the top level, recording exact dependency versions.
  Cargo manages it; never edit it by hand.
- Cargo rebuilds only when files changed; `cargo run` with no changes skips the `Compiling` step.
- `cargo build --release` compiles with optimizations into `target/release/`: faster code, longer
  compile. Two profiles exist: development (rebuild quickly and often) and release (final program).

### Dependencies and versions (§2)
- A version like `rand = "0.10.1"` is a SemVer specifier and is shorthand for `^0.10.1`: any version
  at least 0.10.1 but below 0.11.0. Cargo treats those as having a compatible public API.
- On build, Cargo updates the *registry* (a copy of data from Crates.io), downloads listed crates not
  yet downloaded plus their transitive dependencies, compiles them, then compiles the project.
- Reproducible builds: once `Cargo.lock` exists, Cargo uses the versions recorded there rather than
  re-resolving, so the project stays on its locked version until explicitly upgraded.
- `cargo update` ignores `Cargo.lock`, finds the latest versions fitting the `Cargo.toml` specifiers,
  and rewrites `Cargo.lock`. It stays inside the range (0.10.1 -> 0.10.2, not 0.999.0).
- To move to a new incompatible series, edit the specifier in `Cargo.toml`; the next `cargo build`
  updates the registry and re-evaluates the requirement.

### Language behavior shown in the guessing game (§2)
- `String::new()` — `::` marks an *associated function* (a function implemented on a type); returns a
  new empty `String` (growable, UTF-8 encoded text).
- `io::stdin()` returns a `std::io::Stdin` handle; without `use std::io;` write `std::io::stdin`.
- `read_line(&mut s)` *appends* the user's input to the string (does not overwrite) and returns a
  `Result`; its `Ok` value is the number of bytes read. Input includes the trailing newline (`\n`,
  or `\r\n` on Windows).
- `expect(msg)` on a `Result`: on `Err`, crashes the program and shows `msg`; on `Ok`, returns the
  contained value.
- Number types default to `i32` unless other type information makes Rust infer something else.
  Annotating `guess: u32` and comparing with `secret_number` makes `secret_number` a `u32` too.
- `cmp` compares two values, can be called on anything comparable, takes a reference to the other
  value, and returns an `Ordering` (`Less`, `Greater`, `Equal`).
- `trim` removes leading/trailing whitespace (including `\n` / `\r\n`); `parse` converts a string to
  another type, needs the target type stated (e.g. `let guess: u32`), and returns a `Result`.
- Shadowing lets a new `let guess` reuse the name of an earlier `guess`; often used to convert a
  value from one type to another instead of inventing names like `guess_str`.
- `loop` creates an infinite loop; `break` exits it; `continue` jumps to the next iteration.
- `Err(_)`: the underscore is a catch-all that matches every `Err` regardless of its contents.
- Range expression `start..=end` is inclusive on both bounds (`1..=100` is 1 through 100).

## Syntax and API Reference

| Command | Effect | Ref |
| --- | --- | --- |
| `curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf`, output piped to `sh` | install `rustup` (Linux/macOS) | §1.1 |
| `rustc --version` / `cargo --version` | verify install | §1.1, §1.3 |
| `rustup update` | update to the newest released version | §1.1 |
| `rustup self uninstall` | remove Rust and `rustup` | §1.1 |
| `rustup doc` | open the local offline documentation | §1.1 |
| `rustc main.rs` then `./main` (`.\main` on Windows) | compile and run one file without Cargo | §1.2 |
| `cargo new <name>` | create project; `--vcs` picks VCS or none; `cargo new --help` | §1.3 |
| `cargo init` | create `Cargo.toml` for an existing non-Cargo project | §1.3 |
| `cargo build` | debug build into `target/debug/` | §1.3 |
| `cargo run` | build if needed, then run | §1.3 |
| `cargo check` | verify the code compiles without producing an executable | §1.3 |
| `cargo build --release` | optimized build into `target/release/` | §1.3 |
| `cargo update` | re-resolve dependencies within `Cargo.toml` ranges | §2 |
| `cargo doc --open` | build docs for all dependencies locally and open in a browser | §2 |
| `cargo add rand@0.10.1 trpl@0.2.0` | add dependencies (used to pre-cache the book's crates) | §1.1 |
| `--offline` (any `cargo` command) | use cached crates instead of the network | §1.1 |

```toml
[package]
name = "guessing_game"
version = "0.1.0"
edition = "2024"

[dependencies]
rand = "0.10.1"
```

```rust
use std::cmp::Ordering;
use std::io;
use rand::prelude::*;                                  // brings the RngExt trait into scope

let secret_number = rand::rng().random_range(1..=100); // thread-local, OS-seeded generator
let mut guess = String::new();
io::stdin().read_line(&mut guess).expect("Failed to read line");
let guess: u32 = match guess.trim().parse() {          // shadow String with u32
    Ok(num) => num,
    Err(_) => continue,                                // inside a `loop`
};
match guess.cmp(&secret_number) {
    Ordering::Less => println!("Too small!"),
    Ordering::Greater => println!("Too big!"),
    Ordering::Equal => { println!("You win!"); break; }
}
```

- `println!` placeholders (§2): a variable name goes inside the brackets (`{x}`); for an expression
  result use empty `{}` and pass the expressions after the format string, in order:
  `println!("x = {x} and y + 2 = {}", y + 2);`
- `//` starts a comment that runs to the end of the line (§2).

## Decision Rules

- Use plain `rustc` only for simple single-file programs; use Cargo once there are multiple files or
  any dependency (§1.2, §1.3).
- Run `cargo check` periodically while writing code (often much faster than `cargo build`); run
  `cargo build` when you actually need the executable; prefer `cargo run` over build-then-run (§1.3).
- Benchmark only with `cargo build --release` and the binary in `target/release` (§1.3).
- Use `expect` when crashing on failure is acceptable; switch to a `match` on the `Result` to
  handle the error and keep going (§2).
- `u32` is described as a good default choice for a small positive number (§2).

## Pitfalls and Compiler Errors

- **E0308 mismatched types (§2):** `guess.cmp(&secret_number)` with `guess: String` and an integer
  secret reports "expected `&String`, found `&{integer}`". Rust cannot compare a string with a
  number. Fix: `let guess: u32 = guess.trim().parse().expect("Please type a number!");`
- **Warning `unused_must_use` (§2):** calling `read_line` without using its `Result` compiles but
  warns "unused `Result` that must be used". The right fix is real error handling (or `expect` if
  crashing is intended).
- **Forgetting `trim` (§2):** the newline from pressing enter stays in the string and must be
  removed before `parse` to a number can succeed.
- **`expect` on bad input panics (§2):** non-numeric input gives
  `Please type a number!: ParseIntError { kind: InvalidDigit }` and ends the program.
- **Linker errors (§1.1):** install a C compiler (it typically includes a linker): on macOS
  `xcode-select --install`; on Linux GCC or Clang (Ubuntu: `build-essential`); on Windows the
  installer prompts for Visual Studio. Some common crates also need a C compiler for C code.
- **`rustc` not found (§1.1):** check that Rust is on `PATH` (`echo $PATH`, CMD `echo %PATH%`,
  PowerShell `echo $env:Path`).
- **Dependency API drift (§2):** a different `rand` series may have a different API; pin to the
  `0.10` series for this code.

## Idioms and Best Practices

- Multi-word file names use underscores: `hello_world.rs`, not `helloworld.rs` (§1.2).
- Opening curly bracket on the same line as the function declaration, one space before it (§1.2).
- Use `rustfmt` for a standard style; it ships with the standard Rust distribution (§1.2).
- Break long method chains across lines, one `.method_name()` call per line (§2).
- `new` is the common name for an associated function that makes a new value of a type (§2).
- `Cargo.lock` is often checked into source control because it makes builds reproducible (§2).
- Read compiler error messages closely; they guide you toward working code (§0).

## Details Worth Knowing

- Stability guarantee: examples that compile keep compiling on newer stable versions; only error and
  warning wording may change (§1.1).
- On Windows, `rustc` also emits a `.pdb` file with debugging information next to `main.exe` (§1.2).
- Cargo commands are identical on every OS; any existing project builds with `cargo build` (§1.3).
- Random numbers are not in the standard library; the Rust team provides the `rand` crate (§2).
- `random_range` is a method defined by the `RngExt` trait, exported by `rand::prelude` (§2).
- Book structure (§0): ch. 2, 12, 21 are project chapters, the rest concept chapters. Ferris icons
  flag code that does not compile, panics, or does not produce the desired behavior.
- Forward references: variables/shadowing/number types ch. 3; references ch. 4; enums and `match`
  ch. 6; recoverable errors ch. 9; Cargo and Crates.io ch. 14; patterns ch. 19; macros ch. 20;
  `rustfmt` and `rust-analyzer` Appendix D; editions Appendix E.
