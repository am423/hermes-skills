# Ch 17 - Fundamentals of Asynchronous Programming: Async, Await, Futures, and Streams

Source: The Rust Programming Language ch. 17 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

## Core Model

- **Async** = code expressed as potential pausing points and eventual results; a runtime handles the
  coordination. An alternative to ch. 16 threads, and complementary to them (§17.0).
- **CPU-bound / compute-bound**: limited by processing speed (video export). **I/O-bound**: limited by input
  and output speed (network download) (§17.0).
- **Concurrency**: one worker switching between several unfinished tasks. **Parallelism**: several workers
  progressing at the exact same time. Work with dependencies is **serial**. One CPU core can still be
  concurrent; multiple cores can also be parallel (§17.0).
- Async Rust code usually runs concurrently; whether it also runs in parallel depends on the hardware, the
  OS, and the async runtime (§17.0).
- **Blocking** call: holds up the program until its data is completely ready; the term is usually reserved
  for calls touching files, network, or other resources (§17.0).
- **Future**: a value that may not be ready now but will be later; a type implementing the `Future` trait.
  Each future tracks its own progress and what "ready" means (§17.1).
- **Polling**: checking a future to see whether its value is available yet (§17.1).
- **Await point**: every use of `await`; the only place control can be handed back to the runtime (§17.1).
- **Runtime**: a crate that manages executing async code. The **executor** is the part of a runtime that
  actually executes it. Rust bundles no runtime (§17.1).
- **Task**: like a thread, but managed by the runtime (library-level code) rather than by the OS (§17.6).
- **Stream**: a sequence of items produced over time; an asynchronous form of iteration (§17.4).
- **Cooperative multitasking**: each future decides when to hand over control via await points, and is
  responsible for not blocking too long (§17.3).
- Hierarchy: the runtime's executor manages tasks; tasks manage futures; a future is the most granular unit
  of concurrency and may represent a tree of other futures (§17.6).

## Rules and Semantics

### Futures, `async`, `await` (§17.1)
- `async` applies to blocks and functions, marking them as interruptible and resumable. `await` is only
  allowed inside async functions or blocks.
- `await` is a **postfix** keyword: `expr.await`. This makes method chains work:
  `trpl::get(url).await.text().await`.
- Futures are **lazy**: nothing happens until awaited (the compiler warns about an unused future). Compare
  iterators, which do nothing until `next` is called. Contrast `thread::spawn`, whose closure starts
  running immediately.
- An `async` block compiles to a unique, anonymous data type implementing `Future`. An `async fn` compiles to
  a non-async function whose body is an async block; it is equivalent to returning
  `impl Future<Output = T>` where `T` is the written return type.
- `async` and `await` compile to code using the `Future` trait, much as `for` compiles to `Iterator` code.
- The compiler builds an invisible **state machine** (as if an enum with one variant per await point holding
  the state needed there). Normal borrowing and ownership rules still apply and are checked.
- `main` cannot be `async` (E0752): it is the program's starting point, so nothing would drive the future
  it returned. `main` can initialize a runtime but is not one. Every program running async code has at
  least one place that sets up a runtime.
- Some runtimes offer macros that permit `async fn main`; they rewrite it into a normal `fn main` that
  runs a future to completion, as `trpl::block_on` does.

### Tasks, joining, channels (§17.2)
- `trpl::spawn_task(future)` resembles `thread::spawn`. The spawned task is shut down when `main` ends; to
  let it finish, await its join handle. The handle is itself a future whose `Output` is a `Result`.
- No OS thread, and not even a task, is needed for concurrency: put work in separate async blocks and let
  `trpl::join` drive them.
- `trpl::join(a, b)` produces one new future whose output is a tuple of both outputs, ready once **both**
  finish. Await the joined future, not the individual ones.
- `trpl::join` is **fair**: it checks each future equally often, alternating, so output order is the same on
  every run. With threads the OS picks; with `spawn_task` order can vary. Runtimes need not guarantee
  fairness for any given operation and often offer APIs to choose.
- **Within one async block, code runs linearly**: await points execute in the order written. Awaiting
  futures one after another is sequential, not concurrent.
- `trpl::channel()` is an async multiple-producer, single-consumer channel. Differences from the ch. 16
  one: `rx` must be mutable, and `recv` returns a future to await rather than the value.
- Async `recv` does not block; it hands control to the runtime until a message arrives or the send side
  closes. It resolves to `Some(message)` per message, then `None` once the channel is closed.
