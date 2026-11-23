# Ch 10 - Generic Types, Traits, and Lifetimes

Source: The Rust Programming Language ch. 10 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- Generics: abstract stand-ins for concrete types or other properties; code states how they behave and
  relate without knowing what will fill them in (§10.0). Three tools, all checked at compile time:
  - Generic type parameters: apply the same code to different types.
  - Traits and trait bounds: guarantee a generic type has the behaviour the code needs.
  - Lifetimes: a kind of generic describing how references relate, so no reference dangles.
- Trait: defines functionality a type has and can share with other types; a group of method signatures
  for some purpose. Similar to interfaces in other languages, with some differences (§10.2).
- A type's behaviour = the methods callable on it; types share behaviour when the same methods can be
  called on all of them (§10.2).
- Monomorphization: at compile time the compiler finds every concrete type that generic code is used
  with and generates specific code for each. Zero runtime cost versus hand-duplicated code (§10.1).
- Every reference has a lifetime: the scope for which it is valid. Usually implicit and inferred, like
  types; annotation is required only when the lifetimes could relate in more than one way (§10.3).
- Lifetime annotations never change how long anything lives. They describe relationships between the
  lifetimes of several references; the borrow checker rejects callers that violate them (§10.3).
- Borrow checker: compares scopes to decide whether all borrows are valid. A borrow is rejected when the
  referent's lifetime is shorter than the reference's (§10.3).

## Rules and Semantics

### Generic type parameters (§10.1)
- A type parameter must be declared before use: in `<>` between the function name and parameter list;
  just after the struct or enum name; just after `impl` for methods on a generic type.
- `fn largest<T>(list: &[T]) -> &T` reads "`largest` is generic over some type `T`".
- One parameter used for several fields forces them to the same type: `Point<T> { x: T, y: T }` rejects
  `Point { x: 5, y: 4.0 }`. Use `Point<T, U>` to allow different (or equal) types.
- `impl<T> Point<T> { .. }`: declaring `T` after `impl` tells Rust the `T` in `Point<T>` is generic, not
  a concrete type. Such methods exist on every instance whatever type substitutes for `T`. The name may
  differ from the struct definition's, but reusing it is conventional.
- `impl Point<f32> { .. }` (nothing declared after `impl`): methods exist only for that concrete
  instantiation; other `Point<T>` do not have them.
- A method may declare its own generic parameters in addition to the `impl`'s: parameters that belong to
  the struct go after `impl`, those relevant only to the method go after `fn name`.
- A generic body may only use operations valid for every possible `T`; otherwise bound `T` by a trait.

### Traits (§10.2)
- Definition: `trait Name { fn sig(&self) -> Ret; }`. Signature ends in `;` instead of a body; several
  methods are listed one per line. `pub trait` lets dependent crates use it.
- Implementation: `impl Trait for Type { .. }` with a body for each signature. The compiler enforces that
  the method is defined with exactly the trait's signature.
- To call trait methods, the trait must be in scope along with the type:
  `use aggregator::{SocialPost, Summary};`.
- Orphan rule (part of coherence): a trait can be implemented on a type only if the trait or the type,
  or both, is local to your crate. OK: `Display` on your `SocialPost`; your `Summary` on `Vec<T>`.
  Not OK: `Display` on `Vec<T>`. Purpose: two crates cannot implement the same trait for the same type,
  so other people's code cannot break yours and vice versa.
- Default implementations: give the method a body in the trait. `impl Summary for NewsArticle {}` (empty
  block) accepts all defaults. Overriding uses the same syntax as implementing a method with no default.
- A default method may call other methods of the same trait, including ones with no default, so a trait
  can offer much functionality while requiring implementors to write only a small part.
- An overriding implementation cannot call the default implementation of that same method.
- `impl Trait` in parameter position is syntax sugar for a trait bound: `item: &impl Summary` is
  equivalent to `<T: Summary>(item: &T)`.
- `impl Trait` in return position: returns some type implementing the trait without naming it. It must
  be a single concrete type; branches returning different types do not compile.
- Conditional methods: `impl<T: Display + PartialOrd> Pair<T> { .. }` defines the methods only when `T`
  satisfies the bounds.
- Blanket implementation: implementing a trait for every type satisfying a bound, e.g. std's
  `impl<T: Display> ToString for T`. Hence `3.to_string()` works, since integers implement `Display`.

### Lifetimes (§10.3)
- Lifetime parameter names start with an apostrophe, are usually lowercase and very short; `'a` is the
  usual first name. The annotation goes after `&`, separated from the type by a space.
- Declared in `<>` like type parameters, and in the same list: `fn f<'a, T>(..)`.
- A single annotation alone means little; annotations relate several references to each other.
- `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str`: for some `'a`, both arguments live at least as
  long as `'a`, and so does the result. The concrete `'a` is the overlap of the two argument scopes, i.e.
  the smaller of the two lifetimes; the result is valid only that long.
