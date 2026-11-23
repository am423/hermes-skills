# Ch 5 - Using Structs to Structure Related Data

Source: The Rust Programming Language ch. 5 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- **Struct** = a custom data type that packages and names multiple related values forming a
  meaningful group; comparable to an object's data attributes in OO languages (§5.0).
- Structs and enums (ch. 6) are the building blocks for domain types that let the compiler's type
  checking work for you (§5.0).
- Like tuples, a struct's pieces may have different types; unlike tuples, each piece is named, so
  you do not rely on order to specify or access values (§5.1).
- **Fields** = the named, typed pieces of data. **Instance** = a value of the struct type created by
  giving concrete values for each field. The definition is a template; instances fill it in (§5.1).
- Three struct kinds (§5.1): regular (named fields), **tuple structs** (typed positional fields, no
  field names), **unit-like structs** (no fields).
- **Associated functions** = all functions defined in an `impl` block. **Methods** = the associated
  functions whose first parameter is `self`, the instance the method is called on (§5.3).
- Methods are defined in the context of a struct (or, per the text, an enum or a trait object --
  ch. 6 and ch. 18) (§5.3).

## Rules and Semantics

### Defining and instantiating (§5.1)

- Instantiate with the struct name plus `{ key: value }` pairs; field order need not match the
  declaration order.
- Field access and assignment use dot notation: `user1.email`, `user1.email = ...`.
- Mutability is all-or-nothing: the whole instance must be `mut`; individual fields cannot be marked
  mutable.
- A struct expression as the last expression of a function body implicitly returns the new instance.
- **Field init shorthand**: when a variable/parameter has exactly the same name as a field, write
  `email` instead of `email: email`.
- **Struct update syntax**: `..other` fills every field not explicitly set from `other`. It must come
  last; the explicitly set fields may be any number, in any order.
- Struct update **moves** data, like `=` assignment. If a moved field is non-`Copy` (e.g. a `String`
  `username`), the source instance can no longer be used as a whole. If only `Copy` fields
  (`active`, `sign_in_count`) are taken from it, the source stays fully valid. Fields that were not
  moved out (e.g. `user1.email` when `user2` got a new `email`) remain usable.
- Tuple structs: each struct is its own type even when the field types are identical. A function
  taking `Color` will not accept `Point`, though both are three `i32` values.
- Tuple struct instances can be destructured and indexed with `.` plus index, like tuples; but
  destructuring must name the type: `let Point(x, y, z) = origin;`.
- Unit-like structs behave similarly to `()`. Declared with the name and a semicolon; instantiated
  with the bare name -- no curly brackets or parentheses.
- Storing a reference in a struct requires lifetimes (ch. 10), which ensure the referenced data is
  valid as long as the struct is.

### Borrowing structs, printing (§5.2)

- Take `&Rectangle` so the caller keeps ownership and can keep using the instance.
- Accessing fields of a borrowed struct instance does not move the field values.
- `{}` in `println!` uses `Display`: output intended for end users. Primitive types seen so far
  implement it; structs have no provided `Display` implementation because the desired format is
  ambiguous.
- `{:?}` uses `Debug`: developer-oriented output. It is opt-in for structs via the outer attribute
  `#[derive(Debug)]` placed just before the definition.
- `{:#?}` is pretty-printed `Debug`: one field per line, useful for larger structs.
- `dbg!` takes ownership of an expression, prints file and line number of the call plus the
  resulting value, and returns ownership of the value. `println!` takes a reference instead.
- `dbg!` prints to `stderr`; `println!` prints to `stdout`.
- `dbg!` output uses the pretty `Debug` format for a struct; for integers `Debug` prints just the
  value.

### Methods and associated functions (§5.3)

- Everything inside `impl Rectangle { ... }` is associated with the `Rectangle` type.
- `&self` is short for `self: &Self`. Inside an `impl` block, `Self` is an alias for the type the
  block is for. Methods must have a first parameter named `self` of type `Self`; Rust lets you
  abbreviate it to just `self` in that position (the `&` is still needed to borrow).
- Receiver forms: `&self` borrows immutably (read), `&mut self` borrows mutably (change the
  instance), `self` takes ownership -- same choices as any other parameter.
- Extra parameters follow `self` and behave like ordinary function parameters.
- A method may share a name with a field. `rect1.width()` (parentheses) is the method;
  `rect1.width` (no parentheses) is the field.
- **Automatic referencing and dereferencing**: for `object.something()`, Rust automatically adds
  `&`, `&mut`, or `*` so `object` matches the method signature. `p1.distance(&p2)` and
  `(&p1).distance(&p2)` are the same. Method calls are one of the few places with this behavior.
  It works because the receiver type is clear: Rust can tell definitively whether the method reads,
  mutates, or consumes. Rust has no `->` operator.
- Associated functions without `self` are not methods: they need no instance. Called with `::` on the
  type name, e.g. `Rectangle::square(3)`; `String::from` is one.
- `Self` may be used in the return type and in the body of an associated function.
- `new` is a common constructor name but is not special and not built into the language.
- A struct may have multiple `impl` blocks; splitting methods across them is equivalent to one block.

## Syntax and API Reference

