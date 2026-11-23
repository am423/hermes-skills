# Ch 16 - Fearless Concurrency

Source: The Rust Programming Language ch. 16 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- **Concurrent** = parts of a program execute independently; **parallel** = parts execute at the same time.
  Ch. 16 says "concurrent" as shorthand for "concurrent and/or parallel"; ch. 17 separates them (§16.0).
- **Fearless concurrency**: ownership + type checking turn many concurrency bugs into compile-time errors
  instead of hard-to-reproduce runtime bugs; code stays easy to refactor (§16.0).
- Rust is not dogmatic: as a lower-level language it offers several tools (threads, message passing, shared
  state) so you can model the problem the way that fits (§16.0).
- **Process** = OS-managed running program; **threads** = independently running parts of one program (§16.1).
- **1:1 threading**: the standard library uses one OS thread per language thread. Other models exist as
  crates with different trade-offs; async (ch. 17) is another approach (§16.1).
- **Channel** = transmitter + receiver; data flows one way. *Closed* when either half is dropped (§16.2).
- Channels resemble **single ownership** (after sending, you no longer use the value); shared memory resembles
  **multiple ownership** (several threads reach the same location), which needs managing (§16.3).
- **Mutex** (mutual exclusion): only one thread may access the data at a time; the *lock* is the part of the
  mutex that tracks who has exclusive access, so the mutex *guards* its data (§16.3).
- `Send` and `Sync` are `std::marker` traits and are among the few concurrency concepts in the *language*;
  almost everything else in the chapter is standard library, so crates can add their own (§16.4).

## Rules and Semantics

### Threads (§16.1)
- `thread::spawn(closure)` starts a new thread running the closure and returns a `JoinHandle<T>`.
- When the main thread finishes, all spawned threads are shut down whether or not they are done.
- No ordering guarantee between threads: scheduling is up to the OS. A spawned thread is not even guaranteed
  to get to run before main exits unless you join it.
- `handle.join()` blocks the calling thread until the handle's thread terminates. *Blocking* = the thread is
  prevented from doing work or exiting. `JoinHandle<T>` is an owned value.
- Placement of `join` decides interleaving: joining after main's own work lets both run interleaved; joining
  before it makes the spawned thread run to completion first (no interleaving).
- `thread::sleep(Duration)` stops the current thread briefly, giving another thread a chance to run; turn
  taking is likely but not guaranteed.
- Closures passed to `spawn` capture by inference; if the body only needs a reference, the closure borrows.
  Rust cannot know how long the spawned thread runs, so a borrow of a local is rejected (E0373).
- `move` before the closure forces it to take ownership of the values it uses, transferring them to the new
  thread. `move` overrides the conservative borrow default; it never lets you break ownership rules.

### Message passing (§16.2)
- `mpsc` = *multiple producer, single consumer*: many sending ends, exactly one receiving end.
- `mpsc::channel()` returns a tuple `(transmitter, receiver)`, conventionally destructured as `(tx, rx)`.
- The spawned thread must own the transmitter to send, so `tx` is moved into its closure.
- `tx.send(value)` takes ownership of the value and moves it to the receiver; returns `Result<T, E>` and
  errors when the receiver has already been dropped.
- `rx.recv()` blocks the current thread until a value arrives and returns `Result<T, E>`; it returns an
  error once the transmitter closes, signalling that no more values are coming.
- `rx.try_recv()` does not block; returns immediately with `Ok` holding a message if one is available or
  `Err` if there is none right now.
- `rx` can be used as an iterator (`for received in rx`); iteration ends when the channel is closed.
- More producers: call `clone` on the transmitter and give each thread its own transmitter. Arrival order
  across producers is nondeterministic and system dependent.

### Shared state (§16.3)
- Two mutex rules: (1) acquire the lock before using the data; (2) unlock when done so others can acquire
  it. Rust's type system and ownership make both impossible to get wrong.
- `Mutex::new(value)` creates a `Mutex<T>`. `m.lock()` blocks the current thread until the lock is ours.
- `lock` returns a `MutexGuard` wrapped in a `LockResult`. The call fails if another thread holding the lock
  panicked; the book's examples `unwrap` so this thread panics too.
