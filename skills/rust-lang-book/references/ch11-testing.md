# Ch 11 - Writing Automated Tests

Source: The Rust Programming Language ch. 11 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- Correctness = the extent to which code does what we intend. The type system and borrow checker catch a
  large class of bugs but cannot check that logic does what was intended (e.g. `add_two` returning +10);
  tests cover that gap (§11.0).
- A test is a Rust function that verifies non-test code. Typical body: (1) set up data/state, (2) run the
  code under test, (3) assert the results are as expected (§11.1).
- A test is any function annotated `#[test]`. `cargo test` builds a test runner binary that runs every
  annotated function and reports pass/fail per function (§11.1).
- A test fails when something in the test function panics. Each test runs in a new thread; when the main
  thread sees a test thread has died, the test is marked failed (§11.1).
- Two test categories used by the Rust community (§11.3):
  - Unit tests: small, focused, one module in isolation, may test private interfaces. Live in `src`.
  - Integration tests: entirely external to the library, use only the public API like any other external
    code, may exercise several modules per test. Live in top-level `tests/`.
- `cargo test` compiles code in test mode and runs the resulting test binary; by default tests run in
  parallel and output of passing tests is captured (§11.2).

## Rules and Semantics

### Test functions and the generated template (§11.1)
- `cargo new adder --lib` generates a `#[cfg(test)] mod tests` containing `use super::*;` and one
  `#[test] fn it_works()` using `assert_eq!`; it is a template so the structure need not be looked up.
- Any number of test functions and test modules is allowed. Non-test helper functions may live in the
  `tests` module, which is why each test needs its own `#[test]`.
- `tests` is an ordinary inner module with normal visibility rules (ch. 7); `use super::*;` (a glob)
  brings everything defined in the outer module into scope.
- Test names are reported with their module path, e.g. `tests::it_works`.

### Assertion macros (§11.1)
- `assert!(cond)`: takes a Boolean; `true` -> nothing happens, `false` -> calls `panic!`. Failure only
  reports that the expression was false (e.g. `assertion failed: result.contains("Carol")`), not values.
- `assert_eq!(a, b)` / `assert_ne!(a, b)`: compare with `==` / `!=` and on failure print both values with
  debug formatting, labelled `left` and `right`.
- Argument order does not matter in Rust: there is no `expected`/`actual` convention, only `left`/`right`.
  `assert_eq!(4, result)` gives the same `` assertion `left == right` failed `` message.
- Compared values must implement `PartialEq` and `Debug`. All primitives and most std types do; for your
  own structs/enums add `#[derive(PartialEq, Debug)]` (Appendix C lists derivable traits).
- Custom messages: any arguments after the required ones are passed to `format!`, so a format string with
  `{}` placeholders plus values is accepted by `assert!`, `assert_eq!`, and `assert_ne!`.

### `should_panic` (§11.1)
- `#[should_panic]` goes after `#[test]` and before the function. Test passes if the body panics, fails if
  it does not.
- Imprecise by default: passes even when the panic comes from a different cause than intended.
- `#[should_panic(expected = "...")]`: the harness checks that the panic message *contains* the given
  text (substring match). How much of the message to give depends on how much of it is unique or
  dynamic and how precise the test should be.

### `Result<T, E>` tests (§11.1)
- A test may return `Result<T, E>` (e.g. `Result<(), String>`): return `Ok(())` to pass, `Err(..)` to fail.
- This enables the `?` operator in the test body: the test fails if any step returns `Err`.
- `#[should_panic]` cannot be used on tests that return `Result<T, E>`.
- To assert that an operation returns `Err`, do not use `?` on it; use `assert!(value.is_err())`.

### Running tests (§11.2)
- Argument split: options for `cargo test` come first, then the separator `--`, then options for the test
  binary. `cargo test --help` lists the former; `cargo test -- --help` the latter (also documented in the
  "Tests" section of The `rustc` Book).
