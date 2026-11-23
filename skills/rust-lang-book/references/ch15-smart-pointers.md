# Ch 15 - Smart Pointers

Source: The Rust Programming Language ch. 15 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- Pointer: a variable holding a memory address that refers to other data. A reference (`&`) is the
  most common kind: it only borrows, has no special capabilities and no overhead (§15.0).
- Smart pointer: a data structure that acts like a pointer but carries extra metadata and
  capabilities. Usually a struct that implements `Deref` (behave like a reference) and `Drop` (custom
  code when the value goes out of scope). In many cases it OWNS the data it points to (§15.0).
- The pattern is general: many libraries define their own smart pointers, and you can write yours.
  The chapter covers the most common std ones: `Box<T>`, `Rc<T>`, and `Ref<T>`/`RefMut<T>` reached
  through `RefCell<T>` (§15.0).
- Indirection: storing a pointer to a value instead of the value itself. A pointer has a fixed size
  regardless of how much data it points to (§15.1).
- Deref coercion: automatic conversion of a reference to a `Deref` type into a reference to another
  type, applied to function and method arguments (§15.2).
- Interior mutability: a design pattern that lets you mutate data through an immutable reference. The
  type uses `unsafe` code internally, wrapped in a safe API; the outer value stays immutable (§15.5).
- Strong vs weak references: strong references (`Rc<T>`) share ownership; weak references
  (`Weak<T>`) express no ownership and do not keep the value alive (§15.6).
- Memory leaks are memory safe in Rust: preventing them entirely is not one of its guarantees (§15.6).

## Rules and Semantics

### `Box<T>` (§15.1)

- Stores its data on the heap; the pointer stays on the stack. No performance overhead beyond the heap
  storage, and no extra capabilities beyond indirection and heap allocation.
- When a box goes out of scope, both the box (stack) and the data it points to (heap) are deallocated.
- Rust must know a type's size at compile time. For an enum it uses the space of the largest variant.
  A variant that directly holds its own type has infinite size; holding a `Box` of it breaks the chain
  because the box's size is known.
- `Box<T>` is a smart pointer because it implements `Deref` and `Drop`.

### `Deref` and the `*` operator (§15.2)

- Without `Deref`, the compiler can only dereference `&` references.
- `Deref` requires one method, `deref`, which borrows `self` and returns a reference to the inner
  data, plus the associated type `Target`.
- `*y` on a `Deref` type is rewritten to `*(y.deref())`. The substitution happens exactly once per `*`
  written; it does not recurse.
- `deref` returns a reference (not the value) so the inner value is not moved out of `self`.
- `*` on a `Box<T>` works the same as on a reference. A box made from a `Copy` value points to a
  copied value, not to the original variable.
- Deref coercion applies only to types implementing `Deref`, and only when the argument's reference
  type does not match the parameter type. Rust inserts as many `Deref::deref` calls as needed; this is
  resolved at compile time, so there is no runtime penalty.
- `DerefMut` overrides `*` on mutable references.
- Coercion cases:
  1. `&T` to `&U` when `T: Deref<Target=U>`
  2. `&mut T` to `&mut U` when `T: DerefMut<Target=U>`
  3. `&mut T` to `&U` when `T: Deref<Target=U>`
- Immutable references never coerce to mutable ones: a mutable reference is guaranteed unique, so
  downgrading is always safe, but the borrowing rules cannot guarantee an immutable one is unique.

### `Drop` (§15.3)

- `Drop` requires one method, `drop`, taking `&mut self`. It runs automatically when the value goes
  out of scope; the compiler inserts the call. `Drop` is in the prelude.
- Variables are dropped in reverse order of creation.
- The `Drop::drop` method cannot be called explicitly, and the automatic call cannot be disabled;
  an explicit call would lead to a double free since Rust would still drop at end of scope.
- To drop early, pass the value to `std::mem::drop` (in the prelude as `drop`), which is a different
  thing from the trait method.
- Ownership guarantees `drop` runs only once, when the value is no longer in use.

### `Rc<T>` (§15.4)

- Enables multiple owners by counting references; the value is cleaned up only at zero references.
- Single-threaded only. Not in the prelude: `use std::rc::Rc;`.
- `Rc::clone(&a)` only increments the count, no deep copy. The count starts at 1.
- `Drop` for `Rc<T>` decrements the count automatically when an `Rc<T>` goes out of scope.
- Gives shared access for reading only (immutable references); allowing multiple mutable references
  would break the borrowing rules.

### `RefCell<T>` (§15.5)

- Single ownership, like `Box<T>`, but the borrowing rules (one mutable XOR any number of immutable
  references; references always valid) are enforced at runtime. Violations panic rather than fail to
  compile.
- `borrow` returns `Ref<T>`, `borrow_mut` returns `RefMut<T>`; both implement `Deref`. `RefCell<T>`
  counts active `Ref<T>` and `RefMut<T>` values; a count drops when the smart pointer goes out of scope.
