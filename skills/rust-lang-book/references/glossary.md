# Glossary - Term to Reference File

Source: The Rust Programming Language (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).
One-line meaning as the book uses the term, then the reference file with the full treatment.

| Term | Meaning | File |
|---|---|---|
| associated function | Function in an `impl` block; without `self` it is called with `::` | ch05 |
| associated type | Type placeholder in a trait, fixed once per implementation | ch20-advanced |
| async / await | Mark code as pausable; `expr.await` is the only pause point | ch17 |
| attribute-like macro | Procedural macro that defines a new attribute usable on any item | ch20-macros |
| binary crate / library crate | Crate with `main` that builds an executable / crate with no `main` | ch07 |
| blanket implementation | Trait implemented for every type satisfying a bound | ch10 |
| borrowing | Creating a reference; the borrower does not own the value | ch04 |
| borrow checker | Compiler pass comparing scopes to validate every borrow | ch10 |
| closure | Anonymous function that can capture its environment | ch13 |
| coherence / orphan rule | A trait impl needs the trait or the type to be local to the crate | ch10 |
| crate root | Source file the compiler starts from; root module of the crate | ch07 |
| dangling reference | Reference to memory that was given away; rejected at compile time | ch04 |
| declarative macro | `macro_rules!` macro: match-like patterns over code | ch20-macros |
| deref coercion | Automatic `&T` to `&U` conversion through `Deref` in calls | ch15 |
| derive macro | Procedural macro generating a trait impl from `#[derive]` | ch20-macros, appendix |
| diverging function | Function returning the never type `!` | ch20-advanced |
| dynamic dispatch | Method chosen at runtime through a trait object | ch18 |
| dynamically sized type (DST) | Type whose size is known only at runtime, such as `str` | ch20-advanced |
| dyn compatibility | Rules a trait must meet to be used as `dyn Trait` | ch18 |
| edition | Opt-in language revision selected per crate in `Cargo.toml` | appendix |
| executor / runtime | Crate machinery that polls and schedules async code | ch17 |
| expression / statement | Evaluates to a value / performs an action and returns none | ch03 |
| field init shorthand | `Struct { name }` when a variable and a field share a name | ch05 |
| function pointer | The `fn` type; implements all three closure traits | ch20-advanced |
| future | Value that may be ready later; implements `Future` | ch17 |
| generic | Stand-in for a concrete type or other property | ch10 |
| integration test | Test in `tests/` using only the crate's public API | ch11 |
| interior mutability | Mutating data behind an immutable reference, checked at runtime | ch15 |
| irrefutable / refutable | Pattern that always matches / can fail to match | ch19 |
| iterator adapter / consuming adapter | Lazy method returning a new iterator / method that calls `next` | ch13 |
| lifetime | Scope for which a reference is valid | ch10 |
| lifetime elision | Three compiler rules that infer lifetimes in signatures | ch10 |
| match guard | Extra `if` condition on a `match` arm | ch19 |
| method | Function in an `impl` block whose first parameter is `self` | ch05 |
| module / path | Unit of scope and privacy / name of an item in the module tree | ch07 |
| monomorphization | Compiling generic code into specific code per concrete type | ch10 |
| move | Transfer of ownership that invalidates the source variable | ch04 |
| mutex | Mutual exclusion: one thread accesses the data at a time | ch16 |
| never type | `!`, the type of expressions that do not return | ch20-advanced |
| newtype pattern | Tuple struct wrapping one type to make a distinct type | ch20-advanced |
| ownership | Compiler-checked rules for managing memory | ch04 |
| package | One or more crates described by a `Cargo.toml` | ch07 |
| panic | Unrecoverable error: unwind or abort | ch09 |
| pinning | `Pin` guarantee that a value will not move in memory | ch17 |
| prelude | Items the standard library brings into every scope | ch01-02 |
| procedural macro | Macro that takes code as input and produces code | ch20-macros |
| raw identifier | `r#` prefix that lets a keyword be used as a name | appendix |
| raw pointer | `*const T` / `*mut T`; dereferencing requires `unsafe` | ch20-unsafe |
| reference cycle | `Rc<T>` values pointing at each other; leaks memory | ch15 |
| release profile | Named set of build settings (`dev`, `release`) | ch14 |
| `Send` / `Sync` | Marker traits: ownership may move across threads / may be shared | ch16 |
| shadowing | Declaring a new variable with an existing name | ch03 |
| slice | Reference to a contiguous sequence in a collection | ch04 |
| smart pointer | Pointer-like struct with extra metadata and capabilities | ch15 |
| static dispatch | Method chosen at compile time through monomorphization | ch18 |
| stream | Asynchronous sequence of items | ch17 |
| supertrait | Trait that another trait requires | ch20-advanced |
| task | Unit of async work managed by the runtime, not the OS | ch17 |
| trait / trait bound | Shared behaviour / constraint that a generic implements it | ch10 |
| trait object | `dyn Trait` behind a pointer; any type implementing the trait | ch18 |
| `impl Trait` | Shorthand for a trait bound, or an opaque return type | ch10 |
| type alias | `type` synonym for an existing type; not a new type | ch20-advanced |
| unit test | Test of one module in isolation, placed next to the code | ch11 |
| unit type | `()`, the empty tuple; the value of expressions with no result | ch03 |
| unsafe superpowers | The five actions permitted only in `unsafe` | ch20-unsafe |
| unwinding | Walking back up the stack cleaning up after a panic | ch09 |
| workspace | Set of packages sharing one `Cargo.lock` and output directory | ch14 |
| zero-cost abstraction | Higher-level construct with no added runtime overhead | ch13 |
