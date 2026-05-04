*This project has been created as part of the 42 curriculum by yaimghar.*

# Fly-In: Drone Network Routing Simulator

## Description

Fly-In is a drone routing simulation system that solves the challenge of coordinating multiple drones through a network of zones with various constraints. The project simulates turn-by-turn drone movements from a start hub to an end hub while respecting capacity limits, restricted zones, and connection constraints.

The goal is to route all drones to their destination in the minimum number of turns while handling:
- Zone capacity limits (max drones per zone)
- Connection capacity limits (max drones per link)
- Restricted zones (requiring 2 turns to traverse)
- Blocked zones (impassable)
- Priority zones (preferred routing)

The system includes a pathfinding algorithm to discover multiple diverse paths, a turn-by-turn simulator that handles conflicts and capacity constraints, and an optional pygame-based visualizer for real-time observation of drone movements.

## Instructions

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fly_in
```

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
```

3. Install dependencies:
```bash
make install
# or
pip install -r requirements.txt
```

### Running the Simulator

**Basic usage:**
```bash
python3 src/main.py <map_file>
# or
make run ARGS="<map_file>"
```

**Examples:**
```bash
python3 src/main.py maps/easy/01_linear_path.txt
python3 src/main.py maps/medium/01_dead_end_trap.txt
make run ARGS=test.txt
```

### Code Quality

Run linting and type checking:
```bash
make lint
```

Clean build artifacts:
```bash
make clean
```

## Map File Format

Maps are defined in text files with the following syntax:

```
nb_drones: <number>

start_hub: <name> <x> <y> [metadata]
hub: <name> <x> <y> [metadata]
end_hub: <name> <x> <y> [metadata]

connection: <zone1>-<zone2> [metadata]
```

**Metadata options:**
- Zones: `zone=<type>` (normal/restricted/priority/blocked), `max_drones=<n>`, `color=<name>`
- Connections: `max_link_capacity=<n>`

**Example:**
```
nb_drones: 3

start_hub: Start 0 0
hub: A 1 0 [zone=priority color=green]
hub: B 2 0 [zone=restricted max_drones=2]
end_hub: End 3 0 [color=red]

connection: Start-A [max_link_capacity=2]
connection: A-B
connection: B-End
```

## Algorithm Choices and Implementation Strategy

### Pathfinding Algorithm
The pathfinding system uses **Breadth-First Search (BFS)** with zone exclusion to discover multiple diverse paths:

1. **First Path Discovery**: Standard BFS finds the shortest path from start to end, prioritizing zones marked as "priority" type.

2. **Alternative Path Discovery**: For each middle zone in the first path, the algorithm attempts to find alternative routes by excluding that zone. This forces the pathfinder to explore different areas of the network.

3. **Path Distribution**: If fewer unique paths exist than drones, remaining drones are assigned paths using round-robin distribution to balance load across available routes.

**Why BFS?**
- Guarantees shortest path in unweighted graphs
- Simple and efficient for network traversal
- Easy to modify with zone exclusion for path diversity

**Zone Exclusion Strategy:**
The single-zone exclusion approach (excluding one zone at a time) was chosen over pair exclusion because:
- It's simpler and more efficient
- Testing showed it finds sufficient path diversity for all test cases
- Pair exclusion rarely discovered additional unique paths in practice

### Simulation Strategy

The simulator uses a **turn-by-turn coordination system** with conflict resolution:

1. **Transit Handling**: Drones in transit to restricted zones complete their movement first (restricted zones require 2 turns).

2. **Move Planning**: All drones determine their next desired move based on their assigned path.

3. **Conflict Resolution**: Moves are validated sequentially, checking:
   - Zone capacity: `current_occupancy < max_drones`
   - Connection capacity: `current_usage < max_link_capacity`
   - Drones in transit are excluded from zone occupancy counts

4. **Move Execution**: Valid moves are applied, with restricted zone movements entering transit state.

**Key Design Decisions:**

- **Sequential validation**: Moves are checked in order, with earlier drones having priority. This prevents deadlocks and ensures deterministic behavior.

- **In-transit tracking**: Drones moving to restricted zones are tracked separately to avoid double-counting in capacity calculations.

- **Capacity-aware routing**: The simulator respects both zone and connection capacity limits, allowing multiple drones to share paths when capacity allows.

### Data Structures

- **Graph representation**: Adjacency list via connections, enabling O(1) neighbor lookup
- **Path storage**: List of zone sequences, indexed by drone ID
- **Position tracking**: Dictionary mapping drones to current zones
- **Transit state**: Dictionary tracking drones in 2-turn restricted zone movements

## Visual Representation Features

### Terminal Output

The simulator provides color-coded terminal output using ANSI escape codes:

- **Zone colors**: Custom colors from map metadata (red, green, blue, yellow, etc.)
- **Movement notation**: 
  - `D1-A`: Drone 1 moves to zone A
  - `D1-A-B`: Drone 1 enters transit from A to B (restricted zone)
- **Turn counter**: Displays current turn and completion summary

### Pygame Visualizer