- Single-threaded only: using it in a multithreaded context is a compile-time error.
- Costs: mistakes surface later (possibly in production) and there is a small runtime penalty for
  tracking borrows.
- `Rc<RefCell<T>>` yields a value with multiple owners that can also be mutated.

### Reference cycles and `Weak<T>` (§15.6)

- With `Rc<T>` plus `RefCell<T>`, items can refer to each other in a cycle. Their strong counts never
  reach 0, so the values are never dropped: a leak. Rust does not catch this; it is a logic bug.
- `Rc::downgrade(&rc)` returns a `Weak<T>` and increments `weak_count` instead of `strong_count`.
- An `Rc<T>` is cleaned up when `strong_count` is 0; `weak_count` need not be 0.
- `weak.upgrade()` returns `Option<Rc<T>>`: `Some` if the value still exists, `None` if dropped, so
  both cases must be handled and no invalid pointer can result.
- A cycle that includes weak references is broken once the strong counts involved reach 0.

## Syntax and API Reference

```rust
let b = Box::new(5);                                  // §15.1
enum List { Cons(i32, Box<List>), Nil }               // recursive type via indirection

use std::ops::Deref;                                  // §15.2
struct MyBox<T>(T);
impl<T> Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &Self::Target { &self.0 }
}
hello(&m);            // &MyBox<String> -> &String -> &str by deref coercion
hello(&(*m)[..]);     // what it would take without coercion

impl Drop for CustomSmartPointer {                    // §15.3
    fn drop(&mut self) { /* cleanup */ }
}
drop(c);              // std::mem::drop: force early cleanup
```

| API | Meaning | Ref |
|---|---|---|
| `Rc::new(v)` | new reference-counted value | §15.4 |
| `Rc::clone(&a)` | another owner; increments the strong count | §15.4 |
| `Rc::strong_count(&a)` | number of strong references | §15.4 |
| `Rc::weak_count(&a)` | number of `Weak<T>` references | §15.6 |
| `Rc::downgrade(&a)` | create a `Weak<T>` | §15.6 |
| `Weak::new()` | empty weak reference; `upgrade` gives `None` | §15.6 |
| `weak.upgrade()` | `Option<Rc<T>>` | §15.6 |
| `RefCell::new(v)` | wrap a value for runtime-checked borrows (`use std::cell::RefCell;`) | §15.5 |
| `cell.borrow()` | `Ref<T>`, immutable access | §15.5 |
| `cell.borrow_mut()` | `RefMut<T>`, mutable access | §15.5 |

```rust
self.sent_messages.borrow_mut().push(String::from(message));   // mutate through &self (§15.5)
*value.borrow_mut() += 10;                                     // value: Rc<RefCell<i32>>

use std::rc::{Rc, Weak};                                       // §15.6
struct Node {
    value: i32,
    parent: RefCell<Weak<Node>>,       // child does not own parent
    children: RefCell<Vec<Rc<Node>>>,  // parent owns children
}
*leaf.parent.borrow_mut() = Rc::downgrade(&branch);
leaf.parent.borrow().upgrade()         // Option<Rc<Node>>
```

## Decision Rules

- Use `Box<T>` when (§15.1): a type's size is unknown at compile time but a sized context needs it
  (recursive types); a large value should change owners without being copied (only the pointer is
  copied); or you want to own a value caring only that it implements a trait (trait object, Ch 18).
- Keep single values such as an `i32` on the stack; boxing one alone is rarely useful (§15.1).
- Prefer `Vec<T>` over a cons list for a list of items in most cases (§15.1).
- Use `Rc<T>` when heap data is read by several parts of the program and it cannot be determined at
  compile time which part finishes last. If that is known, make that part the owner (§15.4).
- Use `RefCell<T>` when you are sure the code follows the borrowing rules but the compiler cannot
  verify it. Compile-time checking is the default and the best choice in most cases (§15.5).
- Recap from the book (§15.5):

| Type | Owners | Borrows allowed | Checked |
|---|---|---|---|
| `Box<T>` | single | immutable or mutable | compile time |
| `Rc<T>` | multiple | immutable only | compile time |
| `RefCell<T>` | single | immutable or mutable | runtime |

- Combine as `Rc<RefCell<T>>` for shared ownership plus mutation (§15.5).
- In multithreaded code use neither `Rc<T>` nor `RefCell<T>`; `Mutex<T>` is the thread-safe version of
  `RefCell<T>` and multithreaded reference counting is covered in Chapter 16 (§15.4, §15.5).
- Model ownership direction in data structures: a parent owns its children (`Rc<T>`), a child refers
  to its parent without owning it (`Weak<T>`). Dropping the parent drops the children; dropping a
  child leaves the parent (§15.6).
- Holding references in a recursive type instead of `Rc<T>` would need lifetime parameters and would
  require every element to live at least as long as the whole list, which is not always true (§15.4).

## Pitfalls and Compiler Errors