- `send` is not awaited: it does not block, because the channel is unbounded.
- The channel closes when `rx.close` is called or the sender `tx` is dropped. An `async` block that only
  borrows `tx` keeps it alive until the outer block ends; `async move` moves it in so it drops when that
  block finishes. `move` works on async blocks just as on closures.
- What matters is the order in which futures are awaited, not the order in which they are created.
- There is not yet a `for` loop over an asynchronously produced series; use `while let`.

### Yielding and composing (§17.3)
- Rust pauses an async block **only** at an await point; everything between await points is synchronous.
- Long work with no await point blocks all other futures from progressing: one future **starving** others.
- `trpl::yield_now().await` hands control back to the runtime without waiting. It states intent more clearly
  and can be much faster than sleeping: the `sleep` used here always sleeps at least a millisecond, even for
  a `Duration` of one nanosecond.
- `trpl::select(a, b)` finishes as soon as one future finishes. It is **not fair**: it always polls its
  arguments in the order passed (other `select` implementations choose randomly which to poll first).
- Futures compose: a `timeout` is `select` of the caller's future against a `trpl::sleep` timer.

### Streams (§17.4, §17.5)
- Iterators and the async receiver differ in time (sync vs async) and API (`next` vs async `recv`); a
  general stream provides the next item as `Iterator` does, but asynchronously.
- Any iterator can be turned into a stream. Streams are futures, so they combine with any other future.
- `next` on a stream comes from `StreamExt`, not `Stream`; the trait must be in scope.
- `Stream` is the low-level interface combining `Iterator` and `Future`; `StreamExt` layers `next` and
  other `Iterator`-like utility methods on top, and is automatically implemented for every `Stream`.
- Neither `Stream` nor `StreamExt` is in the standard library yet; the common definition comes from the
  `futures` crate and most ecosystem crates use similar ones.

### `Future`, `Pin`, `Unpin` (§17.5)
- `Future::poll` returns `Poll<Self::Output>`: `Pending` = still has work, check again later; `Ready(T)` =
  finished with the value. `Output` is analogous to `Iterator`'s `Item`.
- `await` compiles to calls to `poll`, in a loop that hands control to the runtime instead of blocking. A
  runtime polls each future it is responsible for and puts it back to sleep when it is not ready.
- The `cx: &mut Context` parameter is how a runtime knows when to check a future while staying lazy; you
  generally only care when writing a custom `Future`.
- Do not call `poll` again after `Ready`: many futures panic. Ones that are safe to re-poll say so in
  their documentation. Calling `poll` directly is rare.
- `self: Pin<&mut Self>` is a type annotation on `self`. It tells Rust what type `self` must be for the
  call, and it is restricted to: the type itself, a reference or smart pointer to it, or a `Pin` wrapping a
  reference to it.
- The state machine for an async block may hold **references to itself** between await points. Moving such
  a value would leave internal references pointing at the old, now invalid, location.
- `Pin` wraps pointer-like types (`&`, `&mut`, `Box`, `Rc`; technically types implementing `Deref` or
  `DerefMut`). It is not a pointer and has no behavior of its own; it is a compile-time constraint tool.
- Pinning a value (wrapping a pointer to it in `Pin`) means the value can no longer move. In
  `Pin<Box<SomeType>>` the `SomeType` value is pinned, not the `Box`; the `Box` pointer may still move.
- `Unpin` is a marker trait (like `Send`/`Sync`) saying the type needs no guarantee about being moved. The
  compiler implements it automatically where it can prove safety. `Unpin` is the normal case, `!Unpin`
  (written `impl !Unpin for SomeType`) the special case.
- `Unpin` vs `!Unpin` only matters when using a pinned pointer to the type, like `Pin<&mut SomeType>`.
  `String` is `Unpin`, so a pinned `String` can still be replaced by another at the same location.
- Futures from async blocks may have internal references, so they do not automatically implement `Unpin`.
- Directly awaiting a future pins it implicitly, which is why `pin!` is not needed everywhere.
- `Box<T>` implements `Future` only if the `T` it wraps is a future that implements `Unpin`.
- Each async block has its own compiler-generated type, even with identical `Output`, so differing blocks
  cannot share a `Vec` without trait objects.

## Syntax and API Reference

