# Ch 9 - Error Handling

Source: The Rust Programming Language ch. 9 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- Rust has no exceptions. Errors fall into two categories, each with its own mechanism (§9.0):
  - Recoverable (e.g. file not found): report and/or retry -> return `Result<T, E>`.
  - Unrecoverable (always the symptom of a bug, e.g. indexing past the end of an array): stop
    immediately -> `panic!`.
- The compiler frequently forces you to acknowledge a possible error before the code compiles (§9.0).
- `Result` is an ordinary enum; `T` is the success payload, `E` the failure payload (§9.2):
  ```rust
  enum Result<T, E> {
      Ok(T),
      Err(E),
  }
  ```
- A panic is triggered two ways: an action that panics (out-of-range index) or an explicit `panic!` call.
  Default behaviour: print a failure message, unwind, clean up the stack, quit (§9.1).
- Returning `Result` hands the decision to the caller; panicking makes the "unrecoverable" decision on the
  caller's behalf. A caller can always turn an `Err` into a panic, never the reverse (§9.3).
- Propagating = returning the error to the caller instead of handling it locally, because the caller may
  have more information or logic for deciding what to do (§9.2).

## Rules and Semantics

### Panics (§9.1)
- Unwinding (default): Rust walks back up the stack and cleans up each function's data. It is a lot of work.
- Aborting: ends the program without cleanup; the OS reclaims the memory. Yields a smaller binary.
- The panic message's first line gives the message and the source location, e.g. `src/main.rs:2:5`
  (line 2, character 5). The location is where `panic!` was invoked, which may be inside code you call
  (std or a dependency) rather than the line of your code that led to it.
- `v[99]` on a 3-element vector panics with
  `index out of bounds: the len is 3 but the index is 99`. `[]` must return an element, and no correct
  element exists, so Rust stops instead of reading out of bounds. The same read in C is undefined
  behaviour (a buffer overread, a potential security vulnerability).
- Backtrace = list of every function called to reach the panic point. Reading rule: start from the top and
  read until you reach files you wrote; that is where the problem originated. Lines above are code your
  code called; lines below are code that called yours.
- Backtraces with that information need debug symbols, which are on by default for `cargo build` /
  `cargo run` without `--release`.

### `Result` handling (§9.2)
- `File::open` returns `Result` with `T = std::fs::File` (a file handle) and `E = std::io::Error`.
- `Result`, `Ok` and `Err` are in the prelude (as with `Option`): no `Result::` prefix needed in arms.
- `io::Error` is a struct with a `kind` method returning an `io::ErrorKind` enum value;
  `ErrorKind::NotFound` means the file does not exist. Match on `error.kind()` to react per failure cause.
- `unwrap`: returns the `Ok` payload, or calls `panic!` on `Err` (same as the hand-written `match`).
- `expect(msg)`: same as `unwrap`, but `msg` is the panic message, followed by the error's debug output.

### The `?` operator (§9.2)
- On a `Result`: `Ok(v)` -> the expression evaluates to `v` and execution continues; `Err(e)` -> the
  whole function returns early with that error, as if `return` had been written.
- Difference from the manual `match`: the error value passes through `from` (the `From` trait), converting
  it to the error type named in the current function's return type. So a function can return one error
  type covering many failure causes. Given `impl From<io::Error> for OurError`, `?` on an `io::Error`
  inside a function returning `OurError` converts with no extra code.
- Method calls may be chained directly after `?`: `File::open("hello.txt")?.read_to_string(&mut s)?;`
- `?` is only usable where the function's return type is compatible with the value `?` is applied to,
  because it performs an early return. Allowed return types: `Result`, `Option`, or another type
  implementing `FromResidual`.
- On an `Option`: `None` -> early return of `None`; `Some(v)` -> expression evaluates to `v`.
- No mixing: `?` on `Result` needs a `Result`-returning function, `?` on `Option` needs an
  `Option`-returning one. `?` never converts between them; convert explicitly with `ok` (on `Result`)
  or `ok_or` (on `Option`).

