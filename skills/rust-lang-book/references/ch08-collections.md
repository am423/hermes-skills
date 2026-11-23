# Ch 8 - Common Collections

Source: The Rust Programming Language ch. 8 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- Collections hold multiple values and, unlike the built-in array and tuple types, keep their data on
  the heap: the amount need not be known at compile time and can grow or shrink at runtime. Each kind
  has different capabilities and costs. (§8.0)
- The three covered (§8.0):
  - **Vector** `Vec<T>`: variable number of values of one type, stored next to each other in memory.
  - **String**: a collection of characters; implemented as a collection of bytes plus methods that
    interpret those bytes as text.
  - **Hash map** `HashMap<K, V>`: associates values with keys via a hashing function; one
    implementation of the general *map* structure.
- `String` is a wrapper over a `Vec<u8>` with extra guarantees, restrictions and capabilities. (§8.2)
- Three views of string data: bytes, Unicode scalar values (`char`), and grapheme clusters (closest to
  what people call letters). Rust makes you choose explicitly. (§8.2)
- A collection owns its contents: dropping it drops its elements. (§8.1, §8.3)

## Rules and Semantics

### Vectors (§8.1)

- A vector stores values of the same type only; `Vec<T>` is generic and can hold any type.
- An empty `Vec::new()` needs a type annotation unless later pushes let Rust infer the element type.
  With initial values (`vec![1, 2, 3]`) the type is inferred (`Vec<i32>`, i32 being the default integer).
- Adding elements requires the binding to be `mut`.
- Indexing starts at zero. Two read forms:
  - `&v[i]` gives a reference to the element; panics if `i` is out of range.
  - `v.get(i)` returns `Option<&T>`; `None` when out of range, no panic.
- Borrowing rules apply to element references: while an immutable reference to any element is alive,
  the vector cannot be mutated (e.g. `push`). Reason: elements are contiguous, so adding one may need
  a new allocation and a copy of the old elements, leaving the old reference pointing at deallocated
  memory.
- Iteration: `for i in &v` yields immutable references; `for i in &mut v` yields mutable references,
  and the value is changed through the `*` dereference operator (`*i += 50;`).
- The reference the `for` loop holds prevents modifying the whole vector inside the loop body:
  inserting or removing items there is a compile error similar to the one above.
- Rust must know the element types at compile time to know how much heap memory each element needs.
- Dropping: a vector is freed when it goes out of scope and all its contents are dropped with it. The
  borrow checker ensures references to contents are used only while the vector is valid.

### Strings (§8.2)

- The core language has only one string type: the string slice `str`, usually seen borrowed as `&str`.
  String literals are stored in the program's binary and are therefore string slices.
- `String` comes from the standard library: growable, mutable, owned, UTF-8 encoded. Both `String` and
  string slices are UTF-8 encoded; "strings" may mean either.
- `to_string` is available on any type implementing the `Display` trait (string literals do).
  `String::from` and `to_string` do the same thing.
- `push_str` takes a string slice, so it does not take ownership of its argument; `push` takes a
  single character.
- `+` uses the `add` method, whose signature with concrete types is roughly
  `fn add(self, s: &str) -> String`:
  - The left operand is taken by value: `s1` is moved and no longer valid.
  - The right operand must be a reference: only a string slice can be added to a `String`; two
    `String` values cannot be added together.
  - `&s2` of type `&String` is accepted because of deref coercion, which turns `&s2` into `&s2[..]`.
    `s2` stays valid.
  - It takes ownership of `s1`, appends a copy of `s2`'s contents, and returns ownership of the
    result; more efficient than copying both.
- `format!` works like `println!` but returns a `String`; the generated code uses references, so it
  takes ownership of none of its parameters.
- `String` does not support integer indexing (`s[0]` does not compile). Reasons:
  - A byte index does not always correspond to a valid Unicode scalar value ("Hola" is 4 bytes;
    "Здравствуйте" is 24 bytes, 2 per scalar value; `З` is bytes `208`, `151`).
  - Returning the raw byte is rarely what users want (for `"hi"` it would be `104`, not `h`).
  - Indexing is expected to be constant time (O(1)), which cannot be guaranteed: Rust would have to
    walk from the start to count valid characters.
  - It is unclear what the return type should be: byte, character, grapheme cluster, or string slice.
