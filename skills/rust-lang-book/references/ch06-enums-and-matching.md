# Ch 6 - Enums and Pattern Matching

Source: The Rust Programming Language ch. 6 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- An enum (enumeration) defines a type by listing its possible *variants*; a value is exactly ONE variant
  at a time. Structs group related fields ("and"); enums say a value is one of a set ("or"). (§6.0, §6.1)
- All variants share the single enum type, so one function/parameter can accept any of them. (§6.1)
- Variants can carry data directly, and each variant may carry different types and amounts of data. An
  enum therefore encodes meaning together with data. (§6.1)
- `Option<T>` is the std enum for "a value or nothing". Rust has no null; absence is opt-in through the
  type system, so the compiler checks that the absent case is handled. (§6.1)
- `match` compares a value against patterns in order and runs the code of the first arm that fits
  (coin-sorting-machine model). Its power: expressive patterns + compiler-verified exhaustiveness. (§6.2)
- `if let` and `let...else` are less verbose forms for when only one pattern matters. (§6.3)

## Rules and Semantics

### Defining and using enums (§6.1)

- Variants are namespaced under the enum identifier and reached with `::` (`IpAddrKind::V4`).
- Each variant name with data also becomes a constructor function: `IpAddr::V4(...)` is a function call
  taking the payload and returning an `IpAddr`. It is defined automatically by the enum definition.
- Variant shapes (all four can coexist in one enum):
  - no data: `Quit`
  - named fields like a struct: `Move { x: i32, y: i32 }`
  - a single value: `Write(String)`
  - several positional values: `ChangeColor(i32, i32, i32)`
- Any kind of data can go in a variant: strings, numeric types, structs, even another enum.
- Equivalent separate structs (unit struct, regular struct, tuple structs) could hold the same data, but
  each would be its own type, so a function could not as easily take "any message".
- Methods are defined on enums with `impl`, exactly as on structs; `self` is the enum value the method
  was called on.
- A user-defined type may reuse a std name (e.g. your own `IpAddr`) without conflict as long as the std
  definition has not been brought into scope.

### `Option<T>` (§6.1)

- Definition in std: `enum Option<T> { None, Some(T), }`.
- `Option`, `Some` and `None` are in the prelude: no import, no `Option::` prefix needed. It is still an
  ordinary enum; `Some(T)` and `None` are variants of type `Option<T>`.
- `<T>` is a generic type parameter: `Some` holds one value of any type, and each concrete `T` makes a
  distinct type (`Option<i32>` is not `Option<char>`).
- Inference: `Some(5)` and `Some('e')` infer their types; a bare `None` cannot, so annotate the whole
  type: `let absent_number: Option<i32> = None;`.
- `Option<T>` and `T` are different types: an `Option<T>` cannot be used as if it were definitely a valid
  `T`. You must convert `Option<T>` to `T` before doing `T` operations.
- Consequence: any value whose type is NOT `Option<T>` can safely be assumed to be present/valid.

### `match` (§6.2)

- Form: `match` keyword, then an expression of ANY type (unlike `if`, whose condition must be a Boolean),
  then arms.
- An arm = pattern, `=>`, code. Arms are separated by commas.
- Arms are tested in order; the first matching pattern's code runs and no later arm is compared.
- Arm code is an expression; the value of the matching arm is the value of the whole `match`.
- Short arm code normally has no curly brackets. Multi-line arm code needs curly brackets, and then the
  comma after that arm is optional. The block's last expression is the arm's value.
- Patterns may be literal values, variable names, wildcards, and more (full catalogue in ch. 19).
- Binding: a variable inside a pattern binds to the matching part of the value, which is how data is
  extracted from a variant (`Coin::Quarter(state)` binds `state`; `Some(i)` binds `i`).
- Exhaustive: the arms' patterns must cover every possibility, otherwise the code does not compile. The
  compiler reports which pattern is missing.
- Catch-all: a final arm whose pattern is a variable name matches every remaining value and binds it.
- `_` is a special pattern matching any value WITHOUT binding it; signals the value is unused, so no
  unused-variable warning.
- A catch-all (named or `_`) must be last, since patterns are evaluated in order; arms after a catch-all
  would never run and Rust warns about them.
- "Do nothing" arm: use the unit value as the code: `_ => ()`.

### `if let` and `let...else` (§6.3)

- `if let PATTERN = EXPRESSION { ... }`: pattern and expression separated by an equal sign. Works like a
  `match` where the expression is the scrutinee and the pattern is its first arm; the block runs only
  when the value matches, with the pattern's bindings available inside the block.
- It is syntax sugar for a `match` that runs code for one pattern and ignores all other values.
- `if let ... else { ... }`: the `else` block is the code of the `_` arm in the equivalent `match`.
- `if let` is an expression, so it can produce a value or return early:
  `let state = if let Coin::Quarter(state) = coin { state } else { return None; };`
- `let PATTERN = EXPRESSION else { ... };`: pattern on the left, expression on the right, no `if` branch,
  only an `else` branch.
  - Pattern matches: the bindings are created in the OUTER (enclosing) scope.
  - Pattern does not match: control flows into the `else` arm, which must return from the function.

## Syntax and API Reference

```rust
enum IpAddrKind { V4, V6 }                       // unit-like variants
enum IpAddr { V4(u8, u8, u8, u8), V6(String) }   // different data per variant
enum Message {
    Quit,
    Move { x: i32, y: i32 },
    Write(String),
    ChangeColor(i32, i32, i32),
}
impl Message { fn call(&self) { /* ... */ } }
let m = Message::Write(String::from("hello"));
m.call();
```

