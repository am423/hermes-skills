# Ch 4 - Understanding Ownership

Source: The Rust Programming Language ch. 4 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- **Ownership** = a set of compiler-checked rules governing how a program manages memory. No garbage
  collector, no manual allocate/free. A violated rule means the program does not compile; ownership
  features have no runtime cost (§4.1).
- **The three ownership rules** (§4.1):
  1. Each value has an *owner*.
  2. There can be only one owner at a time.
  3. When the owner goes out of scope, the value is dropped.
- **Stack vs heap** (§4.1):
  - Stack: LIFO push/pop; every value must have a known, fixed size. Pushing is not "allocating".
  - Heap: for data whose size is unknown at compile time or may change. The allocator finds a big
    enough free spot, marks it in use, returns a *pointer* (fixed size, so it can live on the stack).
  - Pushing is faster than allocating (no search, no bookkeeping); heap access is slower because a
    pointer must be followed, and processors do better with data that is close together.
  - Function arguments (including pointers to heap data) and locals are pushed on call, popped on return.
  - The main purpose of ownership is managing heap data: tracking who uses it, minimizing duplicates,
    cleaning up unused data.
- **Scope** = the range of the program in which an item is valid: from its declaration to the end of
  the enclosing scope (§4.1).
- **Move**: assigning or passing a non-`Copy` value transfers ownership and invalidates the source
  variable. It copies only the stack part (like a shallow copy) plus invalidation (§4.1).
- **Reference**: an address that can be followed to data owned by another variable; unlike a pointer,
  it is guaranteed to point to a valid value of a particular type for the reference's whole life.
  Creating a reference is called **borrowing** (§4.2).
- **Slice**: a reference to a contiguous sequence of elements in a collection; it is a kind of
  reference, so it has no ownership (§4.3).

## Rules and Semantics

### Memory, `drop`, move, copy (§4.1)

- String literals are hardcoded into the executable: fast and efficient, but only because they are
  immutable. `String` manages heap data, so it can hold text of unknown/changing size and be mutated.
- `String::from` requests memory from the allocator at run time. The memory is returned automatically
  when the owning variable goes out of scope: Rust calls the special function `drop` at the closing
  curly bracket. (C++ calls this pattern RAII.)
- A `String` value is three stack fields: pointer to the heap contents, length (bytes currently
  used), capacity (bytes received from the allocator).
- `let s2 = s1;` copies pointer, length, capacity -- not the heap data. `s1` is then considered
  invalid, so only `s2` frees the memory. This prevents a *double free*.
- Rust never automatically makes "deep" copies, so any *automatic* copy can be assumed cheap.
- Assigning a completely new value to an existing variable drops the old value immediately:
  `let mut s = String::from("hello"); s = String::from("ahoy");` frees `"hello"` right away.
- `clone` makes a deep copy (heap data too). A `clone` call is a visual signal that arbitrary,
  possibly expensive code runs.
- `Copy` trait: types stored entirely on the stack can have it; variables of such types are trivially
  copied instead of moved and stay valid after assignment. For them deep and shallow copy are the same.
- A type cannot be annotated `Copy` if it, or any of its parts, implements `Drop` (compile error).
- General rule: any group of simple scalar values can be `Copy`; nothing that requires allocation or
  is some form of resource can be.
- Passing a value to a function moves or copies exactly as assignment does. Returning a value
  transfers ownership to the caller.
- A variable holding heap data that goes out of scope is cleaned up by `drop` unless ownership was
  moved elsewhere. A moved-from variable going out of scope does nothing special.

### References and borrowing (§4.2)

- `&s1` creates a reference that refers to `s1` without owning it; the referent is not dropped when
  the reference stops being used. Parameter type `&String` means "reference to a String".
- A function taking references need not return values to hand ownership back; it never had it.
- References are immutable by default, like variables. Mutating through one needs `&mut`.
- Mutable reference needs three things: the binding is `mut`, the call site uses `&mut s`, and the
  parameter type is `&mut String`. The signature then makes mutation obvious.
