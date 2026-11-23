# Review Checklist - Rust Code Against the Book's Guidance

Source: The Rust Programming Language (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).
Walk every section that applies to the change. Each item is a yes/no check; a "no" needs either
a fix or a stated reason. The ref names the chapter file that explains the rule.

## Ownership and Borrowing (ch04, ch10, ch13)

- [ ] Does each function take a reference unless it truly needs ownership? (§4.3)
- [ ] Are string parameters `&str` rather than `&String`, and sequence parameters slices? (§4.3)
- [ ] Is every `clone` a wanted deep copy, not a way around a borrow error? (§4.1, §12.3)
- [ ] Do functions return owned values for data they create, never references to locals? (§10.3)
- [ ] Are positions in collections returned as slices rather than indices that can go stale? (§4.3)
- [ ] Are lifetime annotations only where elision cannot decide, and only on the parameters
      actually related to the output? (§10.3, §12.4)
- [ ] Is there any `'static` added only because the compiler suggested it? (§10.3)

## Types and Data Modelling (ch03, ch05, ch06, ch09, ch18)

- [ ] Are related values grouped in a struct with named fields instead of a tuple? (§5.2)
- [ ] Is a closed set of alternatives an enum with data in the variants? (§6.1)
- [ ] Is absence an `Option<T>` and never a sentinel value? (§6.1)
- [ ] Is each invariant enforced by a type with a private field and a checking constructor,
      rather than re-validated at every use? (§9.3)
- [ ] Could an invalid state or transition be made unrepresentable by encoding states as
      types? (§18.3)
- [ ] Enum for a closed set, generics for homogeneous static dispatch, `dyn Trait` only for an
      open or heterogeneous set? (§18.2)
- [ ] Are fields private unless they are part of the intended API? (§7.3, §18.1)

## Error Handling (ch09, ch12)

- [ ] Does every operation that can fail in normal use return `Result`? (§9.3)
- [ ] Is each `panic!`, `unwrap`, and `expect` in non-test code justified by a broken invariant
      or by knowledge the compiler lacks? (§9.3)
- [ ] Does each `expect` message say why the value should be present? (§9.2, §9.3)
- [ ] Are errors propagated with `?` instead of hand-written `match` ladders? (§9.2)
- [ ] Are fallible constructors named `build` and returning `Result`, with `new` infallible? (§12.3)
- [ ] Do binaries print errors with `eprintln!` and exit non-zero via `process::exit`? (§12.3, §12.6)

## Control Flow and Patterns (ch03, ch06, ch19)

- [ ] Is `match` used where every case must be handled, so the compiler checks exhaustiveness
      instead of an `if let` chain that silently skips cases? (§6.2, §19.1)
- [ ] Is `let...else` used for extract-or-return instead of nesting the happy path? (§6.3)
- [ ] Are collections walked with `for` rather than index-based `while`? (§3.5)
- [ ] Are unused bindings `_` (does not bind or move) rather than `_name` where a move would
      matter? (§19.3)

## Traits, Generics, Closures, Iterators (ch10, ch13, ch20)

- [ ] Is duplicated logic that differs only by type merged into a generic? (§10.1)
- [ ] Are bounds readable: `impl Trait` for simple cases, `where` for many? (§10.2)
- [ ] Is each callable parameter bounded by how the callee uses it: `FnOnce` if called at most
      once, `FnMut` if called repeatedly? (§13.1)
- [ ] Are loops that push into a mutable vector written as iterator adapter chains? (§13.3)
- [ ] Do functions return `impl Iterator` instead of collecting when the caller may not need
      everything? (§13.3)
- [ ] Is a newtype used where a distinct type, unit, or foreign-trait impl is needed, and a type
      alias only to shorten a name? (§20.2, §20.3)
- [ ] Does each type derive the traits its uses require (`Debug` for `{:?}` and `assert_eq!`,
      `PartialEq` for `==`, `Clone`, `Copy`, `Hash`, `Default` where they apply)? (appendix C)

## Smart Pointers and Concurrency (ch15, ch16, ch17, ch21)

- [ ] Is each `Rc`, `RefCell`, `Arc`, and `Mutex` needed, with the simplest type that works? (§15.5,
      §16.3)
- [ ] Could any `Rc` cycle form, and are back-references `Weak`? (§15.6)
- [ ] Can two `RefCell` borrows overlap at runtime and panic? (§15.5)
- [ ] Is every spawned thread that must finish joined through its `JoinHandle`? (§16.1)
- [ ] Is each `MutexGuard` dropped before slow work, with no lock held across a long job or an
      unintended `while let` scope? (§16.3, §21.2)
- [ ] Does any operation need two locks at once (deadlock risk)? (§16.3)
- [ ] Does async code avoid blocking or long CPU work between await points? (§17.3)
- [ ] Is thread or task creation bounded under load? (§21.2)
- [ ] Does shutdown close channels and join workers in `Drop`? (§21.3)

## Modules, API, Docs (ch07, ch14)

- [ ] Is everything private by default, with `pub` only on the intended API? (§7.3)
- [ ] Does `pub use` present the API users expect, independent of internal layout? (§14.2)
- [ ] `use` idioms: parent module for functions, full path for types? (§7.4)
- [ ] Does every public item have a `///` comment, with `# Examples` and, where relevant,
      `# Panics`, `# Errors`, `# Safety` sections? (§14.2)
- [ ] Is logic in `lib.rs` with a thin `main.rs`? (§12.3)

## Tests (ch11, ch12)

- [ ] Is there a unit test for each behaviour, in a `#[cfg(test)]` module beside the code? (§11.3)
- [ ] Do integration tests in `tests/` exercise the public API only? (§11.3)
- [ ] Are error paths tested (`should_panic` with `expected`, or `Result` assertions)? (§11.1)
- [ ] Are tests independent of each other and of run order, sharing no state? (§11.2)
- [ ] Do assertions use `assert_eq!` / `assert_ne!` so failures print both values? (§11.1)

## Unsafe and Macros (ch20)

- [ ] Is each `unsafe` block as small as possible and wrapped in a safe abstraction? (§20.1)
- [ ] Does each `unsafe` block or function carry a `SAFETY` comment or `# Safety` doc stating
      the upheld or required invariants? (§20.1)
- [ ] Has code containing `unsafe` been run under Miri? (§20.1)
- [ ] Is there any `static mut` that an atomic or `Mutex` could replace? (§20.1)
- [ ] Is each macro doing something a function cannot (variadic input, code generation)? (§20.5)

## Tooling Gate

- [ ] `cargo fmt` leaves no diff, `cargo clippy` is clean, `cargo test` passes (appendix D, §11.2).
- [ ] `Cargo.toml` has the intended `edition`, and metadata if the crate is published (§14.2).