- E0072 `recursive type `List` has infinite size` (§15.1): `Cons(i32, List)`. Fix, per the compiler
  help ("insert some indirection (e.g., a `Box`, `Rc`, or `&`)"): `Cons(i32, Box<List>)`.
- E0277 `can't compare `{integer}` with `&{integer}`` (§15.2): `assert_eq!(5, y)` with `y = &x`. A
  number and a reference to one are different types; write `*y`.
- E0614 `type `MyBox<{integer}>` cannot be dereferenced` (§15.2): `*y` on a type without `Deref`.
  Fix: implement `Deref`.
- E0040 `explicit use of destructor method` (§15.3): calling `c.drop()`. Fix: `drop(c)`.
- E0382 `use of moved value: `a`` (§15.4): `Box::new(a)` used for two lists; the first moves `a`.
  Fix: hold `Rc<List>` and use `Rc::clone(&a)` for each sharer.
- E0596 `cannot borrow `x` as mutable, as it is not declared as mutable` (§15.5): `&mut x` on an
  immutable binding.
- E0596 `cannot borrow `self.sent_messages` as mutable, as it is behind a `&` reference` (§15.5):
  pushing to a field inside a `&self` method. The compiler suggests `&mut self` in the trait and impl;
  the book rejects changing the trait just for a test and wraps the field in `RefCell<Vec<String>>`,
  using `borrow_mut()` to push and `borrow()` to read.
- Runtime panic from two active `borrow_mut()` results in one scope (§15.5): compiles, then panics.
  The book's prose quotes the message as `already borrowed: BorrowMutError`; the captured test output
  in the repo reads `RefCell already borrowed`.
- Reference cycle (§15.6): `a` and `b` each end with strong count 2; dropping the variables leaves
  both at 1, so the memory is never freed. Printing such a cycle with `{:?}` overflows the stack.
- An `Rc<T>` parent field in a child would create a cycle with the parent's children list (§15.6).

## Idioms and Best Practices

- Write `Rc::clone(&a)` rather than `a.clone()`. Both work, but the convention visually separates
  cheap count increments from deep-copy clones, so performance reviews can ignore `Rc::clone` (§15.4).
- Put cleanup (files, network connections, locks) in `Drop` so it cannot be forgotten (§15.3).
- Use `drop(value)` to release early, e.g. a lock-managing smart pointer, so other code in the same
  scope can acquire the lock (§15.3).
- Rely on deref coercion instead of spelling out `&` and `*` chains; it lets the same code serve
  references and smart pointers (§15.2).
- Mock objects: a test double that records what happened so the test can assert on it. Implement the
  production trait on a test-only struct and use `RefCell<T>` for the recording field when the trait
  method takes `&self` (§15.5).
- Do not change a trait's signature solely to make a test compile (§15.5).
- Guard against cycles with automated tests, code review and similar practices; wherever `RefCell<T>`
  contains `Rc<T>` (or similar nesting) you must ensure no cycle is created (§15.6).
- Reorganise data so some references express ownership and others do not; only ownership relations
  affect whether a value can be dropped (§15.6).

## Details Worth Knowing

- The real `Box<T>` is ultimately a tuple struct with one element; the book's `MyBox<T>` mirrors that
  but does not store data on the heap (§15.2).
- `String` implements `Deref` returning a string slice, which is why `&String` coerces to `&str`
  (§15.2).
- The dereference operator `*` is distinct from the multiplication and glob operators (§15.2).
- "Destructor" is the general term for a function that cleans up an instance; Rust's `drop` is one
  (§15.3).
- `Drop` could even be used to build your own memory allocator (§15.3).
- The function is `strong_count`, not `count`, because `Rc<T>` also has a `weak_count` (§15.4).
- Example counts (§15.4): 1 after creating `a`, 2 after `b`, 3 after `c`, back to 2 when `c` leaves
  its inner scope.
- Example counts (§15.6): `leaf` strong 1 / weak 0; inside the scope `branch` strong 1 / weak 1 and
  `leaf` strong 2 / weak 0; after `branch` is dropped `leaf.parent.borrow().upgrade()` is `None` and
  `leaf` is strong 1 / weak 0.
- Debug output shows a weak reference as `(Weak)` and a cell as `RefCell { value: ... }` (§15.5, §15.6).
- Calling `borrow_mut` on an `Rc<RefCell<T>>` uses automatic dereferencing through the `Rc<T>`
  (see "Where's the `->` Operator?" in Chapter 5) (§15.5).
- Static analysis is inherently conservative: the compiler may reject a correct program rather than
  ever accept an incorrect one; `RefCell<T>` covers some of those rejected-but-safe cases (§15.5).
- `Nil` in a cons list is the base case of the recursion, not the "null" concept from Chapter 6
  (§15.1).
- Forward references: trait objects in Chapter 18; associated types and `unsafe` in Chapter 20;
  concurrency-safe counterparts in Chapter 16; "The Rustonomicon" for writing your own smart pointers
  (§15.1, §15.2, §15.5, §15.6).
