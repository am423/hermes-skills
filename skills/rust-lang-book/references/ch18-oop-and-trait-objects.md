# Ch 18 - Object-Oriented Programming Features

Source: The Rust Programming Language ch. 18 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- No consensus definition of OOP; by some definitions Rust is OO, by others not. The chapter tests three
  commonly cited characteristics: objects, encapsulation, inheritance (§18.0, §18.1).
- **Objects = data + behavior** (Gang of Four definition): Rust qualifies. Structs and enums hold data; `impl`
  blocks supply methods. They just are not *called* objects (§18.1).
- **Encapsulation**: Rust qualifies. Everything is private by default; `pub` opts modules, types, functions,
  methods in. Only the public API can touch internals, so internals can be refactored freely (§18.1).
- **Inheritance**: Rust does NOT have it. A struct cannot inherit a parent struct's fields and method
  implementations "without using a macro" (§18.1).
- The two reasons people reach for inheritance, and Rust's substitute for each (§18.1):
  - Code reuse -> default trait method implementations (limited form; overridable per implementing type, like
    a child class overriding a parent method).
  - Polymorphism (child usable where parent is expected) -> generics + trait bounds ("bounded parametric
    polymorphism") at compile time, or trait objects at runtime.
- **Polymorphism** is broader than inheritance: code that works with data of multiple types (§18.1).
- **Trait object**: points to (a) an instance of a type implementing the trait and (b) a table used to look up
  that type's trait methods at runtime. Written as some pointer + `dyn` + trait, e.g. `Box<dyn Draw>` or a
  reference (§18.2).
- Trait objects differ from other languages' objects: you cannot add data to a trait object. Their specific
  purpose is abstraction over common behavior; they are less generally useful than classic objects (§18.2).
- **Static dispatch**: compiler knows the callee at compile time (result of monomorphizing generics).
  **Dynamic dispatch**: compiler cannot tell; it emits code that picks the method at runtime. Trait objects
  always use dynamic dispatch (§18.2).
- **State pattern**: a value holds one of a set of state objects; behavior changes with the state; each state
  object owns its own behavior and decides when to transition. The holder knows nothing about either (§18.3).

## Rules and Semantics

### Encapsulation (§18.1)
- A `pub struct` with private fields forces all access through its public methods; this is how an invariant
  between fields is kept (example: a cached `average` kept in sync with a `list`).
- Private helper methods (no `pub`) are callable only from inside; public methods call them to maintain the
  invariant.
- A read-only getter (`pub fn average(&self) -> f64`) exposes a value without allowing modification.
- As long as public method signatures stay the same, the internal data structure can change (e.g. `Vec<i32>`
  to `HashSet<i32>`) without breaking callers. Public fields would leak the structure's own methods.

### Trait objects (§18.2)
- A trait object must sit behind a pointer (reference or `Box<T>` smart pointer); the reason is covered under
  dynamically sized types and the `Sized` trait in ch. 20.
- A trait object can be used in place of a generic or concrete type. The compiler guarantees at compile time
  that every value used there implements the trait, so the full set of types need not be known up front.
- `Vec<Box<dyn Draw>>` holds mixed concrete types (a `Box<Button>` and a `Box<TextField>` in one vector).
- Generic alternative `struct Screen<T: Draw> { components: Vec<T> }`: one `T` is substituted with exactly one
  concrete type at a time, so the collection is homogeneous (all `Button` or all `TextField`).
- A value becomes a trait object by putting it in a `Box<T>` where a `Box<dyn Trait>` is expected; the
  compiler performs the cast from `Box<Concrete>` to `Box<dyn Trait>` (wording from the E0277 note).
- Downstream crates can implement the trait on their own types (`impl Draw for SelectBox`) and pass them to
  library code written before those types existed.
- Types implementing the trait may have unrelated fields and extra `impl` blocks with methods that do not
  apply to other implementors.

### Dynamic dispatch (§18.2)
- At runtime Rust follows the pointers inside the trait object to find the method to call.
- Costs: a runtime lookup that static dispatch does not have; the compiler cannot inline the method, which
  blocks some optimizations.
- **dyn compatibility**: the name of the rules on where dynamic dispatch can and cannot be used. Details are
  deferred to the Rust Reference (traits, "dyn compatibility").
- One dyn-compatibility consequence stated in the chapter: a default trait method returning `self` does not
  work when the trait is used as a trait object, because the concrete `self` type (hence the return type) is
  unknown at compile time (§18.3).

### State pattern with trait objects (§18.3)
- Holder: `state: Option<Box<dyn State>>` in a private field; private `State` trait; one struct per state
  (`Draft`, `PendingReview`, `Published`).
- Because `state` is private and `new` always builds `Draft`, no `Post` can be created in any other state.
- Transition methods take `self: Box<Self>`: valid only when called on a `Box` holding the type; takes
  ownership of the box, invalidating the old state, and returns the new `Box<dyn State>`.
- Why `Option`: Rust does not allow unpopulated struct fields, so `take()` moves the `Some` value out and
  leaves `None`, giving ownership rather than a borrow. Writing
  `self.state = self.state.request_review();` directly cannot obtain ownership.
- A no-op transition returns `self` (e.g. `approve` on `Draft`, `request_review` on `PendingReview`).
- Reading through the state: `self.state.as_ref().unwrap().content(self)`.
  - `as_ref` turns `Option<Box<dyn State>>` into `Option<&Box<dyn State>>`; without it there is an error
    because `state` cannot be moved out of the borrowed `&self`.
  - `unwrap` is acceptable here: the methods guarantee `state` is `Some` once they finish (a "more
    information than the compiler" case from ch. 9).
  - Deref coercion applies through the `&` and the `Box`, so the call lands on the concrete state type.
- A trait method returning a reference into an argument needs lifetime annotations:
  `fn content<'a>(&self, post: &'a Post) -> &'a str`.
- A default `content` returning `""` means only `Published` overrides it.

### States as types (§18.3)
- Each state is its own struct (`DraftPost`, `PendingReviewPost`, `Post`); no `state` field.
- Methods exist only where valid: `DraftPost` and `PendingReviewPost` have no `content` method, so reading
  unpublished content is a compile error, not a runtime empty string.
- Transitions take `self` by value and return the next type, consuming the old instance so none lingers.
- `Post::new` returns `DraftPost`; with a private `content` field and no other constructor, the only route to
  a `Post` is `request_review` then `approve`. The workflow is encoded in the type system.
- Callers must rebind: `let post = post.request_review();` (shadowing), since nothing is mutated in place.

## Syntax and API Reference

```rust
pub trait Draw { fn draw(&self); }
pub struct Screen { pub components: Vec<Box<dyn Draw>> }   // trait-object collection
for component in self.components.iter() { component.draw(); } // dynamic dispatch

pub struct Screen<T: Draw> { pub components: Vec<T> }      // generic, homogeneous
impl<T> Screen<T> where T: Draw { pub fn run(&self) { /* ... */ } }

trait State {
    fn request_review(self: Box<Self>) -> Box<dyn State>;
    fn approve(self: Box<Self>) -> Box<dyn State>;
    fn content<'a>(&self, post: &'a Post) -> &'a str { "" }
}
pub fn request_review(&mut self) {                         // on the holder
    if let Some(s) = self.state.take() { self.state = Some(s.request_review()) }
}
```

| Item | Meaning as used in this chapter |
|---|---|
| `dyn Trait` behind `Box<...>` or a reference | trait object type |
| `self: Box<Self>` | receiver usable only on a `Box` of the type; takes ownership of the box |
| `Option::take` | moves the `Some` value out, leaves `None` in the field |
| `Option::as_ref` | `Option<T>` behind `&self` -> `Option<&T>`, no move |
| `unwrap` | used where `None` is known impossible |
| `Box::new(Draft {})` | builds a boxed state object; coerces to `Box<dyn State>` |

## Decision Rules

- Fixed set of interchangeable types known at compile time -> an enum is "a perfectly good solution"
  (the `SpreadsheetCell` approach from ch. 8) (§18.2).
- Users of your library must be able to add new types -> trait objects (§18.2).
- Only ever homogeneous collections -> prefer generics with trait bounds: monomorphized, static dispatch
  (§18.2).
- Heterogeneous collections, or types unknown when the library is written -> `Vec<Box<dyn Trait>>`, accepting
  the lookup cost and lost inlining in exchange for flexibility (§18.2).
- Want code reuse without inheritance -> default trait method implementations (§18.1).
- State handling, three options compared (§18.3):
  - Trait-object state pattern: rules live inside each state; holder methods and callers need no `match`;
    adding a state means one new struct plus its trait impl. Invalid operations are silent no-ops at runtime.
  - Enum of states: possible, but every place that inspects the state needs a `match` (or similar) covering
    every variant, which can get more repetitive.
  - States as types: invalid states and transitions become compile errors; transitions are no longer fully
    encapsulated (callers rebind), so it is not strictly the OO state pattern.
- OO patterns are available in Rust but "won't always be the best solution" because of features such as
  ownership that OO languages lack; rethinking the design to use Rust's strengths can catch bugs at compile
  time (§18.3).

## Pitfalls and Compiler Errors

- **E0277** `the trait bound `String: Draw` is not satisfied`: a `Box::new(String::from("Hi"))` placed in a
  `Vec<Box<dyn Draw>>`. The note reads "required for the cast from `Box<String>` to `Box<dyn Draw>`". Fix:
  pass a type that implements the trait, or implement the trait for that type (§18.2).
- Moving out of a borrowed field: reading the `Option` field through `&self` without `as_ref` is an error
  because `state` cannot be moved out of the borrowed `&self` (§18.3).
- Default implementations of `request_review` / `approve` that return `self` to remove duplication do not
  work with a trait object: a dyn-compatibility rule (§18.3).
- Downsides of the trait-object state pattern (§18.3):
  - States are coupled: inserting a state such as `Scheduled` between `PendingReview` and `Published`
    requires editing `PendingReview`.
  - Duplicated logic: near-identical no-op transition methods in each state, and near-identical
    `Option::take` delegating methods on the holder.
  - Letting `State::content` decide the post's content blurs the responsibilities of `State` and `Post`.
- Inheritance trade-offs Rust avoids: sharing more code than needed, subclasses inheriting methods that make
  no sense or cause errors for them, single-inheritance restrictions (§18.1).
- Thinking trait objects are free: the dispatch lookup and the loss of inlining are real costs (§18.2).

## Idioms and Best Practices

- Keep fields private and expose behavior through methods so invariants hold and internals can change (§18.1).
- Implement an accessor method rather than making a field `pub` when you may later want to control how the
  data is read (`add_text` / `content` on `Post`) (§18.3).
- Keep state-independent behavior out of the state objects (`add_text` does not touch `state`) (§18.3).
- Duck-typing style with compile-time safety: code cares only that a value responds to `draw`, never checks
  the concrete type, and never needs a runtime check that the method exists (§18.2).
- Many repeated delegating methods on a holder -> consider a macro (ch. 20 "Macros") (§18.3).
- Prefer encoding states and transitions in types when you want invalid states to be impossible (§18.3).
- An assertion such as "a draft returns an empty string from `content`" makes an excellent unit test (§18.3).

## Details Worth Knowing

- History: objects came from Simula in the 1960s; Alan Kay coined "object-oriented programming" in 1967
  (§18.0).
- The text uses the term **dyn compatibility** for the rules on trait-object use (§18.2).
- Rust avoids calling structs and enums "objects" because data (fields) and behavior (`impl` blocks) are
  separate, unlike the combined concept in other languages (§18.2).
- Suggested extensions to the state-pattern `blog` crate: a `reject` method (`PendingReview` -> `Draft`);
  requiring two `approve` calls before `Published`; allowing `add_text` only in `Draft` (hint: the state
  decides what may change but does not itself modify the `Post`) (§18.3).
- Forward references: `Sized` and dynamically sized types (ch. 20); macros (ch. 20); patterns (ch. 19).
- Back references: `pub` and privacy (ch. 7); enum-in-vector workaround (ch. 8); `unwrap` when you know more
  than the compiler (ch. 9); default trait methods, lifetimes, monomorphization (ch. 10).
