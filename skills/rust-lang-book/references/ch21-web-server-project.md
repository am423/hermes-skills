# Ch 21 - Final Project: Building a Multithreaded Web Server

Source: The Rust Programming Language ch. 21 (rust-lang/book @ 5c23042; Rust 1.99.1, edition 2024).

Project chapter: a hand-written HTTP server (`hello` crate: `src/main.rs` binary + `src/lib.rs` thread pool)
using only `std`. No async/await, no external crates. L21-N = the book's Listing 21-N.

## Core Model

- TCP vs HTTP (§21.1): both are request-response protocols (client initiates, server responds). TCP is the
  lower level: how bytes travel, not what they mean. HTTP defines the contents and normally rides on TCP.
- Stream vs connection (§21.1): a `TcpStream` is one open client-server connection; "connection" names the
  whole request/response cycle. `incoming()` yields connection *attempts*, hence each item is a `Result`
  (e.g. an OS limit on simultaneous open connections can make attempts fail).
- Thread pool (§21.2): a fixed group of pre-spawned threads waiting for work. The pool keeps a queue of
  jobs; each thread pops a job, runs it, asks for another. At most N jobs run concurrently (N = thread
  count); extra requests queue. The fixed N is the defence against DoS by unbounded thread creation.
- Worker (§21.2): the pooling term for the struct between the pool and a thread. It owns an `id` and a
  `JoinHandle<()>`; its thread fetches jobs from the shared queue and runs them. Needed because
  `thread::spawn` wants its code at creation time, while a pool needs threads that wait for code sent later.
- Job (§21.2): a boxed closure, `type Job = Box<dyn FnOnce() + Send + 'static>;`, sent down a channel.

## Rules and Semantics

### HTTP and the single-threaded server (§21.1)

- Request: `Method Request-URI HTTP-Version CRLF`, then `headers CRLF`, then `message-body`.
  Response: `HTTP-Version Status-Code Reason-Phrase CRLF`, then `headers CRLF`, then `message-body`.
- CRLF is `\r\n`. Request line example: `GET / HTTP/1.1`; headers start at `Host:`; `GET` has no body.
  A browser ends a request with two newlines in a row, so read lines until the first empty line.
- Minimal success response: `HTTP/1.1 200 OK\r\n\r\n` (no headers, no body). 404 status line used:
  `HTTP/1.1 404 NOT FOUND`. A body needs a `Content-Length` header set to the body's size.
- `TcpListener::bind("127.0.0.1:7878")` returns `Result<T, E>`; binding fails e.g. when two instances of
  the program listen on the same port. `bind` acts like `new`, named after "binding to a port".
- The connection closes when the `TcpStream` is dropped (part of its `drop` implementation), i.e. at the
  end of each loop iteration. A server that sends nothing makes browsers show "Connection reset".
- `BufReader::lines()` (from the `BufRead` trait) yields `Result<String, std::io::Error>`, splitting on
  newline bytes; errors mean invalid UTF-8 or a read failure.
- Only the request line is needed for routing: `buf_reader.lines().next().unwrap().unwrap()`; the first
  `unwrap` handles the `Option` (iterator empty), the second the `Result`.
- `match` on a `String` against string literals needs an explicit slice, `match &request_line[..]`:
  `match` does not auto-reference/dereference the way the equality method does.

### ThreadPool design and its evolution (§21.2-21.3)

| Step | Change | Why |
| --- | --- | --- |
| L21-11 | `thread::spawn` per connection | Works, but unbounded threads can exhaust the system |
| L21-12 | Ideal API: `ThreadPool::new(4)`, `pool.execute(closure)` | Design the caller's interface first |
| (unnumbered) | `pub struct ThreadPool;` in `src/lib.rs`, stub `new`, stub `execute` | Compiler-driven |
| L21-13 | `assert!(size > 0)` in `new`, `# Panics` doc section | Zero is a valid `usize`, not a pool |
| L21-14 | `threads: Vec<thread::JoinHandle<()>>`, `Vec::with_capacity(size)` | Storage for threads |
| L21-15 | private `Worker { id, thread }`; pool holds `workers: Vec<Worker>` | Threads must wait for work |
| L21-16 | `mpsc::channel()`; pool keeps `sender: mpsc::Sender<Job>` | Channel is the job queue |
| L21-17 | pass `receiver` to every `Worker::new` | Fails: E0382, receiver moved in loop |
| L21-18 | `Arc::new(Mutex::new(receiver))`, `Arc::clone(&receiver)` per worker | Share one receiver |
| L21-19 | `Job` becomes a type alias for the boxed closure; `execute` boxes and sends | Work transfer |
| L21-20 | worker closure is `move`, loops: lock, `recv`, run job | Pool now functional |
| L21-22 | `impl Drop` joining each worker via `&mut self.workers` | Fails: E0507 |
| (unnumbered) | iterate `self.workers.drain(..)` instead | Owned workers, so `join` can consume |
| L21-23 | `sender: Option<mpsc::Sender<Job>>`; `drop(self.sender.take())` first | Close before joining |
| L21-24 | worker `match`es `recv()`; `Err(_)` => `break` | Threads exit when channel closes |
| L21-25 | `listener.incoming().take(2)` in `main` | Demo: pool drops at end of `main` |