```rust
match coin {
    Coin::Penny => {
        println!("Lucky penny!");
        1
    }
    Coin::Nickel => 5,
    Coin::Quarter(state) => { println!("State quarter from {state:?}!"); 25 }
    // ...
}

fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        None => None,
        Some(i) => Some(i + 1),
    }
}

match dice_roll {
    3 => add_fancy_hat(),
    7 => remove_fancy_hat(),
    other => move_player(other),   // or `_ => reroll(),` or `_ => (),`
}
```

```rust
if let Some(max) = config_max { println!("The maximum is configured to be {max}"); }

if let Coin::Quarter(state) = coin { /* use state */ } else { count += 1; }

let Coin::Quarter(state) = coin else {
    return None;
};
// `state` usable here, on the happy path
```

| Item | What the chapter says |
|---|---|
| `Option<T>` / `Some(T)` / `None` | prelude; presence or absence of a value (§6.1) |
| `std::net::IpAddr` | std enum `V4(Ipv4Addr)`, `V6(Ipv6Addr)`; payloads are two structs (§6.1) |
| `#[derive(Debug)]` on an enum | lets a variant be printed with `{state:?}` (§6.2) |
| `Some(3u8)` | literal with type suffix gives `Option<u8>` (§6.3) |
| `_ => ()` | catch-all arm that runs no code (§6.2) |

## Decision Rules

- Enum vs struct: use an enum when a value is one of a fixed set of possibilities that should all be
  handled as the same type; use it instead of "struct with a kind field plus data" by putting the data
  in the variants (more concise, and variants may differ in payload). (§6.1)
- Enum vs several separate structs: prefer the enum when functions must accept any of the kinds. (§6.1)
- Use `Option<T>` whenever a value may be absent; plain `T` everywhere else. (§6.1)
- `match` vs `if let`: `if let` means less typing, indentation and boilerplate (no `_ => ()` arm) but
  gives up exhaustiveness checking. Choose by whether conciseness is worth losing that check. (§6.3)
- `match` when several cases need handling; `if let` when only one does. (§6.3 summary)
- Named catch-all (`other`) when the arm uses the value; `_` when it does not. (§6.2)
- `let...else` when the pattern is to extract a value or bail out early: keeps the main body on the
  "happy path" instead of nesting the work in an `if let` body or mixing a value-producing branch with
  a returning branch. (§6.3)
- If logic is too verbose as a `match`, reach for `if let` / `let...else`. (§6.3)

## Pitfalls and Compiler Errors

- **E0277** `cannot add `Option<i8>` to `i8``: `let sum = x + y;` with `x: i8`, `y: Option<i8>`. Help
  text: the trait `Add<Option<i8>>` is not implemented for `i8`. Cause: `Option<T>` is not `T`. Fix:
  get the `T` out first, handling both variants (e.g. with `match`). (§6.1)
- **E0004** `non-exhaustive patterns: `None` not covered`: a `match` on `Option<i32>` with only a
  `Some(i)` arm. The compiler names the uncovered pattern and suggests adding a wildcard arm or the
  explicit pattern (its suggestion shows `None => todo!(),`). Fix: add the missing arm. (§6.2)
- Catch-all arm placed before other arms: later arms can never run; Rust warns. Put it last. (§6.2)
- Binding a catch-all to a name you never use triggers an unused-variable warning; use `_`. (§6.2)
- `match` used for a single interesting case forces boilerplate `_ => ()`; use `if let`. (§6.3)
- `if let` silently ignores non-matching values: a forgotten case is not flagged. (§6.3)
- Nested conditionals inside an `if let` body obscure how top-level branches relate as the work grows;
  the value-or-return `if let` form is also awkward to follow. `let...else` addresses both. (§6.3)
- A bare `None` with no annotation or other context cannot have its `T` inferred. (§6.1)

## Idioms and Best Practices

- The pervasive Rust pattern: `match` on an enum, bind a variable to the inner data, run code using
  it. (§6.2)
- Handle an `Option<T>` by writing code for each variant: code for `Some(T)` may use the inner `T`;
  code for `None` has no `T`. (§6.1)
- Get familiar with the many methods on `Option<T>` (see its std documentation); the book calls this
  "extremely useful". (§6.1)
- Model domain concepts with custom struct and enum types in your API: the compiler then guarantees
  functions only receive values of the type they expect. (§6.3 summary)
- Keep short arms brace-free; use a block only for multi-statement arms. (§6.2)
- Methods on enums commonly `match self` over the variants (e.g. `fn existed_in(&self, year: u16) ->
  bool`). (§6.3)
- Derive `Debug` on enums you want to inspect in output. (§6.2)

## Details Worth Knowing

- Why no null: null's concept (a currently invalid or absent value) is useful, but its implementation
  makes it easy to use a null as a not-null value. Tony Hoare called null his "billion-dollar mistake"
  (2009 talk). Exhaustive `match` on `Option<T>` makes that mistake impossible. (§6.1, §6.2)
- The name "enumeration" comes from enumerating all possible variants. (§6.1)
- std types are "often not much more complicated" than what you would write yourself; `IpAddr` is the
  example. (§6.1)
- `match` returning `None => None` simply propagates absence; `Some(i) => Some(i + 1)` rebuilds a new
  `Some`. (§6.2)
- The unit value `()` is the empty tuple type introduced in ch. 3 ("The Tuple Type"). (§6.2)
- A catch-all satisfies exhaustiveness for types with many values (e.g. `u8`) without listing them. (§6.2)
- In the chapter's examples, matching `coin` by value in `match`/`if let`/`let...else` binds the
  variant's payload (`state`) for use in the following code. (§6.2, §6.3)
- Forward references: generics and `<T>` in ch. 10; all pattern kinds in ch. 19; bringing types into
  scope and modules in ch. 7. (§6.1, §6.2, §6.3)