- Parallelism: tests run in parallel on threads by default, so they must not depend on each other or on
  shared state, including shared environment such as the current working directory or env variables.
- Output capture: stdout of a passing test (e.g. `println!`) is captured and not shown; stdout of a
  failing test is printed along with the failure message.
- Name filtering: a single positional argument selects tests whose name matches it. Only the first value
  given is used, so multiple names cannot be listed; use a partial name instead (substring match).
- The module path is part of the test name, so filtering on a module name runs all tests in that module.
- `#[ignore]` (placed after `#[test]`) excludes a test from normal runs; it is listed as `ignored`.

### Organization (§11.3)
- `#[cfg(test)]` on the `tests` module: compile and run that code only under `cargo test`, not
  `cargo build`. Saves compile time and artifact size. `cfg` = configuration; the item is included only
  when the given configuration option (`test`) is set. Covers helper functions in the module too.
- Private functions can be tested: child modules can use items in their ancestor modules, so
  `use super::*` makes a non-`pub` function callable from `tests`. Rust does not force you to do so.
- `tests/` directory sits at the project top level next to `src`. Cargo compiles each file in it as an
  individual crate, and only when running `cargo test`; no `#[cfg(test)]` needed there.
- Because each integration test file is its own crate, it must import the library:
  `use adder::add_two;`. Only the library's public API is reachable.
- `cargo test` output has three sections in order: unit tests, integration tests (one section per file,
  headed `Running tests/<file>.rs`), then `Doc-tests <crate>`. If any test in a section fails, the
  following sections are not run.
- Files in subdirectories of `tests/` are not compiled as separate crates and get no output section.

## Syntax and API Reference

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_adds_two() { assert_eq!(add_two(2), 4); }

    #[test]
    #[should_panic(expected = "less than or equal to 100")]
    fn greater_than_100() { Guess::new(200); }

    #[test]
    fn it_works() -> Result<(), String> {
        if add(2, 2) == 4 { Ok(()) } else { Err(String::from("two plus two does not equal four")) }
    }

    #[test]
    #[ignore]
    fn expensive_test() { /* slow */ }
}
```

```rust
assert!(result.contains("Carol"), "Greeting did not contain name, value was `{result}`");
```

| Attribute / macro | Meaning (§11.1-11.3) |
|---|---|
| `#[test]` | marks a function as a test |
| `#[should_panic]`, `#[should_panic(expected = "..")]` | pass only if body panics (with substring) |
| `#[ignore]` | skip unless specifically requested |
| `#[cfg(test)]` | compile item only in test configuration |
| `assert!`, `assert_eq!`, `assert_ne!` | assertions; optional trailing `format!` arguments |

| Command | Effect (§11.2, §11.3) |
|---|---|
| `cargo test` | run all tests (unit, integration, doc) |
| `cargo test -- --test-threads=1` | no parallelism; or set another thread count |
| `cargo test -- --show-output` | also show stdout of passing tests |
| `cargo test one_hundred` | run the test(s) whose name matches |
| `cargo test add` | run every test with `add` in its name |
| `cargo test -- --ignored` | run only ignored tests |
| `cargo test -- --include-ignored` | run all tests, ignored or not |
| `cargo test --test integration_test` | run only `tests/integration_test.rs` |
| `cargo test --help` / `cargo test -- --help` | options for cargo / for the test binary |

Summary line format: `test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out`.
`measured` counts benchmark tests, which are only available in nightly Rust as of the text (§11.1).

Shared integration-test helpers (§11.3):

```text
tests/
├── common/
│   └── mod.rs          // pub fn setup() { ... }
└── integration_test.rs // mod common;  ... common::setup();
```

## Decision Rules

- Use `assert!` for Boolean conditions (negate with `!` when the correct result is `false`); prefer
  `assert_eq!`/`assert_ne!` over `assert!(a == b)` because they print both values on failure (§11.1).
- Use `assert_ne!` when you cannot know what a value will be but know what it must not be, e.g. a
  function guaranteed to change its input in a way that varies between runs (§11.1).