- Why `FnOnce() + Send + 'static` for `execute`: mirrors `thread::spawn`'s bounds, since the closure is
  eventually handed to a spawned thread. `FnOnce` because a request's closure runs exactly once; `Send`
  to move it across threads; `'static` because the thread's run time is unknown. `FnOnce()` keeps its
  `()` even with no parameters; the unit return type may be omitted.
- Why `Arc<Mutex<Receiver>>`: Rust's channel is multiple producer, single consumer, so the receiving end
  cannot be cloned; each job must be processed once, not broadcast; taking a job mutates the receiver.
  `Arc` gives shared ownership across workers, `Mutex` lets one worker at a time take a job.
- `recv` blocks until a job arrives; `lock()` fails only if the mutex is poisoned (another thread
  panicked while holding the lock), where `unwrap`-panicking is the correct response.
- `send` returns `Err` once the receiving side is gone; `recv` returns `Err` once the sender is gone.

### Graceful shutdown (§21.3)

- Ctrl-C on the main thread stops all other threads at once, mid-request included; hence cleanup in
  `impl Drop for ThreadPool`: dropping the `Sender` is the stop signal, `join` waits for in-flight work.
- Order inside `drop` matters: (1) drop the sender to close the channel, (2) then `join` each worker.
  Joining first blocks the main thread forever, because workers `loop` endlessly waiting on `recv`.
- After the sender is dropped, every `recv` in the worker loops returns an error; the loop must `break`
  on `Err` rather than `unwrap`.
- A join may still block on a worker that is mid-job or has not yet observed the error; the main thread
  waits for it, then joins the rest, which have already left their loops.
- None of this touches closure execution; it would be the same for a pool backing an async runtime.

## Syntax and API Reference

| API | Use in the project |
| --- | --- |
| `std::net::TcpListener::bind(addr)`, `listener.incoming()` | Listen; iterate `Result` streams |
| `std::io::BufReader::new(&stream)` | Buffered reads; manages `std::io::Read` calls |
| `std::io::prelude::*` | Brings the read/write traits into scope |
| `.lines()`, `.take_while(\|line\| !line.is_empty())` | Read header lines up to the blank line |
| `stream.write_all(response.as_bytes())` | Takes `&[u8]`, sends bytes down the connection |
| `fs::read_to_string(filename)` | Load `hello.html` / `404.html` from the project root, not `src` |
| `thread::spawn`, `thread::JoinHandle<()>`, `.join()` | Worker threads; `join` takes ownership |
| `mpsc::channel()`, `mpsc::Sender<Job>`, `mpsc::Receiver<Job>` | Job queue |
| `Vec::with_capacity(size)` | Pre-allocates; slightly cheaper than `Vec::new` growing on insert |
| `Vec::drain(..)` | Removes every element, yielding owned items |
| `Option::take()` / `Iterator::take(2)` | Move value out leaving `None` / at most first two items |
| `cargo check`, `cargo doc --open` | Drive development by errors; view generated docs |

```rust
let (status_line, filename) = match &request_line[..] {       // routing via a destructured tuple
    "GET / HTTP/1.1" => ("HTTP/1.1 200 OK", "hello.html"),
    _ => ("HTTP/1.1 404 NOT FOUND", "404.html"),
};
let response = format!("{status_line}\r\nContent-Length: {length}\r\n\r\n{contents}");

pub fn new(size: usize) -> ThreadPool                         // panics if size is zero
pub fn execute<F>(&self, f: F) where F: FnOnce() + Send + 'static
self.sender.as_ref().unwrap().send(job).unwrap();             // job = Box::new(f); sender is an Option

let message = receiver.lock().unwrap().recv();                // guard is dropped at the end of this `let`
match message { Ok(job) => job(), Err(_) => break }           // worker loop body (prints omitted)
```

- `thread::spawn` signature quoted by the book: `pub fn spawn<F, T>(f: F) -> JoinHandle<T> where
  F: FnOnce() -> T, F: Send + 'static, T: Send + 'static`.

## Decision Rules

- Bounded pool vs thread-per-request (§21.2): spawn-per-request is the simplest working multithreaded
  form but has no limit; a fixed pool keeps load from exhausting resources. Other throughput models
  named: fork/join, single-threaded async I/O, multithreaded async I/O. Async is called out as a natural
  fit for this problem; many async runtimes use thread pools internally (§21.0).