The optional visualizer enhances understanding through:

1. **Spatial Layout**: Zones positioned according to map coordinates, showing network topology

2. **Visual Elements**:
   - Zones: Circles colored by type or metadata
   - Connections: Lines between zones with capacity labels
   - Drones: Yellow circles with IDs, offset when multiple drones share a zone
   - Start/End: Green and red borders respectively

3. **Real-time Information**:
   - Zone occupancy: Shows current/max drones at each zone
   - Transit visualization: Drones in transit displayed between zones
   - Progress tracking: Turn counter and completion status

4. **Interactive Control**: Step-by-step turn advancement allows detailed observation of routing decisions

**User Experience Benefits**:
- Immediate visual feedback on capacity constraints
- Easy identification of bottlenecks and congestion
- Clear understanding of restricted zone 2-turn mechanics
- Spatial awareness of network structure and drone distribution

## Project Structure

```
fly_in/
├── src/
│   ├── main.py          # CLI entry point
│   ├── visualize.py     # Pygame visualizer entry point
│   ├── models.py        # Data structures (Zone, Connection, Drone, Graph)
│   ├── parser.py        # Map file parser
│   ├── pathfinder.py    # BFS pathfinding with zone exclusion
│   └── simulator.py     # Turn-by-turn simulation engine
├── maps/                # Test maps organized by difficulty
│   ├── easy/
│   ├── medium/
│   ├── hard/
│   └── challenger/
├── requirements.txt     # Python dependencies
├── Makefile            # Build and run commands
└── README.md           # This file
```

## Test Results

All test maps complete successfully with excellent performance:

| Difficulty | Map | Turns | Target | Status |
|------------|-----|-------|--------|--------|
| Easy | 01_linear_path | 4 | ≤6 | ✅ |
| Easy | 02_simple_fork | 5 | ≤6 | ✅ |
| Easy | 03_basic_capacity | 6 | ≤8 | ✅ |
| Medium | 01_dead_end_trap | 8 | ≤15 | ✅ |
| Medium | 02_circular_loop | 9 | ≤20 | ✅ |
| Medium | 03_priority_puzzle | 7 | ≤12 | ✅ |
| Hard | 01_maze_nightmare | 15 | ≤45 | ✅ |
| Hard | 02_capacity_hell | 18 | ≤60 | ✅ |
| Hard | 03_ultimate_challenge | 27 | - | ✅ |
| Challenger | 01_the_impossible_dream | 43 | - | ✅ |

## Resources

### Documentation and References

- **Python Official Documentation**: https://docs.python.org/3/
- **Pygame Documentation**: https://www.pygame.org/docs/
- **Graph Algorithms**: Introduction to Algorithms (CLRS), Chapter 22 - Elementary Graph Algorithms
- **BFS Pathfinding**: https://en.wikipedia.org/wiki/Breadth-first_search
- **ANSI Escape Codes**: https://en.wikipedia.org/wiki/ANSI_escape_code

### AI Usage

AI assistance (Amazon Q Developer) was used for the following tasks:

1. **Code Review and Debugging**:
   - Identifying and fixing mypy type checking errors
   - Debugging pathfinding logic and capacity constraint handling
   - Code quality improvements and refactoring suggestions

2. **Implementation Guidance**:
   - Algorithm design discussions (BFS vs alternatives, zone exclusion strategies)
   - Data structure recommendations for efficient lookups
   - Best practices for Python type hints and function signatures

3. **Documentation**:
   - README structure and formatting
   - Code comments and docstring improvements
   - Algorithm explanation and visualization descriptions

4. **Visualization Development**:
   - Pygame implementation patterns and best practices
   - ANSI color code reference and usage
   - Visual layout calculations and positioning logic

**Parts NOT created by AI**:
- Core algorithm logic and simulation strategy (designed independently)
- Map file format and parser implementation
- Test maps and validation scenarios
- Overall project architecture and design decisions

AI was used as a coding assistant and knowledge resource, but all critical design decisions, algorithm choices, and implementation strategies were made independently with AI providing implementation support and code quality feedback.

## Technical Choices

### Language and Tools

- **Python 3.13**: Chosen for readability, rapid development, and strong typing support
- **Type Hints**: Full type annotations for better code quality and IDE support
- **Pygame**: Optional dependency for visualization, not required for core functionality
- **Flake8 + Mypy**: Enforces code quality and type safety

### Design Patterns

- **Separation of Concerns**: Parser, pathfinder, and simulator are independent modules
- **Data-Driven Design**: Map files define network structure, allowing easy testing
- **Immutable Paths**: Once paths are found, they don't change during simulation
- **State Tracking**: Clear separation between drone positions and transit states

### Performance Considerations

- **BFS Complexity**: O(V + E) where V = zones, E = connections
- **Path Validation**: O(k) where k = number of drones
- **Turn Simulation**: O(k²) worst case for conflict checking
- **Overall**: Efficient for networks with hundreds of zones and dozens of drones

## License

This project is part of the 42 school curriculum and follows 42's academic policies.
