# Ch 20 - Advanced Features: Advanced Traits, Types, Functions and Closures

Source: The Rust Programming Language ch. 20 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).
Covers §20.2 (Advanced Traits), §20.3 (Advanced Types), §20.4 (Advanced Functions and Closures).

## Core Model

- **Associated type**: a type placeholder attached to a trait, usable in its method signatures; the
  implementor names the concrete type once per implementation (§20.2).
- **Default type parameter**: `<PlaceholderType=ConcreteType>` on a generic declaration; implementors
  may omit the parameter when the default fits (§20.2).
- **Operator overloading**: you cannot create new operators or overload arbitrary ones; you CAN overload
  the operations listed in `std::ops` by implementing the corresponding trait (§20.2).
- **Fully qualified syntax**: `<Type as Trait>::function(receiver_if_method, next_arg, ...)`, the most
  explicit way to name which implementation to call (§20.2).
- **Supertrait**: a trait your trait depends on; implementors of your trait must also implement it, so
  your trait can use its associated items (§20.2).
- **Newtype pattern**: a one-field tuple struct thinly wrapping another type, creating a distinct local
  type. No runtime penalty; the wrapper is elided at compile time. Term comes from Haskell (§20.2).
- **Type alias**: `type Name = Existing;` creates a *synonym*, not a new type (§20.3).
- **Never type `!`**: the empty type (no values); stands in as the return type of functions that never
  return, called *diverging functions* (§20.3).
- **Dynamically sized types (DSTs / unsized types)**: types whose size is known only at runtime, e.g.
  `str` (not `&str`) and every trait when named as a type (§20.3).
- **Function pointer**: the type `fn` (lowercase), distinct from the `Fn` closure trait (§20.4).
- **Opaque type**: the unique, unnameable type Rust creates for each `impl Trait` return (§20.4).

## Rules and Semantics

### Associated types vs generics (§20.2)

- `Iterator` has associated type `Item`; `next` returns `Option<Self::Item>`.
- With a generic trait (`Iterator<T>`), a type could implement the trait many times with different `T`,
  and every use of `next` would need annotations to pick the implementation.
- With an associated type there can be only one `impl Iterator for Counter`, so `Item` is chosen once and
  callers never annotate it.
- Associated types are part of the trait's contract: implementors must supply a type for the placeholder.

### Default type parameters and `Add` (§20.2)

- `trait Add<Rhs=Self> { type Output; fn add(self, rhs: Rhs) -> Self::Output; }`.
- `Rhs` ("right-hand side") is the type of the `rhs` parameter; if unspecified in an `impl`, it defaults
  to `Self`, the type `Add` is being implemented on. `Output` is the type returned by `add`.
- `impl Add for Point` uses the default; `impl Add<Meters> for Millimeters` sets `Rhs` explicitly to add
  two different types (with the unit conversion done inside `add`).

### Same-named methods and associated functions (§20.2)

- Nothing stops two traits from having a method of the same name, one type implementing both, or the
  type also having an inherent method with that name.
- `person.fly()` defaults to the method implemented directly on the type.
- `Pilot::fly(&person)` / `Wizard::fly(&person)` select a trait's method; `Human::fly(&person)` is
  equivalent to `person.fly()`.
- For methods, the `self` argument lets Rust pick the implementation when several *types* implement one
  trait.
- Associated functions that are not methods have no `self`: `Dog::baby_name()` calls the inherent
  function; `Animal::baby_name()` is an error (E0790); `<Dog as Animal>::baby_name()` calls the trait's
  implementation for `Dog`.
- Fully qualified syntax is usable everywhere, but any part Rust can infer may be omitted; it is needed
  only when several implementations share a name.

### Supertraits (§20.2)

- Syntax: `trait OutlinePrint: fmt::Display { ... }`; similar to adding a trait bound to the trait.
- Inside the trait's default methods you may then call supertrait functionality, e.g. `self.to_string()`
  (automatically available for any type implementing `Display`).
- Without the `: Display`, the call fails: no method named `to_string` found for type `&Self`.
- Implementing the trait for a type lacking the supertrait is an error (E0277).

### Newtype and the orphan rule (§20.2, §20.3)

- Orphan rule: a trait can be implemented on a type only if the trait or the type, or both, are local to
  the crate. A local wrapper such as `struct Wrapper(Vec<String>);` sidesteps it; implement the external
  trait on `Wrapper` and reach the inner value via `self.0`.
