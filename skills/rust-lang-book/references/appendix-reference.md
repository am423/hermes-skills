# Appendices - Keywords, Operators, Derivable Traits, Tools, Editions, Release Process

Source: The Rust Programming Language title page and appendices A-E, G (rust-lang/book @ 5c23042;
Rust 1.99.1, edition 2024). Lookup tables; refs are (App. A) ... (App. G). Appendix F (translations) omitted.

## Core Model

- Book baseline (title page): assumes Rust 1.99.1 (released 2026-10-15) or later with `edition = "2024"`
  in every project's *Cargo.toml*. Offline copy: `rustup doc --book`.
- Keywords are reserved for current or future language use and cannot be identifiers, except as raw
  identifiers. Identifiers name functions, variables, parameters, struct fields, modules, crates,
  constants, macros, static values, attributes, types, traits, or lifetimes. (App. A)

## Keywords (App. A)

### Currently in use

| Keyword | Meaning |
| --- | --- |
| `as` | Primitive cast; disambiguate the trait containing an item; rename items in `use` |
| `async` | Return a `Future` instead of blocking the current thread |
| `await` | Suspend execution until a `Future`'s result is ready |
| `break` | Exit a loop immediately |
| `const` | Define constant items or constant raw pointers |
| `continue` | Continue to the next loop iteration |
| `crate` | In a module path, the crate root |
| `dyn` | Dynamic dispatch to a trait object |
| `else` | Fallback for `if` and `if let` |
| `enum` | Define an enumeration |
| `extern` | Link an external function or variable |
| `false` | Boolean false literal |
| `fn` | Define a function or the function pointer type |
| `for` | Loop over an iterator's items; implement a trait; specify a higher ranked lifetime |
| `if` | Branch on a conditional expression |
| `impl` | Implement inherent or trait functionality |
| `in` | Part of `for` loop syntax |
| `let` | Bind a variable |
| `loop` | Loop unconditionally |
| `match` | Match a value to patterns |
| `mod` | Define a module |
| `move` | Make a closure take ownership of all its captures |
| `mut` | Mutability in references, raw pointers, or pattern bindings |
| `pub` | Public visibility in struct fields, `impl` blocks, or modules |
| `ref` | Bind by reference |
| `return` | Return from function |
| `Self` | Type alias for the type being defined or implemented |
| `self` | Method subject or current module |
| `static` | Global variable, or lifetime lasting the entire program execution |
| `struct` | Define a structure |
| `super` | Parent module of the current module |
| `trait` | Define a trait |
| `true` | Boolean true literal |
| `type` | Define a type alias or associated type |
| `union` | Define a union; a keyword only when used in a union declaration |
| `unsafe` | Denote unsafe code, functions, traits, or implementations |
| `use` | Bring symbols into scope |
| `where` | Clauses that constrain a type |
| `while` | Loop conditionally on an expression's result |

### Reserved for future use (no functionality yet)

`abstract`, `become`, `box`, `do`, `final`, `gen`, `macro`, `override`, `priv`, `try`, `typeof`,
`unsized`, `virtual`, `yield`

### Raw identifiers

- Prefix a keyword with `r#` to use it where a keyword is not allowed; the prefix is needed at the
  definition and at every use: `fn r#match(needle: &str, haystack: &str) -> bool`, called `r#match(..)`.
  Without it: "expected identifier, found keyword `match`".
- Uses: free choice of identifier names; interop with code from languages where the word is not a
  keyword; calling into crates written for another edition. `try` is not a keyword in edition 2015 but
  is in 2018, 2021 and 2024, so a 2015 library's `try` function is called as `r#try` from later editions.

## Operators (App. B, Table B-1)

In table cells `\|` stands for a literal `|`. Blank trait column = not overloadable.

