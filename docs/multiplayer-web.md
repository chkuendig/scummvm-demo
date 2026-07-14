# TODO: SCUMM HE multiplayer on the web port

Status: **design only** — nothing implemented. Written 2026-07-12/14 after a
source survey; revisit before starting work (upstream moves).

Goal: Moonbase Commander + Backyard sports online play in the Emscripten
build. Web↔web first; cross-play with native as a pathway, not a launch
requirement. Abstractions must not disturb other backends (model: the
http/curl vs http/emscripten split).

## Current architecture (verified in source, 2026-07)

```
engines/scumm/he/net/            game logic layer
  net_main.cpp   "Net"    — sessions, packets, Moonbase map generation
  net_lobby.cpp  "Lobby"  — Backyard sports accounts/matchmaking
        │ consumes ONLY ↓
backends/networking/enet/        ~826-line ScummVM wrapper
  enet.h/host.h/socket.h         — ENet::createHost/connectToHost/createSocket,
        │                          Host::service/send, Socket::send/receive
backends/networking/enet/source/ vendored libenet (unix.cpp → UDP sockets)
```

- Session server: `multiplayer.scummvm.org:9120` (ENet/UDP), configurable via
  `Net::setSessionServer` / ConfMan.
- LAN discovery: UDP broadcast on `:9130` via the wrapper's `Socket`.
- Lobby: plain TCP `Networking::Socket` (`backends/networking/basic`).
- Emscripten currently hard-disables everything: `configure` sets `_enet=no`
  ("no sockets in the browser").
- Key fact: the engine never touches `ENet*` types — the 3-class wrapper is
  already the seam. It just leaks concrete types in its headers.

## Upstream server (multiplayer.scummvm.org)

Repo: `scummvm/scummvm-sites`, branch `multiplayer` (Dockerized, Redis-shared):

| Service | Tech | Role |
|---|---|---|
| Session server (`main.py`) | **Python + pyenet** (real ENet bindings) | game connects here on :9120 |
| Web (`web/main.py`, gunicorn) | Python | session listing |
| Lobby (`lobby/*.js`) | Node.js (TCP) | Backyard sports accounts/matchmaking |

The session server already embedding pyenet is the pivotal fact: a WS↔ENet
gateway is a *patch to upstream's own service*, not a new component.

## Recommended plan (phased)

**Phase 1 — harden the seam (upstreamable, zero behavior change).**
Make `Networking::ENet/Host/Socket` pure interfaces; vendored-enet impl
becomes the default backend. Engine code unchanged; native backends
byte-identical. Also give the Lobby's TCP `Networking::Socket` an interface
sibling.

**Phase 2 — emscripten transport = WebSocket relay (web↔web ships here).**
- `backends/networking/enet/emscripten/` implements the interfaces over a WS
  connection to a small room relay. Frames: `{peer, channel, reliable,
  payload}`; relay does room fanout.
- ENet semantics degrade gracefully over TCP-WS (everything reliable+ordered;
  fine for Moonbase lockstep, acceptable for Backyard sports).
- Peer "addresses" are opaque strings the engine round-trips → relay assigns
  virtual ones (`peer-N`); `getPeerIndexFromHost` keeps working.
- LAN broadcast → relay "list rooms" verb. Lobby TCP → WS endpoint on the
  same relay.
- **Asyncify discipline** (lesson from the SDL3 silence_callback crash, see
  scummvm commit c663ad7ab10): WS `onmessage` only appends to a JS-side ring
  buffer; wasm *pulls* during `Host::service()` — never dynCall into
  possibly-suspended wasm. `service(timeout)` = drain queue, else
  `emscripten_sleep`.
- Headless-testable in CI: two Playwright pages (host + join) + local relay —
  no canvas input needed, unlike UI tests.

**Phase 3 — cross-play pathway: relay = upstream session server + WS.**
Fork `scummvm-sites/multiplayer`, add a `websockets` listener beside the
pyenet one in `main.py`, bridge frames. To native peers and the session
infrastructure, a web player looks like a normal ENet peer → cross-play with
no native-side changes, and the patch is upstreamable to scummvm-sites (i.e.
multiplayer.scummvm.org itself could eventually serve web clients).

**Phase 4 (optional, latency-driven).** WebRTC DataChannels for web↔web
unreliable traffic behind the same interface; relay doubles as signaling.
Only if the sports games feel laggy over TCP-WS. (WebRTC-first was rejected:
native cross-play would require libdatachannel on the native side.)

## Rejected: emscripten POSIX-socket emulation

Building vendored enet against emscripten's UDP-over-WebSocket emulation
compiles but needs websockify-style bridging *per destination host:port*;
enet dials dynamic NAT'd peer addresses the bridge can't know. Brittle,
half-maintained. The configure comment already made the right call.

## Server hosting notes (our infra)

- PHP-à-la-scummvm-cloud fits only the request/response surface (room
  directory, join tokens). The realtime WS relay needs a persistent process —
  impossible on Hostinger shared hosting; PHP WS daemons (Ratchet/Swoole)
  would need a VPS anyway, losing the deployment advantage.
- Best fit: the Phase-3 Python relay as one container on the home docker
  host, exposed as `wss://relay.kuendig.io` through the existing cloudflared
  tunnel (TLS + firewall-friendly 443, no port forwarding, no new hosting).
- Upstream's Redis/web components can come along via their docker-compose if
  session listing is wanted.

## Effort sketch

| Phase | Scope | Rough size |
|---|---|---|
| 1 | interface extraction, native impl unchanged | days |
| 2 | emscripten transport + relay + 2-tab CI test | 1–2 weeks |
| 3 | WS listener in upstream session server (cross-play) | ~1 week |

Main risks: `Net`'s wait-loops under asyncify (poll `service(timeout)` —
same class of problem solved repeatedly in this port), and Moonbase's
`sendRawData`/direct-address paths needing the virtual-address mapping to be
watertight.