- Downside: the wrapper has none of the inner type's methods.
  - Want all of them: implement `Deref` on the wrapper to return the inner type (ch. 15).
  - Want only some (to restrict behavior): implement just those methods manually, delegating to `self.0`.
- Other newtype uses (§20.3): statically prevent mixing up values and indicate units (`Millimeters` vs
  `Meters` vs plain `u32`); expose a public API different from the private inner type's; hide internal
  representation (e.g. a `People` type wrapping `HashMap<i32, String>`) as lightweight encapsulation.

### Type aliases (§20.3)

- `type Kilometers = i32;`: `Kilometers` and `i32` are the same type; values mix freely (`x + y`) and
  pass to `i32` parameters. No newtype-style checking: mix-ups are not compile errors.
- Aliases can be generic: `type Result<T> = std::result::Result<T, std::io::Error>;`, as declared in
  `std::io` and used as `std::io::Result<T>`.
- An alias is still the underlying type: all `Result<T, E>` methods and the `?` operator work.

### Never type (§20.3)

- `fn bar() -> ! { ... }` reads "returns never"; values of `!` cannot be created.
- Expressions of type `!` can be coerced into any other type. This is why a `match` may have one arm
  yielding `u32` and another ending in `continue`: the overall type is `u32`.
- Expressions with the never type named by the source: `continue`, `panic!` and a `loop` that never ends (a
  `loop` containing `break` does not qualify, since it terminates).
- `Option::unwrap` type-checks the same way: `Some(val) => val` is `T`, `None => panic!(...)` is `!`.

### DSTs and `Sized` (§20.3)

- Rust must know how much memory a value of a type needs, and all values of a type use the same amount,
  so you cannot create a variable of, or take an argument of, type `str`.
- Golden rule: values of dynamically sized types must always sit behind a pointer of some kind.
- `&T` is one value (an address); `&str` is two (address and length), so its size is known at compile
  time: twice the length of a `usize`. DSTs in general carry extra metadata storing the dynamic size.
- `str` works with any pointer: `&str`, `Box<str>`, `Rc<str>`. Traits likewise: `&dyn Trait`,
  `Box<dyn Trait>`, `Rc<dyn Trait>`.
- `Sized` is automatically implemented for everything whose size is known at compile time.
- Every generic function gets an implicit bound: `fn generic<T>(t: T)` is treated as
  `fn generic<T: Sized>(t: T)`.
- `fn generic<T: ?Sized>(t: &T)` relaxes it: "`T` may or may not be `Sized`". The `?Trait` syntax exists
  only for `Sized`. The parameter must then be behind a pointer (here `&T`).

### Function pointers (§20.4)

- Functions coerce to the type `fn`. Parameter syntax: `f: fn(i32) -> i32`.
- `fn` is a type, not a trait: use it directly as the parameter type, with no generic parameter or
  trait bound.
- Function pointers implement all three closure traits (`Fn`, `FnMut`, `FnOnce`), so a function pointer
  can always be passed where a closure is expected.
- Each enum variant name is also an initializer function, usable as a function pointer that implements
  the closure traits: `(0u32..20).map(Status::Value)`.
- A named function and the equivalent closure compile to the same code.

### Returning closures (§20.4)

- Closures are represented by traits, so they cannot be returned directly, and they have no returnable
  concrete type. `fn` cannot be the return type if the closure captures values from its scope.
- Normal solution: `impl Trait`, with any of `Fn`, `FnOnce`, `FnMut`.
- Each closure is its own distinct type, and each `impl Trait` return yields a distinct opaque type,
  even for identical trait signatures. To handle several closures uniformly (e.g. in one `Vec`), return
  a trait object: `Box<dyn Fn(i32) -> i32>`.

## Syntax and API Reference

```rust
impl Iterator for Counter { type Item = u32; fn next(&mut self) -> Option<Self::Item> { /* .. */ } }
impl Add<Meters> for Millimeters {
    type Output = Millimeters;
    fn add(self, other: Meters) -> Millimeters { Millimeters(self.0 + (other.0 * 1000)) }
}
println!("{}", <Dog as Animal>::baby_name());     // fully qualified
type Thunk = Box<dyn Fn() + Send + 'static>;       // alias for a long type
fn do_twice(f: fn(i32) -> i32, arg: i32) -> i32 { f(arg) + f(arg) }
fn returns_closure() -> impl Fn(i32) -> i32 { |x| x + 1 }
fn returns_initialized_closure(init: i32) -> Box<dyn Fn(i32) -> i32> { Box::new(move |x| x + init) }
let strs: Vec<String> = nums.iter().map(ToString::to_string).collect();
```

