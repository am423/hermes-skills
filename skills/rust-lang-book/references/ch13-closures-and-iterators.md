# Ch 13 - Functional Language Features: Iterators and Closures

Source: The Rust Programming Language ch. 13 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- Closure: anonymous function that can be stored in a variable or passed as an argument, created in one
  place and called elsewhere. Unlike `fn` functions, closures can capture values from the scope where
  they are defined (§13.1).
- Capture is decided twice (§13.1):
  - what moves INTO the closure: how it captures (immutable borrow, mutable borrow, ownership);
  - what moves OUT of the closure: what the body does with captured values when it runs. This second
    aspect determines which `Fn` traits the closure implements.
- Iterator: a value responsible for the logic of walking a sequence and deciding when it is finished,
  so that logic is not reimplemented by hand (§13.2).
- Iterators are lazy: they have no effect until a method that consumes them is called (§13.2).
- Two kinds of `Iterator` methods (§13.2):
  - consuming adapters: call `next`, use the iterator up (e.g. `sum`, `collect`);
  - iterator adapters: do not consume; produce a different iterator (e.g. `map`, `filter`).
- Zero-cost abstraction: using the abstraction imposes no additional runtime overhead; iterators
  compile down to roughly the code you would write by hand at the lower level (§13.4).

## Rules and Semantics

### Closure types and inference (§13.1)

- Parameter and return type annotations are usually not required on closures. Functions need them
  because their types are part of an explicit interface exposed to users; closures are short, used in
  a narrow context, and not exposed that way, so the compiler infers types (rarely it still needs
  annotations).
- Annotations may be added for explicitness at the cost of verbosity.
- The compiler infers ONE concrete type per parameter and for the return value. The first call fixes
  those types; they are then locked into the closure. Calling it again with another type is an error.
- Unannotated closure definitions need to be used (called) somewhere for the code to compile, because
  types come from usage -- like `let v = Vec::new();` needing an annotation or inserted values.
- Braces around the body are optional when the body is a single expression.
- A closure with no parameters is written with empty pipes: `|| expr`.
- A variable bound to a closure is called with the variable name and parentheses, like a function.

### Capture modes (§13.1)

- Three ways to capture, mirroring the three ways a function takes a parameter: borrow immutably,
  borrow mutably, take ownership. The closure picks based on what the body does with the value, using
  the least access needed.
- Immutable-borrow capture: the captured variable stays usable before the definition, between
  definition and call, and after the call (multiple immutable references are allowed).
- Mutable-borrow capture: the mutable borrow starts at the closure DEFINITION and ends after the
  closure's last use. No other borrow (e.g. a `println!` of the value) is allowed between definition
  and call. The closure binding itself must be `let mut`.
- `move` before the parameter list forces the closure to take ownership of the values it uses, even
  when the body does not strictly need ownership.
- Main use of `move`: passing a closure to a new thread so the thread owns the data. Without it the
  spawned thread could outlive the owner (main might finish first and drop the value), leaving the
  borrowed reference invalid, so the compiler requires the move.

### The `Fn` traits (§13.1)

Closures automatically implement one, two, or all three, additively, based on how the body handles
captured values:

| Trait | Body behaviour | Calls |
|---|---|---|
| `FnOnce` | any closure; one that moves captured values OUT implements only this | once |
| `FnMut` | does not move captured values out, may mutate them | many |
| `Fn` | neither moves out nor mutates, or captures nothing | many, incl. concurrently |

- All closures implement at least `FnOnce`, because every closure can be called.
- `Fn` closures can be called repeatedly without mutating their environment, which matters when a
  closure is called multiple times concurrently.
- Trait bounds on a generic parameter are how functions and structs say which closures they accept.
- A bound of `FnOnce` states that the callee calls the closure at most once; since all closures
  implement it, that bound accepts all three kinds and is the most flexible.
- A function name can be used wherever something implementing an `Fn` trait is required, provided no
  environment capture is needed; the compiler implements whichever `Fn` traits apply to a function
  definition. Example: `unwrap_or_else(Vec::new)` on an `Option<Vec<T>>`.

### The `Iterator` trait (§13.2)

