# Ch 7 - Packages, Crates, and Modules

Source: The Rust Programming Language ch. 7 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- The *module system* is four features (§7.0):
  - **Packages**: a Cargo feature for building, testing and sharing crates.
  - **Crates**: a tree of modules that produces a library or an executable.
  - **Modules and `use`**: control organization, scope and privacy of paths.
  - **Paths**: a way of naming an item (struct, function, module, ...).
- Crate = the smallest amount of code the compiler considers at a time. Even a single file passed to
  `rustc` is a crate. (§7.1)
- Crate root = the source file the compiler starts from; its contents form the root module, an implicit
  module named `crate`, at the top of the *module tree*. (§7.1, §7.2)
- Package = a bundle of one or more crates plus a *Cargo.toml* describing how to build them. (§7.1)
- Module tree is like a filesystem directory tree: modules nest (parent/child), modules defined in the
  same module are siblings, and paths locate items in it. (§7.2)
- Scope: each nested context has a set of names "in scope". Two items with the same name cannot be in
  the same scope. (§7.0)
- Privacy default: hiding implementation details is the default, so you know what inner code can
  change without breaking outer code. `pub` opts items into the public interface. (§7.3)

## Rules and Semantics

### Packages and crates (§7.1)

- Binary crate: compiles to an executable; must have a `main` function.
- Library crate: no `main`, does not compile to an executable; defines functionality to share. When
  Rustaceans say "crate" they usually mean a library crate ("library" in the general sense).
- A package must contain at least one crate; at most ONE library crate; any number of binary crates.
- Cargo conventions (not written in *Cargo.toml*):
  - *src/main.rs* = crate root of a binary crate named after the package.
  - *src/lib.rs* = crate root of a library crate named after the package.
  - Both present = two crates (one binary, one library), both with the package name.
  - Each file in *src/bin* is a separate binary crate.
- Cargo passes the crate root files to `rustc` to build the library or binary.

### Module declaration and file lookup (§7.2, §7.5)

- Compilation starts at the crate root file.
- `mod garden;` in the crate root makes the compiler look for the module's code in:
  1. inline, in curly brackets replacing the semicolon (`mod garden { ... }`);
  2. *src/garden.rs*;
  3. *src/garden/mod.rs* (older style, still supported).
- `mod vegetables;` declared in any non-root file (e.g. *src/garden.rs*) is looked up in the directory
  named for the parent module: inline, *src/garden/vegetables.rs*, or *src/garden/vegetables/mod.rs*.
- A module body can hold other modules, structs, enums, constants, traits, functions.
- `mod` is NOT an "include": load a file with a `mod` declaration exactly once in the module tree;
  everywhere else refer to its items by path to where it was declared.
- `use` has no effect on which files are compiled; only `mod` declares modules.
- Moving a module's body into its own file leaves the module tree, and all paths into it, unchanged.
- Placing *hosting.rs* directly in *src* would make it a `hosting` module declared in the crate root,
  not a child of `front_of_house`; directories mirror the module tree.

### Paths (§7.3)

- Absolute path: starts from a crate root. Current crate: the literal `crate`. External crate: the
  crate's name (e.g. `std`, `rand`).
- Relative path: starts from the current module, using `self`, `super`, or an identifier in the
  current module.
- Segments are separated by `::`. `crate::...` is like `/` at a filesystem root; `super::` is like `..`.
- `super` begins a relative path at the parent module.

### Privacy (§7.2, §7.3)

- All items (functions, methods, structs, enums, modules, constants) are private to parent modules by
  default. To make an item private, put it in a module.
- Items in a parent module cannot use private items of child modules; items in child modules CAN use
  items in their ancestor modules.
- Siblings (items defined in the same module) can refer to each other without `pub`.
- `pub mod` makes only the module reachable from ancestors; its contents remain private. Each item
  inside needs its own `pub`.