- `MutexGuard` implements `Deref` (points at the inner data, usable as a mutable reference) and `Drop`
  (releases the lock automatically when the guard goes out of scope).
- The type is `Mutex<i32>`, not `i32`: the inner value cannot be reached without calling `lock`.
- `Mutex<T>` provides **interior mutability**, as the `Cell` family does: an immutable `Arc<Mutex<T>>`
  binding still yields mutable access to the contents.
- `Rc<T>` is not thread-safe: it updates the count on `clone`/drop without concurrency primitives, so counts
  could go wrong (leaks, or a value dropped while still in use).
- `Arc<T>` (*atomically reference-counted*) has the same API as `Rc<T>` and is safe to share across threads.
  Atomics work like primitive types but are safe to share across threads.

### Send and Sync (§16.4)
- `Send`: ownership of values of the type can be transferred between threads. Almost every Rust type is
  `Send`; exceptions include `Rc<T>` and raw pointers (ch. 20).
- `Sync`: the type is safe to reference from multiple threads. `T` is `Sync` if `&T` is `Send`.
- Both are auto-derived structurally: a type composed entirely of `Send` types is `Send`; a type composed
  entirely of `Sync` types is `Sync`. Almost all primitive types are `Send`; primitive types are all `Sync`.
- Not `Sync`: `Rc<T>` (same reason it is not `Send`), `RefCell<T>` and the related `Cell<T>` family (the
  runtime borrow checking is not thread-safe). `Mutex<T>` is `Sync`.
- They are marker traits with no methods. Implementing them manually requires unsafe Rust (ch. 20).

## Syntax and API Reference

```rust
use std::sync::{Arc, Mutex, mpsc};
use std::thread;
use std::time::Duration;

let handle = thread::spawn(move || { /* owns captured values */ });
handle.join().unwrap();                       // wait for the thread
thread::sleep(Duration::from_millis(1));      // also Duration::from_secs(1)

let (tx, rx) = mpsc::channel();
let tx1 = tx.clone();                         // second producer
tx.send(val).unwrap();                        // moves val
let received = rx.recv().unwrap();            // blocking
for received in rx { /* until channel closes */ }

let counter = Arc::new(Mutex::new(0));
let counter2 = Arc::clone(&counter);          // one clone per thread, made before the move closure
let mut num = counter2.lock().unwrap();       // MutexGuard
*num += 1;                                    // lock released when num drops
println!("Result: {}", *counter.lock().unwrap());
```

| Item | What the chapter says | Ref |
|---|---|---|
| `thread::spawn` | Runs closure on a new thread; returns `JoinHandle<T>` | §16.1 |
| `JoinHandle<T>::join` | Blocks until that thread terminates | §16.1 |
| `mpsc::channel` | Returns `(tx, rx)` | §16.2 |
| `send` / `recv` / `try_recv` | Move value in / block for value / poll without blocking | §16.2 |
| `Mutex::new`, `lock` | Create mutex; block until lock acquired, get `MutexGuard` in a `LockResult` | §16.3 |
| `Arc::new`, `Arc::clone` | Thread-safe shared ownership, same API as `Rc<T>` | §16.3 |
| `std::sync::atomic` | Atomic types: safe, concurrent, atomic access to primitive types | §16.3 |
| `Send`, `Sync` | `std::marker` traits enforced by the compiler | §16.4 |

- Printing a mutex with `{m:?}` after the guard is dropped shows the updated inner value (§16.3).
- Pattern for many threads: collect each `JoinHandle` into a `Vec`, then loop calling `join` on each (§16.3).

## Decision Rules

- Need a spawned thread guaranteed to run to completion: keep the `JoinHandle` and `join` it (§16.1).
- Thread uses data from its parent: use a `move` closure so the thread owns it (§16.1).
- `recv` when the thread has nothing else to do but wait; `try_recv` in a loop when it has other work to do
  between checks (§16.2).
- Channels suit things like a chat system, or many threads each computing a part and sending it to one
  aggregating thread (§16.2).
