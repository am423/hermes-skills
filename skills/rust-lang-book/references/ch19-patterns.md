# Ch 19 - Patterns and Matching

Source: The Rust Programming Language ch. 19 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- A **pattern** is special syntax for matching against the structure ("shape") of a value. It is built from
  some combination of: literals; destructured arrays, enums, structs, or tuples; variables; wildcards;
  placeholders. Examples: `x`, `(a, 3)`, `Some(Color::Red)` (§19.0).
- Using a pattern = comparing it to a value. If the value fits, the named pieces are bound and usable; if
  not, the code tied to that pattern does not run (§19.0).
- **Irrefutable** pattern: matches every possible value (`x` in `let x = 5;`). **Refutable** pattern: can
  fail for some value (`Some(x)` fails on `None`) (§19.2).
- A plain variable name is the simplest pattern: "bind everything to this name, whatever the value" (§19.1).
- Each construct that accepts a pattern requires or expects a particular refutability (table below).

## Rules and Semantics

### Where patterns appear (§19.1)
- `match VALUE { PATTERN => EXPRESSION, ... }`: must be exhaustive. A final catch-all arm (a variable name,
  or `_`) guarantees coverage. `_` matches anything and never binds.
- `let PATTERN = EXPRESSION;`: Rust compares the expression to the pattern and assigns the names it finds.
  A tuple pattern must have the same number of elements as the tuple or the types do not match.
- `if let` / `else if` / `else if let` / `else` can be mixed freely; the conditions need not relate to each
  other, unlike `match`, which compares one value against all its patterns.
- `if let` can introduce a variable that shadows an outer one (`if let Ok(age) = age`). The new binding is
  valid only once the new scope starts at the curly bracket, so the book puts the test on it inside
  the block and says `if let Ok(age) = age && age > 30` cannot combine the two.
  **Compiler check (not from the book):** rustc 1.99.1 with edition 2024 compiles exactly that
  form, in `if let` and in `while let`, and the new binding is usable after `&&`. Prefer the chained
  form on edition 2024; nest the test only on older editions.
- `if let` chains are NOT checked for exhaustiveness; omitting the final `else` silently skips cases.
- `while let PATTERN = EXPR { }` loops as long as the pattern keeps matching (e.g. `Ok(value) = rx.recv()`
  until the sender disconnects and `recv` yields `Err`).
- `for PATTERN in ITER`: whatever directly follows `for` is a pattern (`for (index, value) in
  v.iter().enumerate()`).
- Function parameters are patterns (`fn foo(x: i32)`; `fn print_coordinates(&(x, y): &(i32, i32))`).
  Closure parameter lists accept patterns the same way.

### Refutability (§19.2)
- Function parameters, `let` statements, and `for` loops accept only irrefutable patterns: the program has
  nothing meaningful to do on a failed match.
- `if let`, `while let`, and `let...else` accept both kinds, but the compiler warns on an irrefutable one,
  since these constructs exist to handle possible failure.
- `match` arms must use refutable patterns except the last arm, which should cover remaining values with an
  irrefutable pattern. A one-arm `match` with an irrefutable pattern is allowed but is better written as a
  plain `let`.
- When refutability shows up in an error, change either the pattern or the construct, depending on intent.

### Named variables and shadowing (§19.3)
- Named variables are irrefutable and match any value.
- `match`, `if let`, and `while let` each start a new scope; a variable named in a pattern there shadows any
  outer variable of the same name. `Some(y)` in an arm binds a NEW `y`; it does not compare with outer `y`.
- The shadowing binding ends with the construct's scope; the outer variable is unchanged afterwards.
- To compare against an outer variable, use a match guard (`Some(n) if n == y`). A guard is not a pattern
  and introduces no variables, so `y` in it is the outer `y`.

### Multiple patterns and ranges (§19.3)
- `|` is the pattern *or* operator: an arm runs if any alternative matches.
- `..=` matches an inclusive range. The compiler checks at compile time that the range is not empty, which
  it can only do for numeric and `char` values, so ranges are allowed only for those types.

### Destructuring (§19.3)
- Struct: `Point { x: a, y: b }` binds fields to new names; shorthand `Point { x, y }` creates variables
  named after the fields. Literals can replace some fields to test them while binding the others.
- `match` stops at the first matching arm: `Point { x: 0, y: 0 }` hits the first arm that fits, not all.
- Enum: the pattern mirrors how the variant's data is defined.
  - Unit-like variant (`Message::Quit`): matched only as the literal value; binds nothing.
  - Struct-like variant (`Message::Move { x, y }`): curly brackets with fields, shorthand allowed.
  - Tuple-like variant (`Message::Write(text)`, `Message::ChangeColor(r, g, b)`): parentheses; the number
    of variables must equal the number of elements.