- Slicing with a range is allowed and selects BYTES: `&hello[0..4]` is a `&str` of the first 4 bytes
  (`Зд`). A range that splits a character panics at runtime.
- Iterate explicitly: `chars` for Unicode scalar values, `bytes` for raw bytes. Grapheme clusters are
  not provided by the standard library; crates on crates.io provide them.

### Hash maps (§8.3)

- Not in the prelude: needs `use std::collections::HashMap;`. No built-in construction macro.
- Data lives on the heap. Homogeneous: all keys one type, all values one type.
- `get` takes the key by reference and returns `Option<&V>`; `None` if the key is absent.
- Iterating `for (key, value) in &scores` visits pairs in an arbitrary order.
- Ownership on `insert`: `Copy` types (like `i32`) are copied in; owned values (like `String`) are
  moved and the map becomes their owner, so the original variables are invalid afterwards.
- Inserting references does not move the values, but they must stay valid at least as long as the map.
- Each unique key has exactly one value at a time (many keys may share an equal value).
- Update policies:
  - Overwrite: `insert` with an existing key replaces the value.
  - Insert only if absent: `entry(key)` returns the enum `Entry` (a value that might or might not
    exist); `or_insert(v)` returns a mutable reference (`&mut V`) to the existing value, or inserts
    `v` and returns a mutable reference to it.
  - Update from the old value: keep the `&mut V` from `or_insert` and assign through `*`.
- Default hasher is *SipHash*: resistant to hash-table denial-of-service (DoS) attacks, not the
  fastest. A *hasher* is a type implementing the `BuildHasher` trait; a different one can be specified.

## Syntax and API Reference

```rust
let v: Vec<i32> = Vec::new();
let v = vec![1, 2, 3];
let mut v = Vec::new();  v.push(5);
let third: &i32 = &v[2];
let third: Option<&i32> = v.get(2);
for i in &v { println!("{i}"); }
for i in &mut v { *i += 50; }
```

```rust
let mut s = String::new();
let s = "initial contents".to_string();
let s = String::from("initial contents");
s.push_str("bar");   s.push('l');
let s3 = s1 + &s2;                    // s1 moved
let s = format!("{s1}-{s2}-{s3}");    // nothing moved
let s = &hello[0..4];                 // byte-range slice
for c in "Зд".chars() { /* З, д */ }
for b in "Зд".bytes() { /* 208, 151, 208, 180 */ }
```

```rust
use std::collections::HashMap;
let mut scores = HashMap::new();
scores.insert(String::from("Blue"), 10);
let score = scores.get(&team_name).copied().unwrap_or(0);
for (key, value) in &scores { println!("{key}: {value}"); }
scores.entry(String::from("Yellow")).or_insert(50);
for word in text.split_whitespace() {
    let count = map.entry(word).or_insert(0);
    *count += 1;
}
```

| API | Notes |
|---|---|
| `Vec::new` / `vec!` / `push` / `pop` | `pop` removes and returns the last element (§8.1) |
| `get` (Vec) | `Option<&T>` (§8.1) |
| `String::new`, `String::from`, `to_string` | creation (§8.2) |
| `push_str`, `push`, `+`, `format!` | growth / concatenation (§8.2) |
| `chars`, `bytes` | explicit iteration (§8.2) |
| `contains`, `replace` | search; substitute parts of a string (§8.2) |
| `HashMap::new`, `insert`, `get`, `entry`, `or_insert` | core map API (§8.3) |
| `copied`, `unwrap_or` | `Option<&i32>` -> `Option<i32>`; default when `None` (§8.3) |
| `split_whitespace` | iterator over whitespace-separated subslices (§8.3) |

## Decision Rules

- `&v[i]` when an out-of-range index should crash the program; `v.get(i)` when it may occasionally
  happen in normal operation (e.g. user-entered index) and you want to handle `None`. (§8.1)
- Iterate over elements rather than indexing one at a time to visit every element. (§8.1)
- Mixed types in one vector: wrap them in an enum when the full set of types is known at compile time
  (then `match` guarantees every case is handled). If the set is not known until runtime, use a trait
  object instead (ch. 18). (§8.1)
- `String::from` vs `to_string`: equivalent; choose by style and readability. (§8.2)
- `+` for simple two-string concatenation; `format!` when combining several pieces, since it is much
  easier to read and moves nothing. (§8.2)
