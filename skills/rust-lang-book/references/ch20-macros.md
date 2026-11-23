# Ch 20 - Advanced Features: Macros

Source: The Rust Programming Language ch. 20 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).
Covers §20.5 (Macros) and the chapter summary.

## Core Model

- "Macro" names a family of features (§20.5):
  - **Declarative macros** defined with `macro_rules!`.
  - **Procedural macros**, three kinds:
    1. custom `#[derive]` macros: specify code added by the `derive` attribute on structs and enums;
    2. attribute-like macros: define custom attributes usable on any item;
    3. function-like macros: look like function calls but operate on the tokens given as argument.
- **Metaprogramming**: writing code that writes other code. Macros *expand* into more code than you
  wrote by hand (`println!` and `vec!` and `derive`).
- **Declarative macro** = something like a `match` over source code: the value is the literal Rust
  source passed to the macro, the patterns are compared with the *structure* of that source, and the
  code of the matching arm replaces the invocation. All of it happens during compilation. Also called
  "macros by example", "`macro_rules!` macros", or plain "macros"; the most widely used form.
- **Procedural macro** = acts more like a function: accepts code as input, operates on it, and produces
  code as output (rather than pattern-match-and-replace). Input and output are both `TokenStream`.
- `TokenStream`: a sequence of tokens; defined by the `proc_macro` crate that ships with Rust. Input
  stream = the source the macro operates on; output stream = the code the macro produces.

## Rules and Semantics

### Macros vs functions (§20.5 "The Difference Between Macros and Functions")

- A function signature fixes the number and types of parameters; a macro can take a variable number
  (`println!("hello")` vs `println!("hello {}", name)`).
- Macros are expanded before the compiler interprets the meaning of the code, so a macro can do things
  like implement a trait on a type. A function cannot: it runs at runtime, and a trait must be
  implemented at compile time.
- Cost: macro definitions are code that writes code, so they are generally harder to read, understand
  and maintain than functions.
- Ordering: a macro must be defined or brought into scope *before* it is called in a file; functions
  can be defined anywhere and called anywhere.

### Declarative macros (§20.5 "Declarative Macros for General Metaprogramming")

- Define with `macro_rules!` followed by the macro name **without** the `!`, then curly brackets holding
  the body.
- The body is a list of arms: `( pattern ) => { code };`. If a pattern matches, its block is emitted.
  Input matching none of the arms is an error. Complex macros have more than one arm.
- `#[macro_export]` makes the macro available whenever its defining crate is brought into scope;
  without it the macro can't be brought into scope.
- Macro pattern syntax differs from ch. 19 patterns because it matches code structure, not values.
- Pattern pieces of `( $( $x:expr ),* )`:
  - outer parentheses enclose the whole pattern;
  - `$` declares a macro variable holding the matched Rust code (distinguishing it from a regular Rust
    variable);
  - `$( ... )` captures values matching the inner pattern for use in the replacement code;
  - `$x:expr` matches any Rust expression and names it `$x`;
  - the `,` after `$()` requires a literal comma separator between each matched instance;
  - `*` means zero or more of whatever precedes it.
- In the replacement, code inside `$( ... )*` is generated once per match of the pattern's `$()`, with
  `$x` replaced by each matched expression.
- `vec![1, 2, 3]` therefore expands to a block that creates `temp_vec` with `Vec::new()`, calls
  `temp_vec.push(1);`, `temp_vec.push(2);`, `temp_vec.push(3);`, and evaluates to `temp_vec`.

### Procedural macros in general (§20.5 "Procedural Macros for Generating Code from Attributes")

- Definitions must live in their own crate with a special crate type (`proc-macro`). The source calls
  this a restriction for complex technical reasons that may be lifted eventually.
- The defining function takes `TokenStream` and returns `TokenStream`, and carries an attribute saying
  which kind of procedural macro it is.
- One crate may contain multiple kinds of procedural macros.
- All three kinds work in a similar fashion.

### Custom `derive` (§20.5 "Custom `derive` Macros")

