# Ch 20 - Advanced Features: Unsafe Rust

Source: The Rust Programming Language ch. 20 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).
Covers §20.0 (chapter intro) and §20.1 (Unsafe Rust). See also `ch20-advanced-traits-types-functions.md`
and `ch20-macros.md`.

## Core Model

- Ch 20 is a reference chapter for rarely needed features: unsafe Rust, advanced traits, advanced types,
  advanced functions/closures, macros (§20.0).
- **Unsafe Rust** is a "second language" inside Rust: same as regular Rust plus extra abilities, without
  compiler-enforced memory safety for those abilities (§20.1).
- Why it exists (§20.1):
  - Static analysis is conservative: the compiler rejects some valid programs rather than accept invalid
    ones. `unsafe` is how you say "trust me" when the compiler lacks information.
  - Hardware is inherently unsafe; low-level systems work (talking to the OS, writing an OS) needs it.
- **Five unsafe superpowers** - the only things `unsafe` unlocks (§20.1):
  1. Dereference a raw pointer.
  2. Call an unsafe function or method.
  3. Access or modify a mutable static variable.
  4. Implement an unsafe trait.
  5. Access fields of `union`s.
- `unsafe` does NOT turn off the borrow checker or other checks: references used inside an unsafe block
  are still checked. Only the five features above go unchecked for memory safety.
- `unsafe` does not mean the code is dangerous or wrong; it means the programmer, not the compiler,
  guarantees memory is accessed validly.
- Benefit of the marker: any memory-safety bug must originate in an `unsafe` block, so audits are bounded.
- **Safe abstraction**: wrap unsafe code behind a safe API so `unsafe` does not leak to callers. Parts of
  the standard library are audited safe abstractions over unsafe code.

## Rules and Semantics

### Raw pointers (§20.1 "Dereferencing a Raw Pointer")

- Two types: `*const T` (immutable) and `*mut T` (mutable). The `*` is part of the type name, not a
  dereference. "Immutable" here means the pointer can't be directly assigned to after being dereferenced.
- Unlike references and smart pointers, raw pointers:
  - may ignore borrowing rules (immutable + mutable, or multiple mutable, pointers to one location);
  - are not guaranteed to point to valid memory;
  - may be null;
  - implement no automatic cleanup.
- Creating raw pointers is allowed in safe code; only **dereferencing** requires `unsafe`. Creating a
  pointer does no harm; accessing the pointee is where an invalid value can bite.
- Raw borrow operators: `&raw const num` gives `*const i32`, `&raw mut num` gives `*mut i32`. Pointers
  made directly from a local variable are known valid.
- Casting with `as` (e.g. integer address to `*const i32`) yields a pointer of unknown validity; using
  arbitrary memory is undefined (may hold data or not, may be optimized away, may segfault).
- A `*const` and a `*mut` to the same location may coexist (references could not); mutating through the
  `*mut` can create a data race.

### Unsafe functions and methods (§20.1 "Calling an Unsafe Function or Method")

- Declared with `unsafe` before the rest of the definition: `unsafe fn dangerous() {}`.
- Meaning: the function has requirements (a contract) the compiler cannot verify; the caller must uphold
  them. Calling inside `unsafe { }` asserts you read the docs and fulfil the contract.
- Calling without an unsafe block is error E0133.
- Inside the body of an `unsafe fn`, unsafe operations STILL need their own `unsafe` block; the compiler
  warns if you forget. This keeps unsafe blocks small.
- A function containing unsafe code need not be marked `unsafe`; if the body guarantees validity itself,
  expose it as a safe function.

### `extern` and FFI (§20.1 "Using `extern` Functions to Call External Code")

- `extern` supports a Foreign Function Interface (FFI): a way for a language to define functions that a
  different language can call.
- Foreign declarations go in an `extern` block which **must be marked `unsafe`**: `unsafe extern "C" { }`.
  Other languages don't enforce Rust's rules, so the programmer is responsible.
- `"C"` names the application binary interface (ABI): how to call the function at the assembly level.
  `"C"` is the most common. Full ABI list is in the Rust Reference.
