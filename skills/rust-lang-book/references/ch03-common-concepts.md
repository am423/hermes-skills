# Ch 3 - Common Programming Concepts

Source: The Rust Programming Language ch. 3 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).
Section refs: §3.0 intro, §3.1 Variables and Mutability, §3.2 Data Types, §3.3 Functions,
§3.4 Comments, §3.5 Control Flow.

## Core Model

- **Immutable by default (§3.1):** once a value is bound to a name it cannot change unless the
  variable is declared `mut`. The compiler guarantees a value declared unchanging never changes,
  which makes code easier to reason about. `mut` also signals intent to readers.
- **Constant (§3.1):** a name bound to a value that is *always* immutable, declared with `const`,
  with a mandatory type annotation, set only to a constant expression.
- **Shadowing (§3.1):** a second `let` with the same name creates a *new* variable; the compiler
  sees the newer one until it is itself shadowed or the scope ends.
- **Statically typed (§3.2):** every value has a data type and all variable types must be known at
  compile time; usually inferred from the value and its use.
- **Scalar vs compound (§3.2):** scalar types hold a single value (integers, floating-point,
  Booleans, characters); compound types group several values (tuples, arrays).
- **Statement vs expression (§3.3):** statements perform an action and return no value;
  expressions evaluate to a value. Rust is an expression-based language.
- **Function body (§3.3):** a series of statements optionally ending in an expression; the return
  value is the value of the final expression in the body block.
- **Unit (§3.2):** the tuple with no values. Value and type are both written `()`; it represents
  an empty value or empty return type. Expressions that return nothing else implicitly return it.
- **Keywords (§3.0):** reserved words that cannot be used as variable or function names; a few
  have no current function and are reserved for the future (list in Appendix A).

## Rules and Semantics

### Variables, constants, shadowing (§3.1)
- Assigning twice to a non-`mut` variable is a compile-time error.
- `const` differences from `let`: `mut` is not allowed; the type *must* be annotated; may be
  declared in any scope including global; value must be a constant expression, never something
  computable only at runtime.
- Constants are valid for the entire run of the program, within the scope where they are declared.
- The compiler can evaluate a limited set of operations at compile time, so `60 * 60 * 3` is a
  legal constant initializer.
- Shadowing inside an inner `{}` scope ends when that scope ends; the outer binding is visible again.
- Shadowing vs `mut`: shadowing requires `let` each time (plain reassignment without `let` is still
  an error) and the binding stays immutable afterwards; shadowing may change the value's *type*,
  whereas a `mut` variable can never change type.