- Patterns nest to any depth, across enums, structs, and tuples in one pattern.

### Ignoring values (§19.3)
- `_` matches any value and does not bind. Usable in any pattern, including function parameters.
- `_` nested inside a pattern ignores just that part; it can appear several times in one pattern.
- `_name` suppresses the unused-variable warning but STILL binds, so it can take ownership. `_` alone never
  binds, so nothing is moved.
- `..` ignores every part not explicitly matched. In structs: `Point { x, .. }`. In tuples it expands to as
  many values as needed: `(first, .., last)`.
- `..` must be unambiguous: at most once per tuple pattern.

### Match guards (§19.3)
- A match guard is an extra `if` condition after the pattern in a `match` arm; the arm is chosen only if
  the pattern matches AND the condition holds. It can use variables bound by the pattern.
- Per the book, guards are available only in `match` expressions, not in `if let` or `while let`.
  On edition 2024 a `&&` condition after the pattern gives `if let` / `while let` the same effect
  (see the compiler check under §19.1 above).
- If the guard is false, matching continues with the next arm.
- The compiler does not try to check exhaustiveness when match guard expressions are involved.
- Precedence with `|`: the guard applies to the whole alternation. `4 | 5 | 6 if y` behaves as
  `(4 | 5 | 6) if y`, not `4 | 5 | (6 if y)`.

### `@` bindings (§19.3)
- `name @ PATTERN` tests a value against the pattern and binds it to `name` in one step.
- A bare range in a field position (`id: 10..=12`) tests but leaves no variable holding the value.
- A bare field name (`id`, shorthand) binds but tests nothing: any value matches.

## Syntax and API Reference

### Every place a pattern can be used (§19.1, §19.2)

| Construct | Form | Refutable allowed? | Notes |
|---|---|---|---|
| `match` arm | `PATTERN => EXPRESSION,` | yes (last arm should be irrefutable) | exhaustive; guards allowed |
| `let` statement | `let PATTERN = EXPRESSION;` | no (E0005) | destructuring allowed |
| `let...else` | `let PATTERN = EXPR else { ... };` | yes; warns if irrefutable | block handles non-match |
| `if let` | `if let PATTERN = EXPR { } else { }` | yes; warns if irrefutable | no exhaustiveness check |
| `else if let` | chained after `if` / `if let` | yes | conditions may be unrelated |
| `while let` | `while let PATTERN = EXPR { }` | yes; warns if irrefutable | loops while matching |
| `for` loop | `for PATTERN in ITER { }` | no | pattern follows `for` |
| Function parameter | `fn f(PATTERN: Type)` | no | e.g. `&(x, y): &(i32, i32)` |
| Closure parameter | same as function parameters | no | "in the same way" as functions |

### Every pattern syntax form (§19.3)

| Form | Example | Meaning |
|---|---|---|
| Literal | `1`, `'a'`, `Some(50)` | matches that concrete value |
| Named variable | `x`, `Some(y)` | irrefutable; binds; shadows outer names in new scopes |
| Or | `1 \| 2` | matches any alternative |
| Inclusive range | `1..=5`, `'a'..='j'` | numeric or `char` only; non-empty checked at compile time |
| Struct, renamed | `Point { x: a, y: b }` | binds fields to `a`, `b` |
| Struct, shorthand | `Point { x, y }` | binds variables named like the fields |
| Struct with literal | `Point { x, y: 0 }` | tests `y`, binds `x` |
| Unit-like variant | `Message::Quit` | matches the variant; no bindings |
| Struct-like variant | `Message::Move { x, y }` | destructures named fields |
| Tuple-like variant | `Message::ChangeColor(r, g, b)` | arity must match the variant |
| Nested | `Message::ChangeColor(Color::Rgb(r, g, b))` | patterns inside patterns |
| Tuple | `(x, y, z)` | arity must match |
| Mixed nesting | `((feet, inches), Point { x, y })` | structs and tuples inside a tuple |
| Reference | `&(x, y)` | matches a `&(i32, i32)` argument, binding the inner values |
| Wildcard | `_` | matches anything, binds nothing |
| Nested wildcard | `(Some(_), Some(_))`, `(first, _, third, _, fifth)` | ignore parts |
| Underscore name | `_x`, `Some(_s)` | binds, but no unused warning |
| Rest in struct | `Point { x, .. }` | ignore remaining fields |
| Rest in tuple | `(first, .., last)` | ignore the middle; once per tuple |
| Match guard | `Some(x) if x % 2 == 0` | extra condition; `match` arms only |
| Or + guard | `4 \| 5 \| 6 if y` | guard covers all alternatives |
| At binding | `Message::Hello { id: id @ 3..=7 }` | test against range and bind to `id` |