- **The rules of references**:
  1. At any given time: *either* one mutable reference *or* any number of immutable references.
  2. References must always be valid.
- With a mutable reference to a value, no other reference to that value may exist.
- Multiple immutable references are fine: readers cannot affect each other.
- A reference's scope runs from where it is introduced through its **last use**, not to the end of
  the block. So immutable refs last used before a `&mut` is created do not conflict with it.
- A separate `{ }` block allows several mutable references, just not simultaneous ones.
- The restriction lets Rust prevent **data races** at compile time. A data race needs all three of:
  two or more pointers accessing the same data at the same time; at least one writing; no mechanism
  synchronizing access. Data races cause undefined behavior.
- No dangling references: the compiler ensures data does not go out of scope before a reference to it.

### Slices (§4.3)

- `&s[starting_index..ending_index]`: `starting_index` is the first position, `ending_index` is one
  more than the last position. Internally a slice stores a pointer to the start and a length
  (`ending_index - starting_index`). `&s[6..11]` = pointer to byte 6, length 5.
- String slice type is written `&str`; it is tied to the underlying data, so the borrow rules keep it
  valid (unlike a bare `usize` index, which silently goes stale when the `String` changes).
- String slice range indices must fall on valid UTF-8 character boundaries; slicing in the middle of
  a multibyte character makes the program exit with an error.
- String literals are slices: `let s = "Hello, world!";` has type `&str`, pointing into the binary.
  That is why literals are immutable -- `&str` is an immutable reference.
- General slices: `&a[1..3]` on an `[i32]` array has type `&[i32]`; it stores a reference to the
  first element and a length. Same mechanism applies to other collections.

## Syntax and API Reference

| Form | Meaning | § |
|---|---|---|
| `String::from("hello")` | heap `String` from a literal; `::` namespaces `from` under `String` | 4.1 |
| `s.push_str(", world!")` | append a literal to a `String` (needs `let mut s`) | 4.1 |
| `s1.clone()` | deep copy, heap data included | 4.1 |
| `s.len()` | length of a `String` (returns `usize`) | 4.1 |
| `&x` / `&mut x` | immutable / mutable borrow | 4.2 |
| `*` | dereference operator, opposite of `&` (details in ch. 8, ch. 15) | 4.2 |
| `s.as_bytes()` | view a `String` as an array of bytes | 4.3 |
| `bytes.iter().enumerate()` | iterate yielding `(index, &element)` tuples | 4.3 |
| `b' '` | byte literal | 4.3 |
| `s.clear()` | empty a `String`; takes a mutable reference | 4.3 |
| `&s[0..5]`, `&s[..2]`, `&s[3..]`, `&s[..]` | slice; omit start for 0, end for len, both for whole | 4.3 |

Types that implement `Copy` (§4.1): all integer types (e.g. `u32`); `bool`; all floating-point types
(e.g. `f64`); `char`; tuples containing only `Copy` types -- `(i32, i32)` is `Copy`, `(i32, String)`
is not.

```rust
fn calculate_length(s: &String) -> usize { s.len() }      // borrow, read only
fn change(some_string: &mut String) { some_string.push_str(", world"); }
fn first_word(s: &str) -> &str {                          // idiomatic signature
    let bytes = s.as_bytes();
    for (i, &item) in bytes.iter().enumerate() {          // `&item` destructures the reference
        if item == b' ' { return &s[0..i]; }
    }
    &s[..]
}
```

## Decision Rules

- Functions should not take ownership of arguments unless they need to (stated as idiomatic Rust,
  §4.3). Borrow with `&T` to read, `&mut T` to mutate (§4.2).
- Returning a tuple like `(String, usize)` just to give ownership back works but is "too much
  ceremony"; use a reference parameter instead (§4.1, §4.2).
- Use `clone` only when a real deep copy is wanted; the E0382 help suggests it "if the performance
  cost is acceptable" (§4.1).