- Every item in an `unsafe extern` block is implicitly unsafe to call.
- Mark an individual item `safe` (e.g. `safe fn abs(input: i32) -> i32;`) to allow calls without an
  unsafe block. This is a promise you make; it does not make the function safe by itself.
- Exporting Rust to other languages: put `extern "C"` before `fn` (no extern block) and add
  `#[unsafe(no_mangle)]`. Mangling = the compiler renaming a function to carry more info for later
  compilation stages; it must be disabled so other languages can name the function.
  - `no_mangle` is unsafe because unmangled names can collide across libraries; you must pick a name safe
    to export.
  - Here `unsafe` appears only in the attribute, not on the `extern`.

### Static variables (§20.1 "Accessing or Modifying a Mutable Static Variable")

- Rust's global variables are called *static* variables: `static HELLO_WORLD: &str = "Hello, world!";`.
- Can only store references with the `'static` lifetime; the lifetime is inferred, no annotation needed.
- Reading an immutable static is safe.
- Constants vs immutable statics:
  - a static's value has a fixed address in memory; every use accesses the same data;
  - a constant may duplicate its data wherever it is used;
  - statics can be mutable (`static mut`), constants cannot.
- Any read or write of a `static mut` must be in an `unsafe` block. Multi-threaded access would likely
  cause data races, which is undefined behavior.
- Creating a **reference** to a mutable static is denied by default via the `static_mut_refs` lint,
  including references created invisibly (e.g. by using it in `println!`). Options:
  - opt out with `#[allow(static_mut_refs)]`, or
  - access through a raw pointer made with a raw borrow operator, e.g. `*(&raw const COUNTER)`.

### Unsafe traits (§20.1 "Implementing an Unsafe Trait")

- A trait is unsafe when at least one of its methods has an invariant the compiler can't verify.
- Declare with `unsafe trait Foo { }`; implement with `unsafe impl Foo for i32 { }`. `unsafe impl` is a
  promise to uphold those invariants.
- `Send` / `Sync`: implemented automatically when a type is composed entirely of `Send`/`Sync` types. For
  a type containing a non-`Send`/`Sync` part (such as raw pointers), marking it `Send` or `Sync` requires
  `unsafe`, because you must manually verify the thread-safety guarantees.

### Unions (§20.1 "Accessing Fields of a Union")

- A `union` is like a `struct` but only one declared field is used in a given instance at a time.
- Mainly used to interface with unions in C code.
- Field access is unsafe because Rust can't know the type of the data currently stored.

## Syntax and API Reference

```rust
let mut num = 5;
let r1 = &raw const num;          // *const i32, safe to create
let r2 = &raw mut num;            // *mut i32
unsafe { println!("{}", *r1); }   // deref needs unsafe

let address = 0x012345usize;
let r = address as *const i32;    // arbitrary address; validity unknown
```

```rust
unsafe extern "C" { fn abs(input: i32) -> i32; }       // call needs unsafe { abs(-3) }
unsafe extern "C" { safe fn abs(input: i32) -> i32; }  // callable from safe code

#[unsafe(no_mangle)]
pub extern "C" fn call_from_c() { println!("Just called a Rust function from C!"); }
```

```rust
static mut COUNTER: u32 = 0;
/// SAFETY: (document what callers must guarantee, e.g. single-threaded use)
unsafe fn add_to_count(inc: u32) { unsafe { COUNTER += inc; } }
```

| Item | What the source says |
|---|---|
| `slice.split_at_mut(mid)` | Safe std method on mutable slices; returns two non-overlapping halves |
| `slice.as_mut_ptr()` | Raw pointer to slice data (`*mut i32` for `&mut [i32]`) |
| `slice.len()` | Slice length |
| `std::slice::from_raw_parts_mut(ptr, len)` | Unsafe: builds a slice; must trust pointer is valid |
| `ptr.add(n)` | Unsafe raw-pointer method: offset must also be a valid pointer |
| `rustup +nightly component add miri` | Installs nightly Rust plus Miri |
| `cargo +nightly miri run` / `cargo +nightly miri test` | Run program / test suite under Miri |
| `#[allow(static_mut_refs)]` | Opt out of the deny-by-default lint on refs to `static mut` |
| `#[unsafe(no_mangle)]` | Disable name mangling for an exported function |