- A path works only if every segment is accessible from the use site.
- `pub struct`: the struct is public, fields stay private; mark fields `pub` case by case.
- A struct with any private field cannot be constructed from outside its module, so it must provide a
  public associated function as constructor.
- `pub enum`: all variants become public; `pub` goes only before `enum`.

### `use` (§7.4)

- `use` creates a shortcut to a path, like a symbolic link; the name becomes valid in that scope as if
  defined there. Paths in `use` are privacy-checked like any other.
- A `use` applies only to the scope it appears in; a child module is a different scope.
- Two items with the same name cannot be brought into one scope with `use`.
- `as` gives the imported item a new local name (alias).
- A name imported with `use` is private to the importing scope. `pub use` re-exports it so outside code
  can refer to it as if it were defined in that scope.
- External packages: list in *Cargo.toml* (Cargo downloads it and its dependencies from crates.io),
  then `use` items via a path starting with the crate name.
- `std` is also an external crate, but ships with Rust: no *Cargo.toml* entry, still needs `use`.
- Nested paths: common prefix, `::`, then curly brackets around the differing parts; allowed at any
  level of a path. `self` inside the brackets names the prefix itself.
- Glob `*` brings all public items defined in a path into scope.

## Syntax and API Reference

```rust
mod front_of_house {                 // inline module
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}
mod front_of_house;                  // body in src/front_of_house.rs
pub mod hosting;                     // in src/front_of_house.rs -> src/front_of_house/hosting.rs

crate::front_of_house::hosting::add_to_waitlist();   // absolute
front_of_house::hosting::add_to_waitlist();          // relative
super::deliver_order();                              // relative, from parent module
```

```rust
use crate::front_of_house::hosting;       // then hosting::add_to_waitlist()
use std::collections::HashMap;            // absolute path into the std crate
use std::fmt;  use std::io;               // fmt::Result vs io::Result<()>
use std::io::Result as IoResult;          // alias
pub use crate::front_of_house::hosting;   // re-export
use std::{cmp::Ordering, io};             // nested path
use std::io::{self, Write};               // std::io and std::io::Write
use std::collections::*;                  // glob
use rand::prelude::*;                     // external crate; then rand::rng().random_range(1..=100)
```

```rust
mod back_of_house {
    pub struct Breakfast {
        pub toast: String,
        seasonal_fruit: String,          // private field
    }
    impl Breakfast {
        pub fn summer(toast: &str) -> Breakfast { /* sets both fields */ }
    }
    pub enum Appetizer { Soup, Salad }   // variants public automatically
}
```

| Command / file | Effect (§7.1, §7.2, §7.4) |
|---|---|
| `cargo new my-project` | binary (application) package: *Cargo.toml* + *src/main.rs* |
| `cargo new restaurant --lib` | library package with *src/lib.rs* |
| files in `src/bin` | one extra binary crate per file |
| `rand = "0.10.1"` under `[dependencies]` | dependency line the book uses for `rand` |

## Decision Rules

- Absolute vs relative paths: depends on whether the item definition and its users are more likely to
  move together (relative survives) or separately (absolute survives). The book's general preference:
  absolute paths, since definitions and call sites usually move independently. (§7.3)
- Use `super::` when the module is closely tied to its parent and they would be moved together; fewer
  places to update after a reorganization. (§7.3)
- Functions: `use` the parent module and call `hosting::add_to_waitlist()`; this shows the function is
  not locally defined while keeping paths short. Importing the function itself is unidiomatic. (§7.4)
- Structs, enums and other items: `use` the full path (`use std::collections::HashMap;`). (§7.4)
- Same-named items: either import the parent modules (`fmt::Result`, `io::Result`) or rename one with
  `as`. Both are idiomatic. (§7.4)
- Use `pub use` when the internal structure differs from how callers think about the domain: write
  one structure, expose another. (§7.4)
- Glob imports: be careful; commonly used in the `tests` module to bring everything under test into
  scope, and sometimes as part of the prelude pattern. (§7.4)