### `main` return types (§9.2)
- `main` is the program's entry and exit point, so its return type is restricted. Besides `()` it can
  return `Result<(), E>`; more generally any type implementing `std::process::Termination`, whose
  `report` function returns an `ExitCode`.
- `main` returning `Ok(())` exits with `0`; returning an `Err` exits with a nonzero value (C convention).
- `Box<dyn Error>` is a trait object (ch. 18); read it as "any kind of error". With it, `?` in `main`
  accepts any `Err` value, and the signature stays correct as new error sources are added.

## Syntax and API Reference

```toml
[profile.release]
panic = 'abort'        # abort instead of unwind, in the chosen [profile] section(s)
```

| Item | Meaning (§) |
|---|---|
| `panic!("crash and burn");` | explicit panic with a message (§9.1) |
| `RUST_BACKTRACE=1 cargo run` | print backtrace; any value except `0` enables it (§9.1) |
| `RUST_BACKTRACE=full` | verbose backtrace, suggested by the backtrace's own note (§9.1) |
| `File::open("hello.txt")` | `Result<std::fs::File, std::io::Error>` (§9.2) |
| `File::create("hello.txt")` | create the file; also returns a `Result` (§9.2) |
| `error.kind()` | `io::ErrorKind`, e.g. `ErrorKind::NotFound` (§9.2) |
| `.unwrap()` | payload or panic with default message (§9.2) |
| `.expect("msg")` | payload or panic with your message (§9.2) |
| `.unwrap_or_else(\|error\| { ... })` | closure-based alternative to `match` on `Result` (§9.2) |
| `username_file.read_to_string(&mut username)` | needs `use std::io::Read`; returns a `Result` (§9.2) |
| `fs::read_to_string("hello.txt")` | open + create `String` + read + return, in one call (§9.2) |
| `.ok()` / `.ok_or(..)` | `Result` -> `Option` / `Option` -> `Result` (§9.2) |

```rust
// Propagation, shortest forms (§9.2)
fn read_username_from_file() -> Result<String, io::Error> {
    let mut username = String::new();
    File::open("hello.txt")?.read_to_string(&mut username)?;
    Ok(username)
}

fn last_char_of_first_line(text: &str) -> Option<char> {
    text.lines().next()?.chars().last()
}

fn main() -> Result<(), Box<dyn Error>> {      // use std::error::Error;
    let greeting_file = File::open("hello.txt")?;
    Ok(())
}
```

```rust
// Per-cause handling without nested match (§9.2)
let greeting_file = File::open("hello.txt").unwrap_or_else(|error| {
    if error.kind() == ErrorKind::NotFound {
        File::create("hello.txt").unwrap_or_else(|error| {
            panic!("Problem creating the file: {error:?}");
        })
    } else {
        panic!("Problem opening the file: {error:?}");
    }
});
```

## Decision Rules

- Default for a function that might fail: return `Result` (§9.3).
- Panicking (`unwrap` / `expect`) is appropriate in (§9.3):
  - Examples: robust handling would obscure the point; `unwrap` is understood as a placeholder.
  - Prototypes: they leave clear markers to revisit when hardening the program.
  - Tests: a panic is how a test is marked failed, so a failing call should fail the whole test.
  - Cases where you know more than the compiler: other logic guarantees `Ok`, but the type still says
    `Result`. Use `expect` and state the reason in the message.
- Panic when the code could end up in a bad state (a broken assumption, guarantee, contract or invariant:
  invalid, contradictory or missing values) plus one or more of (§9.3):
  - the bad state is unexpected, not something that will happen occasionally (like bad user input);
  - code after this point relies on not being in that state rather than re-checking at every step;
  - there is no good way to encode the requirement in the types.
- Caller passed nonsensical values: prefer returning an error so the library user decides; panic instead
  when continuing could be insecure or harmful (§9.3).
- External code outside your control returned an invalid state you cannot fix: panicking is often
  appropriate (§9.3).
- Failure is expected (parser given malformed data, HTTP response signalling a rate limit): return
  `Result` (§9.3).