```rust
fn main() {
    trpl::block_on(async {              // runtime entry; every example is wrapped like this
        let handle = trpl::spawn_task(async { /* ... */ });
        trpl::sleep(Duration::from_millis(500)).await;
        handle.await.unwrap();
    });
}

let (tx, mut rx) = trpl::channel();
tx.send(val).unwrap();                               // no await
while let Some(value) = rx.recv().await { /* ... */ }

match trpl::select(fut1, fut2).await {
    Either::Left(left) => left,                      // first argument won
    Either::Right(right) => right,
}

async fn timeout<F: Future>(future_to_try: F, max_time: Duration) -> Result<F::Output, Duration> {
    match trpl::select(future_to_try, trpl::sleep(max_time)).await {
        Either::Left(output) => Ok(output),
        Either::Right(_) => Err(max_time),
    }
}

use trpl::StreamExt;
let mut stream = trpl::stream_from_iter(iter);
while let Some(value) = stream.next().await { /* ... */ }

use std::pin::{Pin, pin};
let tx_fut = pin!(async move { /* ... */ });
let futures: Vec<Pin<&mut dyn Future<Output = ()>>> = vec![tx1_fut, rx_fut, tx_fut];
trpl::join_all(futures).await;
```

```rust
pub trait Future {
    type Output;
    fn poll(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Self::Output>;
}
pub enum Poll<T> { Ready(T), Pending }

trait Stream {                                       // not in std; common `futures` crate definition
    type Item;
    fn poll_next(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>>;
}
trait StreamExt: Stream {
    async fn next(&mut self) -> Option<Self::Item> where Self: Unpin;
}
enum Either<A, B> { Left(A), Right(B) }
```

| `trpl` item | Behavior | Ref |
|---|---|---|
| `block_on(fut)` | Sets up a `tokio` runtime; blocks this thread until `fut` is done; returns value | §17.1 |
| `get(url)`, `response.text()` | Async HTTP fetch; async read of the whole body | §17.1 |
| `Html::parse`, `select_first`, `inner_html` | Parse; first CSS match (`Option<ElementRef>`); text | §17.1 |
| `spawn_task(fut)` | Spawn a runtime task; returns an awaitable join handle | §17.2 |
| `sleep(Duration)` | Async version of `thread::sleep` | §17.2 |
| `join(a, b)` / `join!(a, b, c, ...)` | Wait for both / for a compile-time-known number of futures | §17.2 |
| `join_all(collection)` | Wait for a runtime-sized collection; returns a `JoinAll` struct | §17.5 |
| `channel()` | Unbounded async mpsc channel; `send`, `recv`, `close`, `tx.clone()` | §17.2 |
| `select(a, b)` | First to finish, as `Either::Left` / `Either::Right` | §17.1 |
| `yield_now()` | Hand control back to the runtime | §17.3 |
| `stream_from_iter(iter)` | Turn an iterator into a stream | §17.4 |
| `spawn_blocking` | Named only as part of the multithreaded-by-default runtime | §17.6 |

- Setup commands: `cargo new hello-async`, `cd hello-async`, `cargo add trpl` (§17.1).
- `trpl` re-exports (sometimes renaming or wrapping) items mainly from the `futures` and `tokio` crates.
  `futures` is an official home for async experimentation and where `Future` was first designed; Tokio is
  the most widely used runtime, especially for web applications (§17.1).
- Imports used: `std::future::Future`, `std::pin::{Pin, pin}`, `std::task::{Context, Poll}` (§17.1, §17.5).

## Decision Rules

- **Threads vs async** (§17.6): work that is *very parallelizable* (CPU-bound, e.g. data where each part is
  processed separately) -> threads. Work that is *very concurrent* (I/O-bound, e.g. messages from many
  sources at differing intervals or rates) -> async. Need both -> combine them freely.
- Thread trade-offs: on many OSes a fair bit of memory per thread; only available where OS and hardware
  support them (some embedded systems have no OS). Async concurrency needs no thread per operation (§17.6).
- Threads are a simpler model, "fire and forget", with no native equivalent of a future; they run to
  completion, interrupted only by the OS. That is a strength or a weakness. Neither is always better (§17.6).
- Threads bound sets of **synchronous** operations (concurrency between threads). Tasks bound sets of
  **asynchronous** operations (concurrency between and within tasks, since a task switches between the
  futures in its body) (§17.6).
- Common mix: blocking or compute-bound work on a dedicated thread, reporting through an async channel that
  an async block awaits, e.g. `thread::spawn` sending on `trpl::channel` while `block_on` receives (§17.6).
- Spawning a thread per download avoids blocking, but thread overhead eventually becomes a problem (§17.0).
- `join` for two futures, `join!` when the count is known at compile time, `join_all` for a collection
  whose size is known only at runtime (§17.2, §17.5).