- File layout: prefer *src/name.rs* over *src/name/mod.rs*; many files named *mod.rs* are confusing when
  open together in an editor. (§7.5)
- Split a module into its own file when it gets large. (§7.5)
- For very large projects of interrelated packages that evolve together, use Cargo workspaces. (§7.0)

## Pitfalls and Compiler Errors

- **E0603** `module `hosting` is private`: path is correct but passes through a private child module.
  Fix: `pub mod hosting`. (§7.3)
- **E0603** `function `add_to_waitlist` is private`: module made `pub` but its contents were not.
  Fix: also mark the function `pub fn`. (§7.3)
- **E0433** `cannot find module or crate `hosting` in this scope` ("use of unresolved module or unlinked
  crate"), plus an `unused import` warning (`#[warn(unused_imports)]`): a `use` at the crate root does
  not apply inside a child `mod customer`. Fix: move the `use` into the child module, or reference the
  parent's shortcut as `super::hosting`. (§7.4)
- Two `use` statements importing the same name (`use std::fmt::Result` and `use std::io::Result`):
  not allowed, Rust could not tell which `Result` is meant. (§7.4)
- Assigning to or reading a private field from outside the module (`meal.seasonal_fruit = ...`) does
  not compile. (§7.3)
- Using both file styles (*name.rs* and *name/mod.rs*) for the same module is a compiler error. Mixing
  styles across different modules is allowed but may confuse readers. (§7.5)
- `mod name;` with no matching file does not compile until the file exists. (§7.5)
- Glob imports hide where names come from, and a dependency upgrade that adds a definition with the
  same name as one of yours in that scope can cause compiler errors. (§7.4)
- Treating `mod` as an include and declaring the same file from several places is the wrong model. (§7.5)

## Idioms and Best Practices

- Package with both binary and library: keep just enough code in *src/main.rs* to start an executable
  that calls into the library; define the module tree in *src/lib.rs*. The binary then uses the
  library's public items via paths starting with the package name, exactly like an external client,
  which helps you design a good API. Demonstrated in ch. 12. (§7.3)
- Group related definitions in modules and name the group for why they are related, so readers
  navigate by group and contributors know where new code belongs. (§7.2)
- The public API of a shared library crate is a contract with its users; for managing API changes see
  the Rust API Guidelines. (§7.3)
- Encapsulate: expose a public interface, keep private details you reserve the right to change. (§7.0)
- Use nested paths to cut vertical space when importing several items from one crate or module. (§7.4)
- As a project grows: split into modules, then files, then extract parts into separate crates that
  become external dependencies. (§7.0)

## Details Worth Knowing

- Cargo itself is a package: a binary crate (the CLI) plus a library crate the binary depends on, which
  other projects can also depend on. (§7.1)
- Why enum variants default to public and struct fields to private: enums are not very useful unless
  variants are public; structs are often useful with private fields. (§7.3)
- With `pub use crate::front_of_house::hosting;` external code calls
  `restaurant::hosting::add_to_waitlist()` instead of
  `restaurant::front_of_house::hosting::add_to_waitlist()`, and `front_of_house` need not be `pub`. (§7.4)
- Cheat-sheet example: binary crate `backyard` with *src/main.rs* (`pub mod garden;`), *src/garden.rs*
  (`pub mod vegetables;`), *src/garden/vegetables.rs* defining `Asparagus`, reached as
  `crate::garden::vegetables::Asparagus`. (§7.2)
- A `use` may appear before the `mod` declaration it refers to in the same file (cheat-sheet
  *src/main.rs*). (§7.2)
- The "same module as" rule explains why a private top-level module is usable from a sibling function
  in the crate root without `pub`. (§7.3)
- The file-extraction procedure works identically for binary crates rooted at *src/main.rs*. (§7.5)
- Forward references: workspaces and `pub use` effects on documentation in ch. 14; tests module and
  glob in ch. 11; binary+library layout in ch. 12. (§7.0, §7.3, §7.4)
