# Daily Project Engine

A disciplined daily engineering repository that adds practical, runnable improvements each day across:
- data structures and algorithms
- networking systems
- game systems
- mini CLI tools

## Day 1
- DSA: Implemented weighted graph + Dijkstra shortest path with path reconstruction.
- Networking: Built reliable UDP stop-and-wait transport using sequence numbers, ACKs, checksum verification, and retry logic.
- Game Feature: Added player movement with acceleration/friction and robust tile-based collision resolution.
- Mini Tool: Added a CLI file organizer with category sorting, dry-run mode, manifest output, and undo workflow.

## Day 2
- DSA: Implemented A* pathfinding on a weighted grid with obstacle support and terrain cost handling.
- Networking: Upgraded to reliable UDP Go-Back-N sliding window with cumulative ACK processing, retransmission strategy, and FIN handshake.
- Game Feature: Expanded movement into platform physics (gravity, jump, grounded state) and added projectile-to-enemy combat interactions.
- Mini Tool: Added a daily workflow automation CLI for next-task planning, day validation, commit message generation, and optional auto-commit.

## Run Day 1 Modules
```bash
python days/day1/data_structures.py
python days/day1/game_features.py
python days/day1/networking.py server --port 9000
python days/day1/networking.py client --port 9000 --messages hello world
python days/day1/mini_tools.py run --base . --dry-run
python days/day2/data_structures.py
python days/day2/networking.py self-test --drop-rate 0.2
python days/day2/game_features.py
python days/day2/mini_tools.py next-plan --history task_history.json
```

## Day 3
- DSA: Segment tree with lazy propagation.
- Networking: Selective repeat reliability simulation with out-of-order buffering.
- Game Feature: Enemy finite-state machine with patrol/chase/attack transitions.
- Mini Tool: Incremental backup CLI using file-hash change detection.

## Day 4
- DSA: Union-Find + Kruskal minimum spanning tree.
- Networking: UDP heartbeat monitor with liveness detection and retry logic.
- Game Feature: Event-driven combat loop with cooldown system.
- Mini Tool: Structured log analyzer CLI for level/error aggregation.