- Annotations belong in the signature, not the body; they are part of the function's contract, like
  types. This keeps compiler analysis simpler and errors pointed at the right place.
- Annotate only the references that are related: a function always returning `x` needs
  `fn longest<'a>(x: &'a str, y: &str) -> &'a str`.
- A returned reference's lifetime parameter must match that of one of the parameters. Otherwise it would
  refer to a value created inside the function, which is a dangling reference; no annotation fixes that.
- Structs holding references need a lifetime annotation on every reference:
  `struct ImportantExcerpt<'a> { part: &'a str }`. An instance cannot outlive the reference it holds.
- Methods: lifetime names for struct fields are always declared after `impl` and used after the struct
  name (`impl<'a> ImportantExcerpt<'a>`), because they are part of the struct's type. References in
  method signatures may be tied to the fields' lifetimes or be independent.
- `'static`: the reference *can* live for the entire program. All string literals are `'static`, since
  their text is stored in the program's binary.

### Lifetime elision rules (§10.3)
Input lifetimes = on function/method parameters; output lifetimes = on return values. The rules apply to
`fn` definitions and `impl` blocks. They are cases the compiler considers, not rules programmers follow.
1. Each parameter that is a reference gets its own lifetime parameter:
   `fn foo<'a, 'b>(x: &'a i32, y: &'b i32)`.
2. If there is exactly one input lifetime, it is assigned to all output lifetimes:
   `fn foo<'a>(x: &'a i32) -> &'a i32`.
3. If there are several input lifetimes and one is `&self` or `&mut self`, the lifetime of `self` is
   assigned to all output lifetimes.
- Rule 1 covers inputs, rules 2 and 3 outputs. If any reference still lacks a lifetime after all three,
  compilation stops with an error; the compiler never guesses.
- Worked: `fn first_word(s: &str) -> &str` resolves via rules 1 + 2. `fn longest(x: &str, y: &str) -> &str`
  gets two input lifetimes; rule 2 fails (more than one), rule 3 fails (no `self`), so it errors.

## Syntax and API Reference

```rust
fn largest<T: PartialOrd>(list: &[T]) -> &T          // bounded generic function (§10.1)
struct Point<T> { x: T, y: T }                       // one type for both fields
struct Point<T, U> { x: T, y: U }                    // independent field types
enum Option<T> { Some(T), None }
enum Result<T, E> { Ok(T), Err(E) }
impl<T> Point<T> { fn x(&self) -> &T { &self.x } }   // all instantiations
impl Point<f32> { fn distance_from_origin(&self) -> f32 { .. } }   // one instantiation
impl<X1, Y1> Point<X1, Y1> {                         // impl-level + method-level generics
    fn mixup<X2, Y2>(self, other: Point<X2, Y2>) -> Point<X1, Y2> { .. }
}
```

```rust
pub trait Summary {                                  // (§10.2)
    fn summarize_author(&self) -> String;            // required
    fn summarize(&self) -> String {                  // default, calls a required method
        format!("(Read more from {}...)", self.summarize_author())
    }
}
impl Summary for SocialPost { fn summarize_author(&self) -> String { .. } }
impl Summary for NewsArticle {}                      // all defaults (when every method has one)

pub fn notify(item: &impl Summary)                   // impl Trait parameter
pub fn notify<T: Summary>(item: &T)                  // equivalent trait bound
pub fn notify(item1: &impl Summary, item2: &impl Summary)   // types may differ
pub fn notify<T: Summary>(item1: &T, item2: &T)      // same concrete type forced
pub fn notify(item: &(impl Summary + Display))       // multiple bounds, impl form
pub fn notify<T: Summary + Display>(item: &T)        // multiple bounds, generic form
fn some_function<T, U>(t: &T, u: &U) -> i32
where
    T: Display + Clone,
    U: Clone + Debug,
{ .. }
fn returns_summarizable() -> impl Summary { .. }     // return position
impl<T: Display + PartialOrd> Pair<T> { fn cmp_display(&self) { .. } }   // conditional methods
impl<T: Display> ToString for T { .. }               // blanket impl (std)
```

```rust
&i32        // a reference                           (§10.3)
&'a i32     // a reference with an explicit lifetime
&'a mut i32 // a mutable reference with an explicit lifetime
let s: &'static str = "I have a static lifetime.";
impl<'a> ImportantExcerpt<'a> {
    fn level(&self) -> i32 { 3 }                                     // rule 1 only
    fn announce_and_return_part(&self, announcement: &str) -> &str { self.part }   // rule 3
}
fn longest_with_an_announcement<'a, T>(x: &'a str, y: &'a str, ann: T) -> &'a str
where
    T: Display,
{ .. }
```