- `new` + `assert!` vs `build` returning `Result` (§21.2): panic when the bad input is treated as
  unrecoverable (a pool of zero threads); the alternative shape is
  `pub fn build(size: usize) -> Result<ThreadPool, PoolCreationError>`.
- `usize` for the size: negative counts are meaningless and it is the type for collection sizes.
- `Option` + `take()` vs `Vec::drain(..)` to move a field out in `drop` (§21.3): wrapping something that
  is always present in `Option` purely as a workaround forces every access to deal with the `Option`;
  look for an alternative, here draining the vector. For `sender` an `Option` IS needed, because it
  must be moved out of the pool and dropped before the joins.
- `thread::spawn` vs `std::thread::Builder` (§21.2): `spawn` panics if the OS cannot create a thread;
  a production pool would use `Builder` and its `spawn`, which returns `Result`.
- Library split: the pool goes in `src/lib.rs` because it is independent of web serving and reusable
  for any work; `main.rs` imports it with `use hello::ThreadPool;`.

## Pitfalls and Compiler Errors

- E0433 "cannot find type `ThreadPool` in this scope" (L21-12): define the struct in `src/lib.rs` and
  import it. Then E0599 "no associated function or constant named `new` found for struct `ThreadPool`"
  and E0599 "no method named `execute` found": add the stub `new`, then the stub `execute`.
- E0382 "use of moved value: `receiver`" (L21-17): `Worker::new(id, receiver)` in a loop moves the
  receiver on the first iteration (`Receiver<Job>` is not `Copy`). Fix: `Arc<Mutex<mpsc::Receiver<Job>>>`
  and `Arc::clone` per worker.
- E0507 "cannot move out of `worker.thread` which is behind a mutable reference" (L21-22): `join` takes
  `self` by value but the loop only has `&mut` workers. Fix: iterate `self.workers.drain(..)`
  (or hold `Option<JoinHandle<()>>` and `take()` it).
- `while let Ok(job) = receiver.lock().unwrap().recv() { job(); }` (L21-21) compiles but serialises
  the pool: `while let` (like `if let` and `match`) keeps temporaries alive until the end of its block,
  so the `MutexGuard` is held while the job runs and no other worker can receive. A plain `let`
  statement drops its temporaries when the statement ends, releasing the lock before `job()`.
  `Mutex` has no public `unlock`; the lock lasts as long as the `MutexGuard<T>` inside the
  `LockResult<MutexGuard<T>>` returned by `lock`.
- `unwrap` inside `drop` can panic while already panicking: a double panic crashes immediately and
  ends cleanup in progress. Acceptable in an example, not recommended in production.
- `#[warn(dead_code)]` warnings on the L21-20 pool ("field `workers` is never read", "fields `id` and
  `thread` are never read") were a reminder that nothing was being cleaned up.
- "If it compiles, it works" is not universally true: the stub `execute` compiled and did nothing;
  in a real project that is the time to start writing unit tests.
- Browser artefacts, not server bugs: several connections per page load (`favicon.ico`, retries after a
  closed connection, speculative pre-connections in Chrome-based browsers); simultaneous `/sleep` tabs
  may load one at a time because some browsers run identical requests sequentially for caching.

## Idioms and Best Practices

- Write the client-facing API first, then implement inside that shape; let `cargo check` errors pick
  the next step (compiler-driven development) (§21.2).
- Keep a new abstraction's interface close to the familiar one it replaces (`execute` mirrors
  `thread::spawn`) so switching needs few call-site changes.
- Keep implementation details private (`Worker`, `Worker::new`); give workers an `id` for logging.
- Document panics with a `# Panics` section in the doc comment.
- Separate concerns: `main` accepts connections, `handle_connection` processes one. Branches compute
  only what differs (status line, filename); shared read-file/write-response code appears once.
- `unwrap` everywhere here is for brevity; production code should handle these errors. `expect` with a
  meaningful message is suggested for the lock.

## Details Worth Knowing

- Port 7878 spells "rust" on a phone keypad and is not a usual HTTP port. The single-threaded server is
  about 40 lines. The slow route is simulated with `thread::sleep(Duration::from_secs(5))` on `/sleep`.
- The book's final full `src/lib.rs` listing differs from the prose: it stores
  `thread: Option<thread::JoinHandle<()>>` in `Worker` and joins with
  `if let Some(thread) = worker.thread.take()` over `&mut self.workers`, i.e. the `Option`/`take`
  variant rather than `drain(..)`. Both are in the source; the prose prefers `drain(..)`.
- Suggested extensions (§21.3): more docs, tests, real error handling instead of `unwrap`, reuse the
  pool for other work, compare with a thread pool crate from crates.io.
- Cross-references: channels, `Arc`, `Mutex` (ch. 16); async (ch. 17); closure traits (ch. 13); type
  aliases (ch. 20); `Option::take` pattern (Listing 18-15); `Config::build` (Listing 12-9).