- Assert on a looser property (e.g. `contains`) instead of exact equality when requirements are still
  likely to change, so the test need not be rewritten (§11.1).
- Add a custom failure message when the default one would not show the value needed to debug (§11.1).
- Use `should_panic` to check that error conditions are handled, and add `expected` to make sure the
  panic is the intended one (§11.1).
- Use `Result`-returning tests when `?` makes the test body more convenient (§11.1).
- Tests sharing state (e.g. all writing the same file `test-output.txt`): either give each test its own
  resource (a different file) or run with `--test-threads=1` (§11.2).
- Mark time-consuming tests `#[ignore]` rather than listing the tests you do want; run them with
  `-- --ignored` when there is time to wait (§11.2).
- Write both unit and integration tests: units that work alone can still fail when combined (§11.3).

## Pitfalls and Compiler Errors

- Bare `#[should_panic]` passes on any panic, including an unrelated one (§11.1). Failure outputs:
  - no panic: `note: test did not panic as expected at src/lib.rs:21:8`
  - wrong message: `note: panic did not contain expected string`, followed by `panic message:` and
    `expected substring:` lines.
- `assert_eq!` on a type lacking `PartialEq` or `Debug` will not work; derive both (§11.1).
- Passing several test names to `cargo test` silently uses only the first (§11.2).
- Expecting `println!` output from a passing test: it is captured unless `--show-output` (§11.2).
- Parallel tests interfering through shared files, cwd, or env variables fail for reasons unrelated to
  the code's correctness (§11.2).
- `tests/common.rs` is treated as an integration test crate and shows up in output with
  `running 0 tests`; use `tests/common/mod.rs` instead (§11.3).
- A binary-only crate (`src/main.rs` without `src/lib.rs`) cannot be integration-tested: its functions
  cannot be brought into scope with `use`, since only library crates expose functions to other crates
  (§11.3).
- Failed runs end with `error: test failed, to rerun pass `--lib`` for unit tests (§11.1 output).

## Idioms and Best Practices

- Convention: in each `src` file, a module named `tests` annotated `#[cfg(test)]` holding that file's unit
  tests, next to the code it tests (§11.3).
- Name tests for the behavior checked: `larger_can_hold_smaller`, `smaller_cannot_hold_larger`,
  `greeting_contains_name`, `greater_than_100` (§11.1).
- Keep `src/main.rs` small and put logic in `src/lib.rs` so integration tests can `use` it; the thin
  `main.rs` then does not need testing (§11.3).
- Group integration tests into multiple files by the functionality they test; each file being a separate
  crate imitates how end users consume the crate (§11.3).
- Custom assertion messages document what an assertion means (§11.1).

## Details Worth Knowing

- Failure output has two extra sections: per-test detail (panic message and `src/lib.rs:LINE:COL`), then
  a list of just the failing test names, usable as a filter to rerun one (§11.1).
- Panic lines look like `thread 'tests::another' (6019162) panicked at src/lib.rs:17:9:` and suggest
  `RUST_BACKTRACE=1` (§11.1 output).
- A `should_panic` test is displayed as `test tests::greater_than_100 - should panic ... ok` (§11.1).
- When filtering, tests not run are counted as `N filtered out`; under `-- --ignored` the non-ignored
  tests are counted as filtered out (§11.2).
- `Doc-tests` section: Rust compiles code examples in API documentation, keeping docs and code in sync;
  covered in ch. 14 "Documentation Comments as Tests" (§11.1).
- `tests/common/mod.rs` uses the older module-file naming convention (ch. 7 "Alternate File Paths"); it
  tells Rust not to treat `common` as an integration test file (§11.3).
- Whether private functions should be tested directly is debated; Rust's privacy rules permit it but do
  not require it (§11.3).
- Tests run under the `test` profile: `Finished `test` profile [unoptimized + debuginfo]` (§11.1 output).
- Forward reference: ch. 12 applies these techniques (TDD) to a real project.