## Decision Rules

- Need every case handled and checked by the compiler -> `match` (§19.1).
- Care about one case, or need unrelated conditions in sequence -> `if let` with `else if` / `else if let`;
  accept that missing cases are not reported (§19.1).
- Refutable pattern where a plain `let` was written -> switch to `let...else` and handle the miss in the
  block (§19.2).
- Many alternative values -> a range `1..=5` rather than `1 | 2 | 3 | 4 | 5` (§19.3).
- Comparing with an outer variable, or a condition a pattern cannot express -> match guard (§19.3).
- Need the value AND a test on it -> `name @ pattern` (§19.3).
- Ignore one position -> `_`; ignore everything else -> `..`, quicker than listing `y: _, z: _` (§19.3).
- Unused function parameter: normally remove it from the signature; use `_` when a fixed signature is
  required (e.g. implementing a trait) and the body does not need it, which also avoids the unused-parameter
  warning a name would cause (§19.3).
- Unused variable while prototyping -> `_x`; but use `_` when the value must not be moved (§19.3).

## Pitfalls and Compiler Errors

- **E0308** `mismatched types` ("expected a tuple with 3 elements, found one with 2 elements"):
  `let (x, y) = (1, 2, 3);`. Fix: ignore values with `_` or `..`, or, with too many variables, remove some
  so the counts agree (§19.1).
- **E0005** `refutable pattern in local binding` ("pattern `None` not covered"):
  `let Some(x) = some_option_value;`. `let` bindings require an irrefutable pattern. Fix:
  `let Some(x) = some_option_value else { return; };` (§19.2).
- Warning `unreachable `else` clause`, lint `#[warn(irrefutable_let_patterns)]` (on by default):
  `let x = 5 else { return; };`. The pattern always matches, so the `else` can never run (§19.2).
- Error `` `..` can only be used once per tuple pattern ``: `(.., second, ..)`. Rust cannot tell how many
  values to skip on each side; a variable name like `second` carries no positional meaning (§19.3).
- Accidental shadowing: `Some(y)` in a `match` arm binds a new `y` and matches any `Some`; with
  `x = Some(5)`, `y = 10` it prints `Matched, y = 5`, and outer `y` is still `10` afterwards (§19.3).
- `_s` moves: `if let Some(_s) = s { }` followed by a use of `s` is a compile error because the value was
  moved into `_s`. `if let Some(_) = s` compiles since nothing is bound (§19.3).
- Guard precedence misread: with `x = 4`, `y = false`, the arm `4 | 5 | 6 if y` does not match and the
  program prints `no` (§19.3).
- Guards weaken checking: exhaustiveness is not checked for guard expressions, so keep a guard-free arm for
  the remaining cases (as the book's examples do with `Some(x)` and `_`) (§19.3).
- Arm order matters: only the first matching arm runs (§19.3).

## Idioms and Best Practices

- Prefer struct field shorthand; matching variable names to field names makes the origin of each variable
  easy to remember and avoids `Point { x: x, y: y }` duplication (§19.3).
- Put `_` (or a variable name) in the last `match` arm as the catch-all (§19.1).
- Use `(Some(_), Some(_))` on a tuple of options to test variants without using their contents (§19.3).
- Destructure tuples directly in `let`, `for`, and parameters to name pieces at once (§19.1).
- Use `_ => ()` to do nothing for the remaining variants (§19.3).

## Details Worth Knowing

- `let...else` is the book's stated fix for a refutable pattern in `let`; the compiler's own help text
  suggests it (`else { todo!() }`) (§19.2).
- The E0005 note describes an irrefutable pattern as, for example, "a `struct` or an `enum` with only one
  variant" (§19.2).
- In `&(x, y): &(i32, i32)` called with `&(3, 5)`, `x` is `3` and `y` is `5` (§19.1).
- `enumerate` yields `(index, value)` tuples, first `(0, 'a')` (§19.1).
- `recv` returns `Ok` per message while the sender exists, then `Err` after it disconnects (§19.1).
- The chapter intro lists arrays among destructurable types, but §19.3 shows no array pattern examples.
- Next chapter (ch. 20) covers advanced features.