- Every iterator implements `Iterator`; implementors must define the associated type `Item` and one
  method, `next`. Other methods have default implementations, some of which call `next`.
- `next` returns one item at a time wrapped in `Some`, and `None` once iteration is over.
- Calling `next` changes internal state, so the iterator binding must be `mut`. Each call consumes an
  item.
- A `for` loop takes ownership of the iterator and makes it mutable behind the scenes, so no `mut` is
  needed there. `for` loops implicitly create and consume an iterator.
- A consuming adapter such as `sum` takes ownership of the iterator; the iterator cannot be used
  afterwards.
- Because adapters are lazy, a chain of adapters does nothing until a consuming adapter is called.
- Closures passed to adapters commonly capture their environment (e.g. `filter` comparing against a
  local variable or function parameter).

## Syntax and API Reference

Closure syntax compared with a function (§13.1):

```rust
fn  add_one_v1   (x: u32) -> u32 { x + 1 }
let add_one_v2 = |x: u32| -> u32 { x + 1 };
let add_one_v3 = |x|             { x + 1 };
let add_one_v4 = |x|               x + 1  ;
```

Capture forms (§13.1):

```rust
let only_borrows = || println!("From closure: {list:?}");      // immutable borrow
let mut borrows_mutably = || list.push(7);                     // mutable borrow
thread::spawn(move || println!("From thread: {list:?}")).join().unwrap();  // ownership
```

Trait definition and a std signature using a closure bound (§13.1, §13.2):

```rust
pub trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
    // methods with default implementations elided
}

impl<T> Option<T> {
    pub fn unwrap_or_else<F>(self, f: F) -> T
    where
        F: FnOnce() -> T
    { /* Some(x) => x, None => f() */ }
}
```

| Item | What the chapter says | Ref |
|---|---|---|
| `Option::unwrap_or_else(f)` | returns the `Some` value, else calls `f` and returns its result | §13.1 |
| `slice.sort_by_key(\|r\| r.width)` | closure gets a reference to the current item and returns an | §13.1 |
| | orderable key `K`; bound is `FnMut` because it is called once per item | |
| `v.iter()` | iterator over immutable references (`next` yields `Some(&1)` ...) | §13.2 |
| `v.into_iter()` | iterator that takes ownership of `v` and yields owned values | §13.2 |
| `v.iter_mut()` | iterator over mutable references | §13.2 |
| `iter.next()` | `Option<Self::Item>`; `None` at the end | §13.2 |
| `iter.sum()` | consuming adapter; `let total: i32 = v1_iter.sum();` | §13.2 |
| `iter.map(\|x\| x + 1)` | adapter; new iterator yielding the closure's results | §13.2 |
| `iter.filter(\|s\| ...)` | adapter; closure returns `bool`, `true` keeps the item | §13.2 |
| `iter.collect()` | consuming adapter; gathers items into a collection, e.g. | §13.2 |
| | `let v2: Vec<_> = v1.iter().map(\|x\| x + 1).collect();` | |
| `env::args()` | returns `std::env::Args`, an iterator yielding `String` | §13.3 |
| `contents.lines()` | iterator over lines, usable with `filter`/`collect` | §13.3 |

Iterator in a signature (§13.3):

```rust
fn build(mut args: impl Iterator<Item = String>) -> Result<Config, &'static str> {
    args.next();                                   // skip program name
    let query = match args.next() {
        Some(arg) => arg,
        None => return Err("Didn't get a query string"),
    };
    // ...
}

pub fn search<'a>(query: &str, contents: &'a str) -> Vec<&'a str> {
    contents.lines().filter(|line| line.contains(query)).collect()
}
```

## Decision Rules

- Pick the closure bound by how often the callee invokes it: `FnOnce` if at most once (accepts every
  closure), `FnMut` if it is called repeatedly, as `sort_by_key` does once per slice item (§13.1).
- Use `move` when the closure must own its data, chiefly when handing it to a new thread (§13.1).
- Pass a function name instead of a closure when nothing needs capturing (§13.1).
- `iter` for shared references, `iter_mut` for mutable references, `into_iter` to take ownership and
  get owned values (§13.2).