| Operator | Example | Explanation | Trait |
| --- | --- | --- | --- |
| `!` | `ident!(...)`, `ident!{...}`, `ident![...]` | Macro expansion | |
| `!` | `!expr` | Bitwise or logical complement | `Not` |
| `!=` | `expr != expr` | Nonequality comparison | `PartialEq` |
| `%` | `expr % expr` | Arithmetic remainder | `Rem` |
| `%=` | `var %= expr` | Arithmetic remainder and assignment | `RemAssign` |
| `&` | `&expr`, `&mut expr` | Borrow | |
| `&` | `&type`, `&mut type`, `&'a type`, `&'a mut type` | Borrowed pointer type | |
| `&` | `expr & expr` | Bitwise AND | `BitAnd` |
| `&=` | `var &= expr` | Bitwise AND and assignment | `BitAndAssign` |
| `&&` | `expr && expr` | Short-circuiting logical AND | |
| `*` | `expr * expr` | Arithmetic multiplication | `Mul` |
| `*=` | `var *= expr` | Arithmetic multiplication and assignment | `MulAssign` |
| `*` | `*expr` | Dereference | `Deref` |
| `*` | `*const type`, `*mut type` | Raw pointer | |
| `+` | `trait + trait`, `'a + trait` | Compound type constraint | |
| `+` | `expr + expr` | Arithmetic addition | `Add` |
| `+=` | `var += expr` | Arithmetic addition and assignment | `AddAssign` |
| `,` | `expr, expr` | Argument and element separator | |
| `-` | `- expr` | Arithmetic negation | `Neg` |
| `-` | `expr - expr` | Arithmetic subtraction | `Sub` |
| `-=` | `var -= expr` | Arithmetic subtraction and assignment | `SubAssign` |
| `->` | `fn(...) -> type`, `\|...\| -> type` | Function and closure return type | |
| `.` | `expr.ident` | Field access | |
| `.` | `expr.ident(expr, ...)` | Method call | |
| `.` | `expr.0`, `expr.1`, and so on | Tuple indexing | |
| `..` | `..`, `expr..`, `..expr`, `expr..expr` | Right-exclusive range literal | `PartialOrd` |
| `..=` | `..=expr`, `expr..=expr` | Right-inclusive range literal | `PartialOrd` |
| `..` | `..expr` | Struct literal update syntax | |
| `..` | `variant(x, ..)`, `struct_type { x, .. }` | "And the rest" pattern binding | |
| `...` | `expr...expr` | Deprecated (use `..=`); in a pattern: inclusive range pattern | |
| `/` | `expr / expr` | Arithmetic division | `Div` |
| `/=` | `var /= expr` | Arithmetic division and assignment | `DivAssign` |
| `:` | `pat: type`, `ident: type` | Constraints | |
| `:` | `ident: expr` | Struct field initializer | |
| `:` | `'a: loop {...}` | Loop label | |
| `;` | `expr;` | Statement and item terminator | |
| `;` | `[...; len]` | Part of fixed-size array syntax | |
| `<<` | `expr << expr` | Left-shift | `Shl` |
| `<<=` | `var <<= expr` | Left-shift and assignment | `ShlAssign` |
| `<` | `expr < expr` | Less than comparison | `PartialOrd` |
| `<=` | `expr <= expr` | Less than or equal to comparison | `PartialOrd` |
| `=` | `var = expr`, `ident = type` | Assignment/equivalence | |
| `==` | `expr == expr` | Equality comparison | `PartialEq` |
| `=>` | `pat => expr` | Part of match arm syntax | |
| `>` | `expr > expr` | Greater than comparison | `PartialOrd` |
| `>=` | `expr >= expr` | Greater than or equal to comparison | `PartialOrd` |
| `>>` | `expr >> expr` | Right-shift | `Shr` |
| `>>=` | `var >>= expr` | Right-shift and assignment | `ShrAssign` |
| `@` | `ident @ pat` | Pattern binding | |
| `^` | `expr ^ expr` | Bitwise exclusive OR | `BitXor` |
| `^=` | `var ^= expr` | Bitwise exclusive OR and assignment | `BitXorAssign` |
| `\|` | `pat \| pat` | Pattern alternatives | |
| `\|` | `expr \| expr` | Bitwise OR | `BitOr` |
| `\|=` | `var \|= expr` | Bitwise OR and assignment | `BitOrAssign` |
| `\|\|` | `expr \|\| expr` | Short-circuiting logical OR | |
| `?` | `expr?` | Error propagation | |

## Non-operator Symbols (App. B, Tables B-2 to B-10)