- Operation could put a user at risk on invalid values: validate first and panic if invalid. This is why
  std panics on out-of-bounds memory access (§9.3).
- Want smallest possible binary: `panic = 'abort'` (§9.1).
- `?` hits a function with an incompatible return type: either change the return type (if nothing
  prevents it) or handle the value with `match` or a `Result<T, E>` method (§9.2).

## Pitfalls and Compiler Errors

- E0277 "the `?` operator can only be used in a function that returns `Result` or `Option` (or another
  type that implements `FromResidual`)": `?` used in `fn main()` returning `()`. Compiler help and book
  fix: `fn main() -> Result<(), Box<dyn std::error::Error>>` plus a trailing `Ok(())` (§9.2).
- Mixing `?` on an `Option` inside a `Result`-returning function (or vice versa) does not compile; use
  `ok` / `ok_or` (§9.2).
- `match` with a blanket `Err(error) => panic!(..)` panics for every cause; add an inner match on
  `error.kind()` when different causes need different handling (§9.2).
- A panic location inside library code does not identify your bug; use the backtrace and look at the
  first frame mentioning a file you wrote (§9.1).
- Bare `unwrap` gives only the generic
  ``called `Result::unwrap()` on an `Err` value: ...`` message; no statement of intent (§9.2).
- Repeating the same range check in every function is tedious and may cost performance; move it into a
  validating type (§9.3).
- Parsing a hardcoded valid string still yields a `Result`; the compiler cannot see it never fails (§9.3).

## Idioms and Best Practices

- Production code: most Rustaceans choose `expect` over `unwrap`, with a message explaining why the
  operation is expected to always succeed, e.g. `.expect("hello.txt should be included in this project")`
  or `.expect("Hardcoded IP address should be valid")`. If the assumption breaks, debugging has more
  context, and the stated assumption prompts a rewrite when the value's source changes (§9.2, §9.3).
- Prefer `?` over hand-written `match` + `return Err(e)` for propagation (§9.2).
- Closure-taking `Result` methods such as `unwrap_or_else` can replace large nested `match` trees (§9.2).
- Let the type system do the checks: a non-`Option` parameter means "definitely a value", `u32` means
  never negative. Invalid calls then fail to compile and need no runtime check (§9.3).
- Validation newtype (§9.3): private field, a `new` associated function that checks the invariant, and a
  getter. Code outside the module cannot set the field, so every instance is known to be valid, and
  functions taking or returning the type need no further checks.
  ```rust
  pub struct Guess { value: i32 }
  impl Guess {
      pub fn new(value: i32) -> Guess {
          if value < 1 || value > 100 {
              panic!("Guess value must be between 1 and 100, got {value}.");
          }
          Guess { value }
      }
      pub fn value(&self) -> i32 { self.value }
  }
  ```
- Document function contracts in the API docs, especially conditions under which the function panics. A
  contract violation is a caller-side bug: the calling programmer fixes the code; the calling code has
  no reasonable recovery (§9.3).

## Details Worth Knowing

- The panic output's thread line carries a numeric id in the listings' current output, e.g.
  `thread 'main' (6018279) panicked at src/main.rs:2:5:` (§9.1, listing output).
- `io::Error` debug output looks like
  `Os { code: 2, kind: NotFound, message: "No such file or directory" }` (§9.2).
- A missing first line vs. an empty first line both make `last_char_of_first_line` return `None`
  (`""` and `"\nhi"`): `next()` yields `None` for empty text, `last()` yields `None` for an empty line
  (§9.2).
- `{error:?}` inside `panic!` formats the error with debug formatting (§9.2).
- A method that only returns a field's data is sometimes called a getter (§9.3).
- The book's `Guess` code lives in `src/guessing_game.rs` and needs a `mod guessing_game;` declaration
  (§9.3).
- Forward references: generics (ch. 10); closures and the methods that take them (ch. 13); documenting
  panics in API docs (ch. 14); trait objects and encoding states as types (ch. 18).