- Take an owned iterator (`impl Iterator<Item = String>`) instead of a borrowed slice (`&[String]`)
  when the function needs to own the elements: values are moved out rather than cloned, avoiding the
  extra allocation, and length checks plus indexing disappear (§13.3).
- Prefer iterator adapter chains over a loop that pushes into a mutable vector: more concise, and no
  mutable intermediate state. Most Rust programmers prefer the iterator style (§13.3).
- Return `impl Iterator<Item = &'a str>` (drop the `collect`) to make a function itself an iterator
  adapter; callers then get each result as it is found instead of after everything is collected
  (§13.3).
- Do not choose a hand-written loop for speed: the two forms perform about the same (§13.4).

## Pitfalls and Compiler Errors

- E0308 `mismatched types` (§13.1): `let example_closure = |x| x;` called with a `String` and then
  with `5`. The first call locks the parameter and return type to `String`; the note says the type was
  expected because of the earlier call. Each closure has one concrete type per parameter.
- E0507 `cannot move out of `value`, a captured variable in an `FnMut` closure` (§13.1): a closure
  given to `sort_by_key` did `sort_operations.push(value)` with a captured `String`, which moves the
  value out, so the closure is only `FnOnce`, while the bound needs `FnMut`. The compiler suggests
  cloning if the cost is acceptable. The book's fix: do not move out of the environment -- keep a
  counter outside and do `num_sort_operations += 1;` in the body (a mutable-borrow capture).
- Borrowing between a mutably-capturing closure's definition and its call is rejected: no other
  borrows while the mutable borrow is live (§13.1).
- Omitting `move` on a closure passed to `thread::spawn`, or using the moved value in the main thread
  after the closure is defined, produces compiler errors (§13.1).
- Warning `unused `Map` that must be used` with note `iterators are lazy and do nothing unless
  consumed` (lint `unused_must_use`) (§13.2): `v1.iter().map(|x| x + 1);` alone never runs the
  closure. Fix: consume it, e.g. with `collect`.
- Using an iterator after a consuming adapter such as `sum` is not allowed; it was moved (§13.2).
- Forgetting `mut` on an iterator binding (or parameter) on which `next` is called directly (§13.2,
  §13.3).

## Idioms and Best Practices

- Define short closures inline at the call site: `user_preference.unwrap_or_else(|| self.most_stocked())`.
  The closure captures an immutable reference to `self`; the library code needs no knowledge of the
  caller's types (§13.1).
- Use closures to customise behaviour while reusing the iteration logic `Iterator` provides (§13.2).
- Chain several adapters for complex operations, ending with a consuming adapter (§13.2).
- Annotate the target collection where `collect` needs it; `Vec<_>` lets the element type be inferred
  (§13.2).
- Functional style minimises mutable state for clarity. Removing a mutable accumulator may also make
  later parallelisation easier, since there is no concurrent access to manage (§13.3).
- Iterator code states the high-level objective (e.g. the filter condition) rather than the loop
  bookkeeping and vector building (§13.3).
- Pass `env::args()` directly to the function that parses it instead of collecting to a `Vec` and
  passing a slice; call `next` once and discard the result to skip the program name (§13.3).
- Return a descriptive `Err` when `next` yields `None` for a required argument (§13.3).

## Details Worth Knowing

- `type Item` / `Self::Item` is associated-type syntax; covered in depth in Chapter 20 (§13.2).
- Threads and why `move` matters for them are covered in Chapter 16 (§13.1).
- `impl Trait` parameter syntax comes from Chapter 10, "Using Traits as Parameters" (§13.3).
- Iterators work with many kinds of sequences, not only indexable structures like vectors (§13.2).
- Benchmark in the book (searching for "the" in the full text of The Adventures of Sherlock Holmes):
  `for` loop 19,620,300 ns/iter (+/- 915,700) vs iterators 19,234,900 ns/iter (+/- 657,200) (§13.4).
- Optimisations such as loop unrolling and eliminating bounds checks on array access apply to
  iterator code; in many cases it compiles to the same assembly as hand-written code (§13.4).
- The book ties "zero-cost" to Stroustrup's zero-overhead principle: what you don't use you don't pay
  for, and what you do use you couldn't hand code any better (§13.4).
- Pattern matching and enums are also described as functional-style influences on Rust (§13.0).