- Works only on structs and enums.
- The function annotated `#[proc_macro_derive(HelloMacro)]` is called when a user writes
  `#[derive(HelloMacro)]` on a type. The name given in the attribute matches the trait name by
  convention.
- The returned `TokenStream` is **added to** the code the user wrote.
- `proc_macro_derive` functions must return `TokenStream`, not `Result`, to conform to the procedural
  macro API; errors must therefore be reported by panicking.
- Why a macro is required here: Rust has no reflection, so a type's name cannot be looked up at
  runtime; a default trait method cannot print the implementing type's name. Code must be generated at
  compile time.

### Attribute-like macros (§20.5 "Attribute-Like Macros")

- Create new attributes instead of generating code for `derive`. More flexible: applicable to other
  items as well, such as functions.
- Signature takes two streams: `attr` is the attribute's contents (the `GET, "/"` in
  `#[route(GET, "/")]`), `item` is the body of the item it is attached to (e.g. the whole `fn index()`).
- Otherwise identical in workflow to custom derive: a `proc-macro` crate plus a generating function.

### Function-like macros (§20.5 "Function-Like Macros")

- Invoked like function calls; like `macro_rules!` macros they can take an unknown number of arguments.
- Unlike `macro_rules!` (restricted to match-like syntax), they take a `TokenStream` and manipulate it
  with Rust code, enabling much more complex processing, e.g. an `sql!` macro that parses a SQL
  statement and checks that it is syntactically correct.
- The function receives the tokens inside the parentheses and returns the generated code.

## Syntax and API Reference

```rust
#[macro_export]
macro_rules! vec {                       // simplified std definition (Listing 20-35)
    ( $( $x:expr ),* ) => {
        {
            let mut temp_vec = Vec::new();
            $( temp_vec.push($x); )*
            temp_vec
        }
    };
}
```

Procedural macro entry points:

| Kind | Attribute on the defining fn | User-side invocation |
|---|---|---|
| Custom derive | `#[proc_macro_derive(HelloMacro)]` | `#[derive(HelloMacro)]` |
| Attribute-like | `#[proc_macro_attribute]` | `#[route(GET, "/")]` |
| Function-like | `#[proc_macro]` | `sql!(SELECT * FROM posts WHERE id=1)` |

```rust
pub fn hello_macro_derive(input: TokenStream) -> TokenStream      // custom derive
pub fn route(attr: TokenStream, item: TokenStream) -> TokenStream // attribute-like
pub fn sql(input: TokenStream) -> TokenStream                     // function-like
```

Derive crate `Cargo.toml` (`hello_macro_derive/Cargo.toml`):

```toml
[lib]
proc-macro = true

[dependencies]
syn = "2.0"
quote = "1.0"
```

Derive implementation skeleton (Listings 20-40, 20-42):

```rust
use proc_macro::TokenStream;
use quote::quote;

#[proc_macro_derive(HelloMacro)]
pub fn hello_macro_derive(input: TokenStream) -> TokenStream {
    let ast = syn::parse(input).unwrap();   // parse into a syntax tree
    impl_hello_macro(&ast)                  // build the trait implementation
}

fn impl_hello_macro(ast: &syn::DeriveInput) -> TokenStream {
    let name = &ast.ident;
    let generated = quote! {
        impl HelloMacro for #name {
            fn hello_macro() { println!("Hello, Macro! My name is {}!", stringify!(#name)); }
        }
    };
    generated.into()
}
```

| Item | Role per the source |
|---|---|
| `proc_macro` crate | Ships with Rust (no Cargo.toml entry); compiler API to read/manipulate Rust code |
| `syn` crate | Parses Rust code from a string into a data structure you can operate on |
| `syn::parse` | Takes a `TokenStream`, returns a `DeriveInput` representing the parsed code |
| `syn::DeriveInput` | Parsed item; fields shown include `ident` (the name) and `data` |
| `ast.ident` | `Ident` for the annotated type's name (prints as e.g. `Pancakes`) |
| `quote` crate / `quote!` | Turns `syn` data structures back into Rust code; defines returned code |
| `#name` inside `quote!` | Templating: replaced with the value of variable `name`; repetition also exists |
| `.into()` | Converts the `quote!` result into the required `TokenStream` |
| `stringify!` | Built in; turns an expression into a string literal at compile time (`1 + 2` -> `"1 + 2"`) |