- Prefer `&str` over `&String` for string parameters: the same function then accepts `&String`
  values, slices of a `String`, and string literals, with no loss of functionality (§4.3).
- Return a slice rather than an index into a collection: the index is a separate value that can get
  out of sync, the slice is checked by the compiler (§4.3).
- To return data created inside a function, return the owned value (`String`), not a reference (§4.2).

## Pitfalls and Compiler Errors

- **E0382 ``borrow of moved value: `s1` ``** (§4.1): using `s1` after `let s2 = s1;`. Note says the move
  occurs because `String` does not implement the `Copy` trait. Compiler help: `let s2 = s1.clone();`.
  Using a variable after passing it by value to a function is likewise a compile-time error.
- **E0596 ``cannot borrow `*some_string` as mutable, as it is behind a `&` reference``** (§4.2):
  calling `push_str` through `&String`. Fix: `some_string: &mut String`, pass `&mut s`, declare
  `let mut s`.
- **E0499 ``cannot borrow `s` as mutable more than once at a time``** (§4.2): `let r1 = &mut s;
  let r2 = &mut s;` with `r1` used afterwards. Fix: end the first borrow first (inner `{ }` scope, or
  stop using `r1` before creating `r2`).
- **E0502 ``cannot borrow `s` as mutable because it is also borrowed as immutable``** (§4.2, §4.3):
  `&mut s` created while earlier `&s` refs are still used later. Also triggered by `s.clear()` while a
  `&str` slice of `s` is used afterwards. Fix: finish using the immutable refs before mutating.
- **E0106 `missing lifetime specifier`** (§4.2): `fn dangle() -> &String` returning `&s` of a local.
  Help text: the return type contains a borrowed value but there is no value for it to be borrowed
  from. Book's fix: return `String` directly (ownership moves out, nothing is deallocated). The
  compiler also mentions `&'static String` but calls that uncommon.
- Stale index bug (§4.3): `let word = first_word(&s); s.clear();` with `first_word` returning `usize`
  compiles fine, yet `word` (5) is now meaningless. Tracking start and end indices is worse. Slices
  turn this logic bug into a compile-time error.
- Slicing a string in the middle of a multibyte character is a runtime error, not a compile error
  (§4.3).

## Idioms and Best Practices

- Read borrowing errors as the compiler pointing at a potential bug early, with the exact location
  (§4.2).
- Write `&s[..2]` rather than `&s[0..2]`, `&s[3..]` rather than `&s[3..len]`, `&s[..]` for all (§4.3).
- `&String` arguments work where `&str` is expected ("equivalent to whole slices"); this relies on
  deref coercions (ch. 15). A literal can be passed directly with no slice syntax (§4.3).
- Use `for (i, &item) in bytes.iter().enumerate()` rather than computing indices by hand (§4.3).
- Use an inner block `{ let r1 = &mut s; }` to limit a mutable borrow explicitly (§4.2).

## Details Worth Knowing

- Drop order shown in Listing 4-3/4-4 comments: at the end of `main`, later-declared variables go
  out of scope first (`x`, then `s`; `s3`, then `s1`) (§4.1).
- Capacity vs length matters but is not relevant to ownership; ch. 8 covers non-ownership aspects of
  `String` (§4.1).
- Adding the `Copy` annotation to your own type: see "Derivable Traits" in Appendix C; traits are
  ch. 10 (§4.1).
- Lifetimes, which E0106 refers to, are covered in ch. 10 (§4.2).
- §4.3 assumes ASCII only; proper UTF-8 handling is in ch. 8. Iterators are ch. 13; patterns ch. 6.
- `assert_eq!(slice, &[2, 3]);` is how the book checks an array slice `&a[1..3]` of `[1, 2, 3, 4, 5]`
  (§4.3).
- The `::` syntax is revisited for methods (ch. 5) and module paths (ch. 7) (§4.1).