- Use `chars` or `bytes` deliberately depending on whether you need scalar values or raw bytes. (§8.2)
- Hash map vs vector: use a hash map to look data up by a key of any type instead of by index. (§8.3)
- Use `entry(...).or_insert(...)` instead of hand-written check-then-insert: cleaner, and "plays more
  nicely with the borrow checker". (§8.3)
- Keep the default SipHash unless profiling shows hashing is too slow; then specify another hasher,
  typically from a crates.io library rather than writing one from scratch. (§8.3)

## Pitfalls and Compiler Errors

- **E0502** `cannot borrow `v` as mutable because it is also borrowed as immutable`: `let first =
  &v[0]; v.push(6);` then using `first`. Cause: `push` may reallocate. Fix: do not hold an element
  reference across a mutation. (§8.1)
- Index past the end with `&v[100]` panics at runtime; `v.get(100)` returns `None`. (§8.1)
- Inserting or removing items of a vector inside a `for` loop over it does not compile. (§8.1)
- **E0277** `the type `str` cannot be indexed by `{integer}``: `let h = s1[0];` on a `String`. Notes say
  "string indices are ranges of `usize`" and suggest `.chars().nth()` or `.bytes().nth()`. (§8.2)
- Runtime panic `end byte index 1 is not a char boundary; it is inside 'З' (bytes 0..2 of string)`
  from `&hello[0..1]`. Range slicing can crash the program; use with caution. (§8.2)
- Using `s1` after `let s3 = s1 + &s2;`: it was moved into `add`. (§8.2)
- Chained `+` (`s1 + "-" + &s2 + "-" + &s3`) is hard to read; use `format!`. (§8.2)
- Assuming the length of a string equals its character count: it is a byte count. (§8.2)
- Assuming one `char` is one letter: some scalar values are diacritics that make no sense alone. (§8.2)
- Using `field_name`/`field_value` after `map.insert(field_name, field_value)`: both were moved. (§8.3)
- Relying on hash map iteration or `{:?}` output order: it is arbitrary. (§8.3)
- Forgetting `*` when assigning through the `&mut V` returned by `or_insert`. (§8.3)

## Idioms and Best Practices

- Prefer `vec![...]` with initial values; explicit `Vec<T>` annotations are rarely needed. (§8.1)
- Word-count idiom: `let count = map.entry(word).or_insert(0); *count += 1;` inside the loop; the
  mutable reference goes out of scope at the end of the `for` loop, so the borrow rules allow it. (§8.3)
- Read-with-default idiom: `map.get(&key).copied().unwrap_or(0)`. (§8.3)
- Take `&str` parameters when ownership is not needed, as `push_str` does. (§8.2)
- Review the std API docs for `Vec<T>`, `String`/`&str` and `HashMap<K, V>`; the chapter covers only
  the basics. (§8.1, §8.2, §8.3)
- Handle UTF-8 correctly up front: Rust makes correct `String` handling the default, exposing more
  complexity early but avoiding non-ASCII bugs later. (§8.2)

## Details Worth Knowing

- Hindi "नमस्ते": 18 bytes, six `char` values (the fourth and sixth are diacritics), four grapheme
  clusters. (§8.2)
- In std, `add` is actually defined with generics and associated types; the concrete signature above
  is what applies for `String`. (§8.2)
- Other names for hash maps elsewhere: hash, map, object, hash table, dictionary, associative
  array. (§8.3)
- `HashMap` is the least often used of the three, hence absent from the prelude and with less std
  support. (§8.3)
- The examples create maps with an unannotated `HashMap::new()` followed by `insert`/`entry` calls;
  the word-count example passes the subslices from `split_whitespace` directly as keys. (§8.3)
- Other std collections are documented under `std::collections`. (§8.0)
- Suggested exercises: median and mode of an integer list; Pig Latin conversion (mind UTF-8); a text
  interface adding employees to departments with a hash map and vectors. (§8.3)
- Forward references: generics ch. 10; lifetimes for references stored in maps ch. 10; traits and
  `BuildHasher` ch. 10; dereference operator and deref coercion ch. 15; trait objects ch. 18; `Vec<T>`
  implementation details in The Rustonomicon. (§8.1, §8.2, §8.3)