Safe-abstraction shape of `split_at_mut` (Listing 20-6): take `len` and `as_mut_ptr()`, then
`assert!(mid <= len);`, then in one `unsafe` block return
`(slice::from_raw_parts_mut(ptr, mid), slice::from_raw_parts_mut(ptr.add(mid), len - mid))`.
The assertion is what makes every pointer used valid, so the function itself stays safe.

## Decision Rules

- Reach for `unsafe` when you know the code is okay but the compiler cannot prove it (§20.1).
- Using `unsafe` for one of the five superpowers "isn't wrong or even frowned upon"; it is just harder to
  get right because the compiler can't help.
- Raw pointers: main uses are interfacing with C code and building safe abstractions the borrow checker
  can't understand. You trade guaranteed safety for performance or foreign/hardware interop.
- Prefer a raw borrow operator over an `as` cast from an integer; there is usually no good reason to make
  a pointer to an arbitrary address.
- Prefer a safe wrapper function over marking a whole function `unsafe` when the body can guarantee the
  invariants itself; mark the function `unsafe` when the caller must uphold something (e.g. the
  single-thread requirement of `add_to_count`).
- Mark an FFI item `safe` only when it has no memory-safety considerations for any input (like C `abs`
  with any `i32`).
- Prefer the concurrency techniques and thread-safe smart pointers from ch. 16 over `static mut`, so the
  compiler checks cross-thread access.
- Run Miri whenever you write unsafe code, combined with good tests.

## Pitfalls and Compiler Errors

- **E0133** "call to unsafe function `dangerous` is unsafe and requires unsafe block": calling an
  `unsafe fn` from safe code. Fix: wrap the call in `unsafe { }` after verifying the contract.
- **E0499** "cannot borrow `*values` as mutable more than once at a time": safe attempt at
  `split_at_mut` returning `(&mut values[..mid], &mut values[mid..])`. The borrow checker only sees two
  mutable borrows of the same slice, not that the halves don't overlap. The compiler's help suggests
  `.split_at_mut(position)`; the hand-rolled fix uses raw pointers as above.
- Building a slice from an arbitrary address (`from_raw_parts_mut(r, 10000)` with `r` cast from an
  integer) is undefined behavior when used: the memory isn't owned and holds no guaranteed valid `i32`s.
- Miri on that code: a warning for the integer-to-pointer cast (Miri can't tell if it is a problem since
  it doesn't know the pointer's origin), then an error `Undefined Behavior` for constructing an invalid
  `&mut [i32]` from a dangling reference.
- Forgetting the inner `unsafe` block inside an `unsafe fn` produces a compiler warning.
- Referencing a `static mut` (even implicitly in `println!`) trips the deny-by-default lint.
- A `safe` FFI marker or an `unsafe impl` that isn't actually upheld is your bug; the compiler trusts it.

## Idioms and Best Practices

- Keep `unsafe` blocks small; it pays off when investigating memory bugs (§20.1).
- Enclose unsafe code in a safe abstraction with a safe API.
- Write a comment starting with `SAFETY` on every unsafe function explaining what the caller must do, and
  on every unsafe operation explaining how the safety rules are upheld.
- Establish validity with checks before the unsafe block (e.g. `assert!(mid <= len)` so an out-of-range
  index panics before any pointer is used).
- Static variable names use `SCREAMING_SNAKE_CASE`.

## Details Worth Knowing

- Miri is an official Rust tool for detecting undefined behavior. It is *dynamic* (runs the program or
  its tests), whereas the borrow checker is *static* (§20.1 "Using Miri to Check Unsafe Code").
- Miri requires nightly Rust; installing it does not change the Rust version your project uses.
- Miri limits: only catches problems in code that actually runs, and doesn't cover every kind of
  unsoundness. A Miri finding means a real bug; a clean run does not prove absence of bugs. It can
  sometimes recommend fixes.
- A slice is a pointer to data plus a length (ch. 4), which is why `from_raw_parts_mut` takes exactly
  those two things.
- Further reading named by the source: The Rustonomicon (official guide for `unsafe`), the Rust Reference
  for ABIs and unions, Appendix G for nightly Rust.