| Symbol | Explanation |
| --- | --- |
| **Stand-alone (B-2)** | |
| `'ident` | Named lifetime or loop label |
| digits + `u8`, `i32`, `f64`, `usize`, ... | Numeric literal of specific type |
| `"..."` | String literal |
| `r"..."`, `r#"..."#`, `r##"..."##`, ... | Raw string literal; escape characters not processed |
| `b"..."` | Byte string literal; an array of bytes instead of a string |
| `br"..."`, `br#"..."#`, `br##"..."##`, ... | Raw byte string literal (raw + byte string combined) |
| `'...'` | Character literal |
| `b'...'` | ASCII byte literal |
| `\|...\| expr` | Closure |
| `!` | Always-empty bottom type for diverging functions |
| `_` | "Ignored" pattern binding; also makes integer literals readable |
| **Paths (B-3)** | |
| `ident::ident` | Namespace path |
| `::path` | Path relative to the crate root (explicitly absolute) |
| `self::path` | Path relative to the current module (explicitly relative) |
| `super::path` | Path relative to the parent of the current module |
| `type::ident`, `<type as trait>::ident` | Associated constants, functions, and types |
| `<type>::...` | Associated item of a type that cannot be named directly (`<&T>::...`, `<[T]>::...`) |
| `trait::method(...)` | Disambiguate a method call by naming the trait that defines it |
| `type::method(...)` | Disambiguate a method call by naming the type it is defined for |
| `<type as trait>::method(...)` | Disambiguate a method call by naming both trait and type |
| **Generics (B-4)** | |
| `path<...>` | Parameters to a generic type in a type (`Vec<u8>`) |
| `path::<...>`, `method::<...>` | Parameters in an expression: the turbofish (`"42".parse::<i32>()`) |
| `fn ident<...> ...` | Define generic function |
| `struct ident<...> ...` | Define generic structure |
| `enum ident<...> ...` | Define generic enumeration |
| `impl<...> ...` | Define generic implementation |
| `for<...> type` | Higher ranked lifetime bounds |
| `type<ident=type>` | Generic type with specific associated type assignments (`Iterator<Item=T>`) |
| **Trait bounds (B-5)** | |
| `T: U` | `T` constrained to types that implement `U` |
| `T: 'a` | `T` must outlive `'a`: no transitively contained reference lives shorter than `'a` |
| `T: 'static` | `T` contains no borrowed references other than `'static` ones |
| `'b: 'a` | Lifetime `'b` must outlive lifetime `'a` |
| `T: ?Sized` | Allow the type parameter to be a dynamically sized type |
| `'a + trait`, `trait + trait` | Compound type constraint |
| **Macros and attributes (B-6)** | |
| `#[meta]` | Outer attribute |
| `#![meta]` | Inner attribute |
| `$ident` | Macro substitution |
| `$ident:kind` | Macro metavariable |
| `$(...)...` | Macro repetition |
| `ident!(...)`, `ident!{...}`, `ident![...]` | Macro invocation |
| **Comments (B-7)** | |
| `//` | Line comment |
| `//!` | Inner line doc comment |
| `///` | Outer line doc comment |
| `/*...*/` | Block comment |
| `/*!...*/` | Inner block doc comment |
| `/**...*/` | Outer block doc comment |
| **Parentheses (B-8)** | |
| `()` | Empty tuple (unit), both literal and type |
| `(expr)` | Parenthesized expression |
| `(expr,)` | Single-element tuple expression |
| `(type,)` | Single-element tuple type |
| `(expr, ...)` | Tuple expression |
| `(type, ...)` | Tuple type |
| `expr(expr, ...)` | Function call; also initializes tuple `struct`s and tuple `enum` variants |
| **Curly brackets (B-9)** | |
| `{...}` | Block expression |
| `Type {...}` | Struct literal |
| **Square brackets (B-10)** | |
| `[...]` | Array literal |
| `[expr; len]` | Array literal containing `len` copies of `expr` |
| `[type; len]` | Array type containing `len` instances of `type` |
| `expr[expr]` | Collection indexing; overloadable (`Index`, `IndexMut`) |
| `expr[..]`, `expr[a..]`, `expr[..b]`, `expr[a..b]` | Collection indexing posing as slicing (note below) |

Slice-style indexing uses `Range`, `RangeFrom`, `RangeTo`, or `RangeFull` as the "index".

## Derivable Traits (App. C)

The `derive` attribute, applied to a struct or enum definition, generates a default implementation of
a trait for that type.

- `Debug`: enables `:?` inside `{}` placeholders, for programmer-facing inspection of an instance.
  Required by e.g. `assert_eq!`, which prints the values when the assertion fails.
- `PartialEq`: enables `==` and `!=`; derive implements `eq`. Structs: equal only if all fields are
  equal. Enums: each variant equals itself and no other. Required by e.g. `assert_eq!`.
- `Eq`: no methods; signals that every value equals itself. Only for types that are `PartialEq`; not
  every `PartialEq` type qualifies (floats: `NaN` is not equal to `NaN`). Required for `HashMap<K, V>` keys.
- `PartialOrd`: enables `<`, `>`, `<=`, `>=`; only for `PartialEq` types. Derive implements
  `partial_cmp`, returning `Option<Ordering>` (`None` when no ordering exists, e.g. any float vs `NaN`).
  Structs compare field by field in definition order; earlier enum variants are less than later ones.
  Required by e.g. `gen_range` from the `rand` crate.
- `Ord`: a valid ordering exists for any two values; `cmp` returns `Ordering`, not an `Option`. Only for
  types that are `PartialOrd` and `Eq`. Derived `cmp` orders like derived `partial_cmp`. Required when
  storing values in a `BTreeSet<T>`.
- `Clone`: explicit deep copy via `clone`; may run arbitrary code and copy heap data. Derive calls
  `clone` on each part, so every field or value must be `Clone`. Required by e.g. `to_vec` on a slice.
