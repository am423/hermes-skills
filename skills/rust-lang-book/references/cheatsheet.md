# Cheatsheet - Cross-Chapter Decision Tables and Error Index

Source: The Rust Programming Language (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).
Every row is the book's own guidance; the ref names the chapter file that holds the detail.

## Passing and Returning Data (ch04, ch10, ch13)

| Situation | Do this |
|---|---|
| Function only reads a value | Take `&T`; do not take ownership unless needed (§4.3) |
| Function mutates the caller's value | Take `&mut T` (§4.2) |
| String parameter | `&str`, not `&String`: accepts literals, slices, and `&String` (§4.3) |
| Function returns data it creates | Return the owned value, never a reference to a local (§4.2, §10.3) |
| Position inside a collection | Return a slice, not an index that can go stale (§4.3) |
| Function must own the elements | Take `impl Iterator<Item = T>` instead of a slice and cloning (§13.3) |
| Tempted to `clone` | Only for a real deep copy; fine for a few small values on a first pass (§4.1, §12.3) |
| Compiler suggests `'static` | Usually a dangling reference or lifetime mismatch; fix that instead (§10.3) |
| Returning a tuple just to hand ownership back | Use a reference parameter (§4.2) |

## Choosing a Data Shape (ch03, ch05, ch06, ch08, ch18)

| Need | Use |
|---|---|
| Related values with meaning | Struct with named fields, not a tuple or loose variables (§5.2) |
| Distinct type around a tuple, names redundant | Tuple struct (§5.1) |
| Type with no data that implements a trait | Unit-like struct (§5.1) |
| Value is one of a fixed set of kinds | Enum with data in the variants (§6.1) |
| Value may be absent | `Option<T>`; plain `T` everywhere else (§6.1) |
| Fixed element count or stack data | Array; otherwise, and when unsure, `Vec<T>` (§3.2) |
| Mixed types in a vector, set known at compile time | Enum (§8.1) |
| Mixed types, set open or user-extensible | Trait objects, `Vec<Box<dyn Trait>>` (§8.1, §18.2) |
| Homogeneous collection of one generic type | Generics with trait bounds: static dispatch (§18.2) |
| Lookup by key rather than index | `HashMap<K, V>` (§8.3) |
| Struct should own its data | Owned fields (`String`); reference fields need lifetimes (§5.1) |
| Integer type, unsure | `i32`; `usize`/`isize` mainly for indexing (§3.2) |

## Smart Pointers and Sharing (ch15, ch16)

| Type | Owners | Borrows | Checked | Threads |
|---|---|---|---|---|
| `Box<T>` | single | immutable or mutable | compile time | - |
| `Rc<T>` | multiple | immutable only | compile time | single-threaded only |
| `RefCell<T>` | single | immutable or mutable | runtime (panics) | single-threaded only |
| `Arc<T>` | multiple | immutable only | compile time | thread-safe `Rc<T>` |
| `Mutex<T>` | - | mutable through the lock | runtime (lock) | thread-safe `RefCell<T>` |

- `Box<T>`: recursive types, moving large data without copying, owning a trait object (§15.1).
- `Rc<T>`: several readers and no compile-time answer to who finishes last (§15.4).
- `RefCell<T>`: you know the borrow rules hold but the compiler cannot verify it; compile-time
  checking stays the default (§15.5). Shared plus mutable: `Rc<RefCell<T>>` (§15.5).
- `Weak<T>`: non-owning back-reference (child to parent) to avoid reference cycles (§15.6).
- Across threads: `Arc<Mutex<T>>`; do not default to `Arc<T>`, it costs performance (§16.3).
- Simple numeric shared state: `std::sync::atomic` types over `Mutex<T>` (§16.3).

## Errors (ch09, ch12, ch21)

| Situation | Do this |
|---|---|
| Function might fail | Return `Result`: the default (§9.3) |
| Failure is expected (bad input, rate limit) | `Result` (§9.3) |
| Broken invariant or contract, unexpected, cannot be encoded in types | `panic!` (§9.3) |
| Continuing could be insecure or harmful | Validate, then panic (§9.3) |
| Examples, prototypes, tests | `unwrap` / `expect` are fine (§9.3) |
| You know more than the compiler | `expect` with a message saying why it cannot fail (§9.3) |
| Production code choosing between the two | `expect` over `unwrap` (§9.2) |
| Propagating | `?`; return type must be compatible (`Result`, `Option`) (§9.2) |
| Constructor can fail | Name it `build` and return `Result`; `new` is expected not to fail (§12.3) |
| Invariant on a value | Type with private field + validating constructor (§9.3) |
| Smallest binary | `panic = 'abort'` in the profile (§9.1) |

## Control Flow and Patterns (ch03, ch06, ch19)

| Need | Use |
|---|---|
| Every case handled, compiler-checked | `match` (§6.2, §19.1) |
| Only one case matters | `if let`: shorter, loses exhaustiveness checking (§6.3) |
| Extract a value or bail out early | `let...else`: keeps the happy path unindented (§6.3, §19.2) |
| More than one `else if` | Refactor, typically to `match` (§3.5) |
| Catch-all arm | Named binding if the value is used, `_` if not (§6.2) |
| Many alternative values | Range `1..=5` rather than listing each value with the or operator (§19.3) |
| Compare with an outer variable | Match guard (§19.3) |
| Test a value and keep it | `name @ pattern` (§19.3) |
| Ignore the rest of a struct or tuple | `..` (§19.3) |
| Walk a collection | `for`, not an index-based `while` (§3.5) |
| Retry until success, value out of the loop | `loop` with `break value` (§3.5) |

## Traits, Generics, Closures (ch10, ch13, ch20)