### Scalar types (§3.2)
- Signed integers `iN` store -(2^(n-1)) to 2^(n-1) - 1 (two's complement); unsigned `uN` store
  0 to 2^n - 1. `i8`: -128..127; `u8`: 0..255.
- `isize` / `usize` are architecture-dependent: 64 bits on 64-bit, 32 bits on 32-bit.
- Integer literals default to `i32`; float literals default to `f64`.
- Integer overflow: debug builds include checks that *panic* at runtime; `--release` builds do not
  check and perform two's complement wrapping (for `u8`, 256 becomes 0, 257 becomes 1). Relying on
  wrapping is considered an error.
- Floats: `f32` and `f64`, both signed, IEEE-754. `f64` is the default because on modern CPUs it is
  roughly as fast as `f32` with more precision.
- Numeric operations on all number types: addition, subtraction, multiplication, division,
  remainder. Integer division truncates toward zero (`-5 / 3` is `-1`).
- `bool`: values `true` and `false`, one byte in size.
- `char`: single-quoted literal, 4 bytes, a Unicode scalar value (`U+0000`..`U+D7FF` and
  `U+E000`..`U+10FFFF`), so it covers accented letters, CJK, emoji, zero-width spaces.

### Compound types (§3.2)
- Tuple: fixed length (cannot grow or shrink once declared); element types may differ. Access by
  destructuring with a `let` pattern or by `.index` (first index is 0).
- Array: every element has the same type; fixed length; a single chunk of memory of known, fixed
  size that can be allocated on the stack.
- Array indexing is bounds-checked at runtime: an index greater than or equal to the length panics
  instead of reading invalid memory.

### Functions (§3.3)
- Definition order does not matter; a function only needs to be defined in a scope visible to the
  caller.
- Every parameter's type *must* be declared in the signature. Rationale: the compiler then almost
  never needs annotations elsewhere, and can give better error messages.
- Return type is declared after `->`; return values are not named.
- `return value` exits early; most functions return the last expression implicitly.
- `let` is a statement and yields no value, so `x = y = 6`-style chaining does not exist. Function
  definitions are statements too.
- Expressions include: math operations, literals, function calls, macro calls, and `{}` scope
  blocks. A block evaluates to its final expression.
- Expressions have no ending semicolon; adding one turns the expression into a statement that
  returns no value.

### Control flow (§3.5)
- `if` condition *must* be a `bool`; there is no automatic conversion of non-Boolean types.
- `else` is optional; without it a false condition just skips the block.
- `else if` chains run only the block for the first `true` condition; later ones are not checked.
- `if` is an expression and can be the right side of a `let`. All arms must produce the same type,
  because a variable has a single type known at compile time.
- Three loops: `loop`, `while`, `for`.
- `loop` repeats forever until told to stop. `break` exits; `continue` skips the rest of the
  iteration and goes to the next one.
- `break <expr>` makes that value the value of the `loop` expression.
- `break` exits only the current loop; `return` always exits the current function.
- In nested loops `break`/`continue` apply to the innermost loop unless given a *loop label*
  (must start with a single quote), e.g. `break 'counting_up;`.
- `while cond { }` runs while the condition is `true`.
- `for x in collection { }` runs the body once per item.

## Syntax and API Reference

| Length | Signed | Unsigned |
| --- | --- | --- |
| 8 / 16 / 32 / 64 / 128-bit | `i8` `i16` `i32` `i64` `i128` | `u8` `u16` `u32` `u64` `u128` |
| Architecture-dependent | `isize` | `usize` |

| Integer literal | Example |
| --- | --- |
| Decimal / Hex / Octal / Binary | `98_222` / `0xff` / `0o77` / `0b1111_0000` |
| Byte (`u8` only) | `b'A'` |

- Type suffix on literals that could be several numeric types: `57u8`. `_` is a visual separator:
  `1_000` equals `1000` (§3.2).
- Overflow method families on primitive numeric types (§3.2): `wrapping_*` (e.g. `wrapping_add`)
  wraps in all modes; `checked_*` returns `None` on overflow; `overflowing_*` returns the value
  plus a Boolean overflow flag; `saturating_*` clamps at the type's minimum or maximum.

```rust
const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 * 3;         // §3.1
let spaces = "   "; let spaces = spaces.len();          // shadowing changes type
let tup: (i32, f64, u8) = (500, 6.4, 1);                 // §3.2 tuple
let (x, y, z) = tup;  let first = tup.0;                 // destructure / index
let a: [i32; 5] = [1, 2, 3, 4, 5];                       // array type [T; N]
let b = [3; 5];                                          // same as [3, 3, 3, 3, 3]
fn plus_one(x: i32) -> i32 { x + 1 }                     // §3.3 tail expression
let y = { let x = 3; x + 1 };                            // block expression -> 4
let number = if condition { 5 } else { 6 };              // §3.5
let result = loop { counter += 1; if counter == 10 { break counter * 2; } };
'counting_up: loop { loop { break 'counting_up; } }      // loop label
while number != 0 { number -= 1; }
for element in a { println!("the value is: {element}"); }
for number in (1..4).rev() { println!("{number}!"); }    // prints 3, 2, 1
```

- `Range` (std) generates the numbers in sequence from a start up to but not including an end;
  `rev` reverses it (§3.5).
- Comments (§3.4): `//` to end of line; multi-line comments repeat `//` on every line.

## Decision Rules

- Mutability is a judgment call: use whichever is clearest in the situation (§3.1).
- Use `const` for hardcoded domain values many parts of the program need (e.g. a maximum score):
  the name conveys meaning and there is one place to update (§3.1).
- Use shadowing to apply a few transformations and end with an immutable binding, or to convert a
  value's type while keeping one name instead of `spaces_str` / `spaces_num` (§3.1).
- Integer choice: start from the `i32` default when unsure; use `isize`/`usize` mainly for indexing
  a collection (§3.2).
- Array vs vector: array when data should live on the stack or the element count is fixed and
  known (e.g. the 12 month names); otherwise, and when unsure, use a vector (§3.2).
- More than one `else if` suggests refactoring, typically to `match` (ch. 6) (§3.5).
- Use `loop` to retry an operation that might fail and to pass a result out via `break` (§3.5).
- Use `while` instead of hand-rolled `loop` + `if` + `else` + `break`: less nesting, clearer (§3.5).
- Prefer `for` over index-based `while` for collections: safer (no out-of-bounds or missed items),
  more concise, and can be more efficient since no per-iteration bounds comparison is needed.
  `for` is the most commonly used loop; use it with a range even for counted repetition (§3.5).

## Pitfalls and Compiler Errors

- **E0384** "cannot assign twice to immutable variable" (§3.1): reassigning a non-`mut` binding.
  Fix: `let mut x = 5;` (the compiler's own suggestion) or shadow with a new `let`.
- **E0308** mismatched types, "expected `&str`, found `usize`" (§3.1): `let mut spaces = "   ";
  spaces = spaces.len();`. Fix: shadow with `let spaces = spaces.len();`.
- **E0284** "type annotations needed" (§3.2): `let guess = "42".parse().expect(...)` with no type.
  Fix: annotate, `let guess: u32 = ...`.
- **"expected expression, found `let` statement"** (no code) (§3.3): `let x = (let y = 6);`.
- **E0308** "expected `i32`, found `()`" (§3.3): body ends in `x + 1;`, so the function implicitly
  returns `()`. Fix: remove the semicolon.
- **E0308** "expected `bool`, found integer" (§3.5): `if number { }`. Fix: `if number != 0 { }`.
- **E0308** "`if` and `else` have incompatible types" (§3.5): arms yield an integer and a `&str`.
- **Runtime panic** "index out of bounds: the len is 5 but the index is 10" (§3.2): the code
  compiles; the check can only happen at runtime for user-supplied indexes.
- **Index-based `while` over an array** (§3.5): panics if the condition is not updated when the
  array shrinks, and is slower because of the bounds check on every iteration.
- **Overflow** (§3.2): behavior differs between debug (panic) and release (wrap); handle it
  explicitly with the method families above.

## Idioms and Best Practices

- Constants: all uppercase with underscores between words, e.g. `THREE_HOURS_IN_SECONDS` (§3.1).
- Write constant values as readable computations (`60 * 60 * 3`) rather than `10800` (§3.1).
- Functions and variables use snake case: lowercase with underscores (§3.3).
- Comments usually go on their own line above the code they annotate; end-of-line comments are
  allowed but less common (§3.4).

## Details Worth Knowing

- A `char` may not match the human notion of a "character"; see ch. 8 on strings (§3.2).
- Parameters are the variables in a signature and arguments the concrete values, though the terms
  are used interchangeably in casual speech (§3.3).
- Blocks tied to `if` conditions are sometimes called *arms*, like `match` arms (§3.5).
- Most terminals interrupt a stuck loop with ctrl-C (§3.5).
- Forward references: stack vs heap ch. 4; `match` ch. 6; vectors and strings ch. 8; panics and
  error handling ch. 9; documentation comments ch. 14; keywords Appendix A; operators Appendix B.