| Form | Meaning |
|---|---|
| `type Item;` in a trait / `type Item = u32;` in an impl | Declare / set an associated type |
| `trait Add<Rhs=Self>` | Default type parameter |
| `Trait::method(&value)` | Pick a trait's method when names collide |
| `<Type as Trait>::function(...)` | Fully qualified call |
| `trait A: B` | `B` is a supertrait of `A` |
| `struct Wrapper(Vec<String>);` | Newtype; inner value is `self.0` |
| `fn bar() -> !` | Diverging function |
| `T: ?Sized` | Opt out of the implicit `Sized` bound |
| `fn(i32) -> i32` | Function pointer type |

## Decision Rules

- Associated type when a type should implement the trait exactly once and callers shouldn't annotate;
  generic trait parameter when multiple implementations per type are wanted (§20.2).
- Default type parameters serve two purposes: extending a type/trait without breaking existing code (add
  a parameter with a default), and allowing customization most users won't need (like `Add`'s `Rhs`).
- Newtype when you need compile-time distinction, units, encapsulation, or an external trait on an
  external type; type alias when you only want to cut repetition and accept no extra type checking.
- Wrapper needing the full inner API: implement `Deref`; restricted API: hand-write delegating methods.
- Accepting callables: prefer a generic type bounded by a closure trait so both functions and closures
  work. Accept only `fn` when interfacing with external code lacking closures (C functions can take
  functions as arguments, but C has no closures) (§20.4).
- Closure vs named function (or enum initializer) as an argument: same compiled code; pick the clearer.
- Return `impl Fn...` for a single closure type; return `Box<dyn Fn...>` when different closures must
  share one type.

## Pitfalls and Compiler Errors

- **E0790** "cannot call associated function on trait without specifying the corresponding `impl` type":
  `Animal::baby_name()` with no `self` to infer from. Fix: `<Dog as Animal>::baby_name()`.
- Calling `Dog::baby_name()` compiles but silently picks the inherent function (prints `Spot`, not
  `puppy`); likewise `person.fly()` picks the inherent method.
- **E0277** "`Point` doesn't implement `std::fmt::Display`" (unsatisfied trait bound):
  `impl OutlinePrint for Point {}` without the supertrait. Fix: `impl fmt::Display for Point`.
- **E0308** mismatched types, "expected opaque type, found a different opaque type", note "distinct
  uses of `impl Trait` result in different opaque types": putting results of two `impl Fn(i32) -> i32`
  functions in one `vec!` call. Fix: make both return `Box<dyn Fn(i32) -> i32>`.
- `match` arms of different value types (e.g. `5` and `"hello"`) do not compile; only `!`-typed arms
  may differ.
- `let s1: str = "Hello there!";` does not compile (needs 12 bytes vs 15 for another string: no single
  size). Fix: use `&str`.
- `map(ToString::to_string)` needs the trait-qualified path because several functions are named
  `to_string`.
- Type aliases give no protection against mixing up `Kilometers` and `i32`.

## Idioms and Best Practices

- Give associated types names describing their use, and document them in the API docs (§20.2).
- Choose meaningful alias names to convey intent: `Thunk` suits a stored closure, since a thunk is code
  to be evaluated later (§20.3).
- Follow the `std::io` pattern: a module-level `Result<T>` alias fixing the error type gives a
  consistent interface and shorter signatures.
- Use newtypes to encode units in parameter types so wrong-unit calls fail to compile.

## Details Worth Knowing

- Associated types are used less than most book features but more than the rest of this chapter (§20.2).
- `ToString::to_string` is implemented by the standard library for any type implementing `Display`.
- `fmt` signature used for `Display`: `fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result`, with
  `write!(f, ...)` as the body.
- Distinct opaque types for same-signature closures parallels distinct concrete types for async blocks
  with the same output type (ch. 17).
- Cross-references: traits ch. 10, tuple structs ch. 5, `Deref` ch. 15, trait objects and encapsulation
  ch. 18, closure type inference ch. 13, enum initializers ch. 6.