| Need | Use |
|---|---|
| Simple bound on one parameter | `impl Trait` (§10.2) |
| Two parameters forced to the same type, or many bounds | Trait-bound syntax; `where` clause (§10.2) |
| Hide a concrete return type (closures, iterators) | Return `impl Trait` (§10.2, §13.3) |
| Return one of several types | Trait object (§10.2, ch18) |
| One implementation of a trait per type | Associated type; several: generic parameter (§20.2) |
| External trait on an external type, units, encapsulation | Newtype (§20.2, §20.3) |
| Shorten a long type only | Type alias: no extra type checking (§20.3) |
| Parameter that accepts a callable | Generic bounded by a closure trait; `fn` only for FFI (§20.4) |
| Callee calls it at most once / repeatedly | `FnOnce` / `FnMut` (§13.1) |
| Closure must own its captures (threads) | `move` (§13.1, §16.1) |
| Return a closure | `impl Fn...`; `Box<dyn Fn...>` when several must share a type (§20.4) |
| Loop that pushes into a `mut` vector | Iterator adapter chain; same speed (§13.3, §13.4) |
| Too many generic parameters | Split the code into smaller pieces (§10.1) |

## Concurrency (ch16, ch17, ch21)

| Need | Use |
|---|---|
| Very parallelizable, CPU-bound work | Threads (§17.6) |
| Very concurrent, I/O-bound work | Async (§17.6) |
| Both | Combine: blocking work on a thread, results over an async channel (§17.6) |
| Hand data between threads | Channels (`mpsc`) (§16.2) |
| Threads updating one shared result | `Arc<Mutex<T>>` (§16.3) |
| Thread must finish | Keep the `JoinHandle` and `join` it (§16.1) |
| Receiver has other work between checks | `try_recv`; otherwise `recv` (§16.2) |
| Two futures / fixed count / runtime-sized collection | `join` / `join!` / `join_all` (§17.2, §17.5) |
| Only the first result matters | `select` (§17.3) |
| Let other futures run | `yield_now`, not `sleep` (§17.3) |
| Value must drop when an async block ends | `async move` (§17.2) |
| Unbounded request load | Fixed-size thread pool, not a thread per request (§21.2) |
| Custom `Send`/`Sync` | Avoid; needs unsafe and care (§16.4) |

## Modules, Tests, Cargo, Unsafe, Macros

- Paths: prefer absolute; `super::` when module and parent move together (§7.3).
- `use` the parent module for functions, the full path for structs and enums; `as` or parent
  modules for name clashes (§7.4). `pub use` to expose a friendlier API than the internal layout
  (§7.4, §14.2).
- Files: `src/name.rs`, not `src/name/mod.rs` (§7.5).
- Binary crates: thin `main.rs`, logic in `lib.rs` so it can be tested (§12.3).
- Tests: `assert_eq!`/`assert_ne!` over `assert!(a == b)`; unit tests in a `#[cfg(test)]` module
  next to the code, integration tests in `tests/` (§11.1, §11.3). Slow tests: `#[ignore]` (§11.2).
- CLI: errors to stderr with `eprintln!`, results to stdout (§12.6). Env var for a setting that
  should hold across runs in a session (§12.5).
- Cargo: `cargo check` while writing, `--release` for benchmarks (§1.3); workspace when crates
  change together (§14.3); `///` for items, `//!` for the crate or module (§14.2).
- Unsafe: only for what the compiler cannot prove; wrap it in a safe abstraction; `&raw const` /
  `&raw mut` for raw pointers; run Miri (§20.1). No `static mut` when ch. 16 tools suffice (§20.1).
- Macros: only for variadic arguments or compile-time code generation; otherwise a function (§20.5).

## Compiler Error Index

Load the named file for cause and fix. Codes are those shown in the book's compiler output.

| Code | Meaning in the book | File |
|---|---|---|
| E0004 | non-exhaustive `match` patterns | ch06 |
| E0005 | refutable pattern in `let` | ch19 |
| E0040 | explicit call of the `drop` destructor method | ch15 |
| E0072 | recursive type has infinite size | ch15 |
| E0106 | missing lifetime specifier | ch04, ch05, ch10, ch12 |
| E0133 | unsafe call outside an `unsafe` block | ch20-unsafe |
| E0277 | trait bound not satisfied (`Display`, `?`, `Send`, `Unpin`, indexing `str`) | ch05, ch06, ch08, ch09, ch15, ch16, ch17, ch18, ch20 |
| E0284 | type annotations needed | ch03 |
| E0308 | mismatched types | ch01-02, ch03, ch10, ch13, ch19, ch20 |
| E0369 | binary operator on an unbounded generic | ch10 |
| E0373 | closure may outlive borrowed value (needs `move`) | ch16 |
| E0382 | use or borrow of moved value | ch04, ch15, ch16, ch21 |
| E0384 | assign twice to immutable variable | ch03 |
| E0432 | unresolved import (crate missing from a member's manifest) | ch14 |
| E0433 | unresolved module, crate, or type | ch07, ch21 |
| E0499 | second mutable borrow | ch04, ch20-unsafe |
| E0502 | mutable borrow while immutably borrowed | ch04, ch08 |
| E0507 | move out of a borrow or captured variable | ch13, ch21 |
| E0515 | returning a reference to a local | ch10 |
| E0596 | mutable borrow of something not mutable | ch04, ch15 |
| E0597 | value does not live long enough | ch10 |
| E0599 | method or associated function not found (trait not in scope) | ch17, ch21 |
| E0603 | private item on the path | ch07 |
| E0614 | type cannot be dereferenced (no `Deref`) | ch15 |
| E0752 | `main` cannot be `async` | ch17 |
| E0790 | cannot infer type for an associated function call | ch20-advanced |