- `select` when only the first result matters; pass the future that should get first chance first (§17.3).
- Pass `block_on` an async block rather than a single future when more than one async call is needed,
  which is most real code. `block_on` is where you choose to cross between sync and async (§17.1, §17.2).
- Prefer `yield_now` over `sleep` when the goal is only to let other futures run (§17.3).
- Splitting compute-bound work with yields is cheap but not free and can make it much slower; sometimes
  letting an operation block briefly is better overall. Measure real bottlenecks (§17.3).
- Async can still help compute-bound work as a way to structure relationships between parts of a program,
  at the cost of state-machine overhead (§17.3).
- Use `async move` whenever a value must be dropped when the block ends (e.g. channel senders) (§17.2).
- Day to day: mostly `async`/`await`, then `select` and `join!` to control the outermost futures. `Pin` and
  `Unpin` matter mainly for lower-level libraries or writing a runtime (§17.3, §17.5).
- Runtimes differ by target (many-core web server vs single-core microcontroller with no heap); others may
  suit you better than Tokio (§17.1).

## Pitfalls and Compiler Errors

- **E0752** "`main` function is not allowed to be `async`". Fix: plain `main` calling `trpl::block_on` with
  an async block (§17.1).
- **E0599** "no method named `next` found for struct `tokio_stream::iter::Iter`": trait not in scope.
  Fix: `use trpl::StreamExt;` (§17.4).
- **E0277** "`dyn Future<Output = ()>` cannot be unpinned ... the trait `Unpin` is not implemented" from
  `trpl::join_all` over `Vec<Box<dyn Future<Output = ()>>>`. Fix: wrap each async block in `pin!` and
  type the vector as `Vec<Pin<&mut dyn Future<Output = ()>>>`. The compiler note also mentions `Box::pin`
  for when the pinned value must be accessed outside the current scope (§17.5).
- Program never exits: a `while let Some(..) = rx.recv().await` loop waits forever because `tx` is only
  borrowed and never dropped. Fix: `async move` on every sending block, including clones (§17.2).
- Messages arrive all at once after the total delay: sends, sleeps, and receives share one async block and
  run in sequence. Fix: separate async blocks combined with `trpl::join` (§17.2).
- Forgetting to await: the future never runs (§17.1).
- Blocking calls such as `std::thread::sleep` inside a future give no interleaving at all; a future with no
  await point can complete without the other ever running (§17.3).
- Unawaited spawned task is cut off when the main async block finishes (§17.2).

## Idioms and Best Practices

- Chain with postfix await instead of intermediate bindings (§17.1).
- `Option::map` is more idiomatic than `match` for transforming an optional value (§17.1).
- Return identifying data alongside results (e.g. the URL with its title) so a raced result stays
  meaningful (§17.1).
- `Ext` suffix: community pattern for a trait that extends another. Keeping `Stream` and `StreamExt`
  separate lets convenience APIs evolve without touching the foundational trait (§17.4, §17.5).
- For a custom streaming type implement only `Stream`; users get `StreamExt` methods automatically (§17.5).
- Build abstractions by composition, e.g. timeouts combined with retries around network calls (§17.3).

## Details Worth Knowing

- Languages such as C# and JavaScript also have `async`/`await`, but Rust's handling differs significantly;
  most languages bundle a runtime and Rust does not (§17.1).
- `trpl::select` is built on the more general `select` from the `futures` crate (§17.1).
- The real `StreamExt::next` signature is `fn next(&mut self) -> Next<'_, Self> where Self: Unpin;` because
  it supports Rust versions without async functions in traits; `Next` is a struct implementing `Future`.
  In `trpl`'s version `next` has a default implementation that calls `Stream::poll_next` (§17.5).
- A `Stream` definition much like the `futures` one will likely end up in the standard library (§17.5).
- The runtime behind `trpl` is multithreaded by default. Many runtimes use **work stealing** to move tasks
  between threads based on utilization, which requires threads and tasks together (§17.6).
- Listings write `F: Future` and `dyn Future` with no `use` line; the desugared `page_title` example does
  import `std::future::Future` (§17.1, §17.3, §17.5).
- In some Rust-based embedded operating systems cooperative multitasking is the only kind (§17.3).
- Types needing `Pin` appear mostly in async Rust but occasionally elsewhere. Further reading: `std::pin`
  API docs; chapters 2 and 4 of *Asynchronous Programming in Rust* (§17.5).
- Forward references: trait objects and `self` type annotations in ch. 18; ch. 21 compares threads with
  tasks and futures in a larger project (§17.5, §17.6).