Commands and dependency wiring:

- `cargo new hello_macro --lib`, then inside that project `cargo new hello_macro_derive --lib`.
- `cargo new pancakes` for the consuming binary; unpublished crates are added as `path` dependencies:
  `hello_macro = { path = "../hello_macro" }` and
  `hello_macro_derive = { path = "../hello_macro/hello_macro_derive" }`. Published ones would be
  regular dependencies.
- User code: `use hello_macro::HelloMacro;` and `use hello_macro_derive::HelloMacro;`, then
  `#[derive(HelloMacro)] struct Pancakes;` and `Pancakes::hello_macro();`.

## Decision Rules

- Function vs macro: use a macro when you need a variable number of arguments or compile-time code
  generation such as implementing a trait; otherwise the function is simpler to read and maintain.
- `macro_rules!` vs function-like procedural macro: the former is limited to match-like patterns; reach
  for the latter when the input needs real processing in Rust code (parsing/validating, as with `sql!`).
- Custom derive vs attribute-like: derive only for structs and enums; attribute-like when the
  annotation must apply to other items (functions) or take its own arguments.
- Provide a derive when users would otherwise hand-write the same `impl` block for every type.
- Crate layout choice: keeping `hello_macro` and `hello_macro_derive` as separate dependencies lets
  users take the trait without the derive. The alternative is for `hello_macro` to depend on
  `hello_macro_derive` and re-export the macro.

## Pitfalls and Compiler Errors

- No error codes appear in this section. Mistakes the source calls out:
- Omitting `#[macro_export]`: the macro cannot be brought into scope from the crate.
- Writing the `!` in the definition name: `macro_rules! vec`, not `vec!`.
- Invoking a `macro_rules!` macro with input matching no arm is an error.
- Calling a macro before it is defined or brought into scope in the file.
- Putting a procedural macro in an ordinary crate: it must be its own crate with `proc-macro = true`.
- Listing 20-40 alone does not compile until `impl_hello_macro` is defined.
- Bare `unwrap` on `syn::parse` in a derive is a simplification; production code should give specific
  messages via `panic!` or `expect`.
- Returning the `quote!` result directly: the compiler expects a `TokenStream`, so call `.into()`.
- Changing the trait in `hello_macro` requires changing the macro in `hello_macro_derive` too.

## Idioms and Best Practices

- Naming convention: for a crate `foo`, the custom derive crate is `foo_derive`.
- Place the derive crate inside the directory of the crate it serves, since the two are tightly related;
  they are still published separately, and users add both as dependencies and bring both into scope.
- Split a procedural macro into an outer function that parses the `TokenStream` (nearly identical in
  every proc-macro crate) and an inner function that transforms the syntax tree (purpose-specific).
- Name the derive after the trait it implements.
- Use `stringify!(#name)` rather than formatting: the `#name` input might be an expression to print
  literally, and it saves an allocation by producing a string literal at compile time. `format!` and
  `println!` instead evaluate the expression and turn the result into a `String`.

## Details Worth Knowing

- The real std `vec!` also pre-allocates the correct amount of memory; the book's version omits that.
- Parsing `struct Pancakes;` yields a `DeriveInput` whose `ident` is `Pancakes` and whose `data` is a
  `Struct` with `fields: Unit` (a unit struct); more fields exist for other kinds of Rust code.
- Final program output: `Hello, Macro! My name is Pancakes!`.
- An attribute-like `#[route]` would be defined by a web framework as a procedural macro.
- Further reading named by the source: Rust Reference "macros by example" for full pattern syntax, "The
  Little Book of Rust Macros" (started by Daniel Keep, continued by Lukas Wirth), `syn` docs for
  `DeriveInput`, `quote` crate docs; Appendix C covers the `derive` attribute.
- Chapter summary: these features are rarely used; the chapter is meant as a reference for recognizing
  them in error-message suggestions or other people's code. Ch. 21 is the final project.