```rust
struct User { active: bool, username: String, email: String, sign_in_count: u64 }
let mut user1 = User { active: true, username: String::from("u"), email: String::from("e"),
                       sign_in_count: 1 };
user1.email = String::from("anotheremail@example.com");

fn build_user(email: String, username: String) -> User {
    User { active: true, username, email, sign_in_count: 1 }      // field init shorthand
}
let user2 = User { email: String::from("another@example.com"), ..user1 };  // update syntax

struct Color(i32, i32, i32);         // tuple struct
let black = Color(0, 0, 0);
struct AlwaysEqual;                  // unit-like struct
let subject = AlwaysEqual;

#[derive(Debug)]
struct Rectangle { width: u32, height: u32 }
impl Rectangle {
    fn area(&self) -> u32 { self.width * self.height }
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
    fn square(size: u32) -> Self { Self { width: size, height: size } }  // associated fn
}
let sq = Rectangle::square(3);
```

| Form | Effect | § |
|---|---|---|
| `println!("{rect1}")` | `Display`; fails for a struct without an implementation | 5.2 |
| `println!("{rect1:?}")` / `{:?}` | `Debug`: `Rectangle { width: 30, height: 50 }` | 5.2 |
| `println!("{rect1:#?}")` / `{:#?}` | pretty `Debug`, multi-line | 5.2 |
| `#[derive(Debug)]` | outer attribute opting a type into `Debug` | 5.2 |
| `dbg!(30 * scale)` | prints `[src/main.rs:10:16] 30 * scale = 60` to stderr, returns the value | 5.2 |
| `dbg!(&rect1)` | debug-print without giving up ownership | 5.2 |
| `rect1.area()` | method call syntax | 5.3 |
| `Rectangle::square(3)` | associated function call | 5.3 |

## Decision Rules

- Struct over separate variables: when parameters are related (width and height of one rectangle),
  group them so the signature says so (§5.2).
- Struct over tuple: tuples add structure but do not name elements, so `dimensions.0`/`.1` hides
  meaning and invites mix-ups; named fields convey meaning (§5.2).
- Tuple struct: when you want to name the whole tuple and make it a distinct type, and naming each
  field would be verbose or redundant (§5.1).
- Unit-like struct: when you need to implement a trait on a type but have no data to store (§5.1).
- Owned field types (`String`) over references (`&str`): when each instance should own all its data
  and that data should be valid as long as the struct is. Reference fields need lifetimes (§5.1).
- Receiver choice (§5.3): `&self` to read only; `&mut self` to change the instance; bare `self` is
  rare, typically when the method transforms `self` into something else and the caller must not use
  the original afterwards.
- Method over free function: gives method syntax, avoids repeating the type of `self`, and above all
  organizes everything an instance can do in one `impl` block (§5.3).
- Associated function without `self`: commonly for constructors returning a new instance, or
  convenience constructors like `square` (§5.3).
- Multiple `impl` blocks: no reason to split in simple cases; useful with generic types and traits
  (ch. 10) (§5.3).

## Pitfalls and Compiler Errors

- **E0277 `` `Rectangle` doesn't implement `std::fmt::Display` ``** (§5.2): printing a struct with
  `{}`. Compiler note suggests `{:?}` (or `{:#?}` for pretty-print). Fix: use debug formatting.
- **E0277 `` `Rectangle` doesn't implement `Debug` ``** (§5.2): using `{:?}` without opting in.
  Fix per the help text: annotate the struct with `#[derive(Debug)]`.
- **E0106 `missing lifetime specifier`** (§5.1): fields declared `username: &str`, `email: &str`
  without lifetimes; one error per field. Compiler suggests `struct User<'a>` and `&'a str`. The
  book's fix for now: use owned `String` fields (proper fix in ch. 10).
- Using an instance after struct update moved a non-`Copy` field out of it: `user1` is unusable as a
  whole once its `username` `String` moved into `user2` (§5.1).
- Passing an owned struct to `dbg!` moves it; pass `&rect1` to keep using it (§5.2).
- Expecting to mark a single field `mut`: not allowed; the binding must be `mut` (§5.1).
- Passing a `Point` where a `Color` is expected fails even with identical field types (§5.1).

## Idioms and Best Practices

- Name a struct for the significance of the grouped data; name function parameters the same as the
  fields they initialize and use field init shorthand (§5.1).
- Borrow structs in function signatures (`&Rectangle`) so callers retain ownership; "you often see
  borrows of structs" (§5.2).
- **Getters**: a method named like a field that only returns that field's value. Rust does not
  generate them. They enable read-only access: private field, public method (visibility: ch. 7)
  (§5.3).
- Wrap a sub-expression in `dbg!` in place (`width: dbg!(30 * scale)`): since it returns the value,
  behavior is unchanged (§5.2).
- Use `Self` in constructors' return type and body instead of repeating the type name (§5.3).

## Details Worth Knowing

- The example project is created with Cargo as `rectangles` and run with `cargo run` (§5.2).
- Other derivable traits are listed in Appendix C; implementing traits with custom behavior and
  defining your own is ch. 10. Many attributes other than `derive` exist (Rust Reference,
  "Attributes") (§5.2).
- `stderr` vs `stdout` is covered in ch. 12 (§5.2).
- `::` is used both for associated functions and for namespaces created by modules (ch. 7) (§5.3).
- The `->` sidebar example uses `f64::powi(other.x - self.x, 2)` and `f64::sqrt(...)` on a
  `#[derive(Debug,Copy,Clone)] struct Point { x: f64, y: f64 }` (§5.3).
- An `AlwaysEqual` unit-like struct is imagined as equal to every instance of any other type, e.g.
  for a known result in tests; trait implementation on such types is shown in ch. 10 (§5.1).