## Decision Rules

- Two functions differing only in parameter types, or several struct/enum definitions differing only in
  the types they hold: merge into one generic definition (§10.0, §10.1).
- Fields that must share a type: one parameter; fields that may differ: one parameter each (§10.1).
- Needing lots of generic type parameters suggests restructuring the code into smaller pieces; more than
  a few makes code hard to read (§10.1).
- `impl Trait` for simple, concise cases; full trait-bound syntax when more must be expressed, notably
  forcing two parameters to be the same type (§10.2).
- Many bounds across several generics: move them to a `where` clause so name, parameter list and return
  type stay close together (§10.2).
- Return `impl Trait` to hide a concrete type; especially useful for closures and iterators, whose types
  only the compiler knows or are very long. Need to return one of several types: trait objects, ch. 18
  (§10.2).
- Function needs to return data it creates itself: return an owned type, not a reference, making the
  caller responsible for cleanup (§10.3).
- Take string slices rather than `String` parameters when the function should not take ownership (§10.3).
- Compiler suggests `'static`: first ask whether the reference really lives for the whole program and
  whether you want it to. Usually the real cause is a dangling reference or a mismatch of available
  lifetimes; fix that instead (§10.3).

## Pitfalls and Compiler Errors

- E0369 "binary operation `>` cannot be applied to type `&T`": comparing values of an unbounded `T`. Fix
  per help text: `fn largest<T: std::cmp::PartialOrd>(list: &[T]) -> &T` (§10.1).
- E0308 "mismatched types ... expected integer, found floating-point number": `Point { x: 5, y: 4.0 }`
  with `Point<T>`; the first field fixes `T`. Fix: `Point<T, U>` (§10.1).
- E0597 "`x` does not live long enough": `r = &x;` in an inner scope, `r` used after it ends. Fix: make
  the data outlive the reference (declare `x` in the outer scope) (§10.3).
- E0106 "missing lifetime specifier ... expected named lifetime parameter": `fn longest(x: &str, y: &str)
  -> &str`; the signature does not say whether the result borrows from `x` or `y`. Fix:
  `fn longest<'a>(x: &'a str, y: &'a str) -> &'a str` (§10.3).
- E0597 "`string2` does not live long enough": `result = longest(string1.as_str(), string2.as_str())`
  used after `string2`'s scope. Rejected even though `string1` is actually the longer one; the signature
  promises only the smaller lifetime (§10.3).
- E0515 "cannot return value referencing local variable `result`": returning `result.as_str()` of a local
  `String`. An unrelated `'a` on the return type does not help. Fix: return an owned value (§10.3).
- `impl Summary` return with `if`/`else` yielding `NewsArticle` vs `SocialPost` does not compile (§10.2).
- Passing a type that lacks the trait (e.g. `String` or `i32` to `notify`) does not compile (§10.2).
- Implementing an external trait on an external type violates the orphan rule (§10.2).

## Idioms and Best Practices

- Type parameter names: short, often one letter, UpperCamelCase; `T` (for "type") is the default (§10.1).
- Duplication removal recipe: identify duplicate code; extract it into a function body with inputs and
  return values in the signature; replace the duplicates with calls. Generics apply the same steps to
  types (§10.0).
- `Self` is an alias for the type of the `impl` block: `fn new(x: T, y: T) -> Self { Self { x, y } }`
  (§10.2).
- Design traits with a small required core and defaults built on it (§10.2).
- Trait bounds move "method not defined" errors from runtime to compile time and remove the need for
  runtime behaviour checks, improving performance without losing generic flexibility (§10.2).

## Details Worth Knowing

- Monomorphized `Some(5)` and `Some(5.0)` yield two specialised definitions, illustrated as `Option_i32`
  and `Option_f64`; the compiler's real names differ (§10.1).
- std implements `PartialOrd` on both `i32` and `char`; see Appendix C for the trait (§10.1).
- `distance_from_origin` uses `powi(2)` and `sqrt()`, operations available only on floats (§10.1).
- Blanket implementations are listed in a trait's docs under "Implementors" (§10.2).
- `let r;` without an initial value is allowed; using it before assignment is a compile-time error, so
  this is not a null value (§10.3).
- Elision is historical: pre-1.0 Rust required explicit lifetimes on every reference, e.g.
  `fn first_word<'a>(s: &'a str) -> &'a str`. More patterns may be added, so fewer annotations might be
  needed in future (§10.3).
- The book's examples use the names `SocialPost` and `repost` for the aggregator types (§10.2).
- Forward references: closures and iterators (ch. 13); trait objects (ch. 18); advanced lifetime
  scenarios are in the Rust Reference (§10.3).