- `Copy`: duplicate by copying only bits stored on the stack; no arbitrary code. Defines no methods.
  Derivable when all parts are `Copy`; must also be `Clone`. Rarely required; it saves `clone` calls.
- `Hash`: maps an instance of arbitrary size to a fixed-size value; derive implements `hash` by
  combining `hash` of each part, so all parts must be `Hash`. Required for `HashMap<K, V>` keys.
- `Default`: derive implements the `default` function by calling `default` on each part, so all parts
  must be `Default`. Required by e.g. `unwrap_or_default` on `Option<T>` (returns `Default::default`
  for `T` when the value is `None`).
- These are the only standard-library traits usable with `derive`; others have no sensible default.
  `Display` cannot be derived, because end-user formatting needs a human decision about what to show.
  Libraries can provide `derive` for their own traits via procedural macros (ch. 20).
- When to derive: `Debug` so values can be inspected and used in assertions; `PartialEq`/`Eq` for
  comparison and map keys; `PartialOrd`/`Ord` for sorting and ordered collections; `Hash` for map keys;
  `Default` to fill remaining fields with struct update syntax, `..Default::default()`.
- `Copy` vs `Clone`: `Copy` has no methods precisely so nobody can overload them and break the
  assumption that copying is very fast. Anything `Copy` allows, `Clone` allows too, but possibly slower
  or with explicit `clone` calls. A `Copy` type's `Clone` is trivial and does the same job.

## Development Tools (App. D)

| Tool | Command | What it does |
| --- | --- | --- |
| `rustfmt` / `cargo-fmt` | `cargo fmt` | Reformats all Rust code in the current crate to community style |
| `rustfix` | `cargo fix` | Applies compiler-suggested fixes for warnings; also migrates between editions |
| Clippy | `cargo clippy` | Extra lints that catch common mistakes |
| `rust-analyzer` | (IDE plug-in) | Language Server Protocol utilities for IDE integration |

- `rustfmt`, `rustfix` and Clippy ship with standard Rust installations. `rustfmt` is to `cargo-fmt` as
  `rustc` is to `cargo`: finer control vs awareness of Cargo project conventions. Formatting should
  change style only, never semantics.
- `cargo fix` example: `let mut x = 42;` never mutated triggers `#[warn(unused_mut)]` ("variable does
  not need to be mutable"); `cargo fix` removes the `mut`.
- Clippy example: `let x = 3.1415;` is an error under `#[deny(clippy::approx_constant)]` (on by
  default); use `std::f64::consts::PI`.
- `rust-analyzer` (community-recommended; e.g. the Visual Studio Code plug-in) gives the IDE
  autocompletion, jump to definition, and inline errors.

## Editions (App. E)

- Available editions: Rust 2015, 2018, 2021, 2024; a new one roughly every three years, shipped through
  the normal six-week release process. The book uses 2024 idioms.
- The `edition` key in *Cargo.toml* selects the edition; if absent, `2015` is used for backward
  compatibility. Editions are opt-in per project.
- An edition may contain incompatible changes (e.g. a new keyword clashing with identifiers); code that
  does not opt in keeps compiling on newer compilers.
- Every compiler supports all editions that existed before its release and links crates of different
  editions together; the edition only affects how the compiler initially parses code. A 2015 crate can
  depend on a 2018 crate and vice versa.
- Most features reach all editions; some (mainly those needing new keywords) need a later edition.
- Migration: `cargo fix`; details in *The Rust Edition Guide*.

## Release Process and Nightly Rust (App. G)

- Principle: upgrading to a new stable Rust should never be something to fear.
- Train model: all development lands on the main branch. Channels: nightly (built every night), beta
  (branches from main every six weeks), stable (produced from beta six weeks later; the next beta
  branches from nightly at the same time). A stable release every six weeks.
- Regressions found in beta are fixed on main, then backported to the `beta` branch. Typical practice:
  develop on stable, test against beta in CI.
- Support: only the most recent stable is supported; each version reaches end of life after six weeks.
- Unstable features: in-progress work lands on main behind a feature flag. Using it requires a nightly
  toolchain plus an opt-in annotation in the source. Beta and stable accept no feature flags. The book
  covers stable features only.
- RFC process: anyone may write a Request For Comments; the relevant team (language, compiler,
  infrastructure, documentation, ...) discusses and accepts or rejects by consensus. Accepted -> issue
  opened -> implementation lands on main behind a feature gate -> trialled on nightly -> team decides ->
  gate removed -> feature rides the trains to stable.
- `rustup toolchain install nightly`: install nightly (stable is installed by default).
  `rustup toolchain list`: show installed toolchains, e.g. `stable-x86_64-pc-windows-msvc (default)`.
  `rustup override set nightly`: run in a project directory to use nightly for `rustc`/`cargo` there.
- A toolchain is a release of Rust plus its associated components; `rustup` switches channels globally
  or per project.