- Mutex + `Arc` suits dividing a calculation into independent parts across threads, each updating a shared
  result (§16.3).
- Simple numerical operations: prefer the simpler `std::sync::atomic` types over `Mutex<T>` (§16.3).
- `Rc<T>`/`RefCell<T>` for single-threaded multiple ownership/interior mutability; `Arc<T>`/`Mutex<T>` are
  the multithreaded counterparts. Do not use `Arc<T>` by default: thread safety has a performance penalty
  worth paying only when needed (§16.3, §16.4).
- Do not hand-implement `Send`/`Sync` unless building a new concurrent type from non-`Send`/`Sync` parts;
  that needs careful thought and unsafe code; see the Rustonomicon (§16.4).
- For real multithreaded work, look for current crates: they evolve faster than the standard library (§16.4).

## Pitfalls and Compiler Errors

- **E0373** "closure may outlive the current function, but it borrows `v`": a `spawn` closure borrowed a
  local; the note says the function requires the argument to outlive `'static`. Fix: `move ||` (§16.1).
- **E0382** "use of moved value: `v`": after `move`, the parent used the value (e.g. `drop(v)`). `move` does
  not make this legal; the compiler suggests cloning before the closure if both sides need it (§16.1).
- **E0382** "borrow of moved value: `val`": value used after `tx.send(val)`. `send` moved it; the other
  thread could modify or drop it. Do not touch a value after sending it (§16.2).
- **E0382** "borrow of moved value: `counter`" with "value moved into closure here, in previous iteration of
  loop": a bare `Mutex` was moved into several thread closures. Fix: shared ownership via `Arc` (§16.3).
- **E0277** "`Rc<Mutex<i32>>` cannot be sent between threads safely" / "the trait `Send` is not implemented
  for `Rc<Mutex<i32>>`": `Rc` used across threads. Fix: swap to `Arc` (`use`, `new`, `clone` calls) (§16.3).
- `mpsc::channel()` with no later use does not compile: Rust cannot tell what type will be sent (§16.2).
- Forgetting to join: spawned work is cut off when main ends, or may never start (§16.1).
- Joining too early serializes the work and removes concurrency (§16.1).
- **Deadlock**: an operation needs two locks and two threads each hold one, waiting forever. Rust does not
  prevent this logic error, as it does not prevent `Rc<T>` reference cycles (§16.3).
- Thread hazards named by the book: race conditions (data accessed in an inconsistent order), deadlocks,
  and situational hard-to-reproduce bugs. Rust mitigates them; careful design is still required (§16.1).

## Idioms and Best Practices

- Name channel halves `tx` and `rx` (traditional abbreviations for transmitter/receiver) (§16.2).
- Shadow the shared handle inside the loop: `let counter = Arc::clone(&counter);` then `move` it (§16.3).
- Hold a `MutexGuard` in an inner block; the lock is released when that scope ends (§16.3).
- Examples `unwrap` on `send`/`recv`/`lock`/`join`; real applications should handle the errors properly
  using ch. 9 strategies (§16.2).
- Slogan quoted from the Go documentation: "Do not communicate by sharing memory; instead, share memory by
  communicating" (§16.2).

## Details Worth Knowing

- If you see no interleaving in the thread examples, increase the loop ranges to give the OS more chances to
  switch threads (§16.1).
- `let (tx, rx) = ...` is a destructuring pattern in `let`; patterns are covered in ch. 19 (§16.2).
- Because the main `for received in rx` loop contains no delay, pauses seen between messages prove main is
  waiting on the sender (§16.2).
- The reason primitives are not atomic and std types do not use `Arc<T>` by default is purely the performance
  cost of thread-safety guarantees (§16.3).
- `Mutex<T>`/`Arc<T>` parallels `RefCell<T>`/`Rc<T>`: the first of each pair gives interior mutability, the
  second shared ownership (§16.3).
- std docs for `Mutex<T>` and `MutexGuard` cover deadlock-related details (§16.3).
- Forward references: ch. 17 covers async; ch. 20 covers unsafe Rust and raw pointers; the ch. 21 project
  uses these concurrency tools in a more realistic setting (§16.4).
