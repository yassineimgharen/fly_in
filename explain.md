# map
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: tunnelB 7 4 [zone=normal color=red]
hub: obstacleX 5 5 [zone=blocked color=gray]
connection: hub-roof1
connection: hub-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [max_link_capacity=2]
connection: tunnelB-goal

# structure
fly_in/
├── Makefile (already exists, but empty)
├── README.md
├── requirements.txt
├── .gitignore
└── src/
    ├── __init__.py
    ├── main.py
    ├── parser.py
    ├── models.py
    ├── graph.py
    ├── pathfinder.py
    ├── simulator.py
    └── visualizer.py

# goal
-All drones start at the same place
-They all need to reach the same destination
-They move simultaneously (in parallel, not one-by-one)
-Zones have limited capacity (usually only 1 drone at a time)
-Some zones cost more "turns" to enter
-Goal: Get all drones to the end in the FEWEST total turns

# connection
Problem: Connection has zone1 and zone2, but you don't know which one is "the other side"
Why get_other_zone()
conn = Connection(hub, roof1)
other = conn.get_other_zone(hub)  # Returns roof1
other = conn.get_other_zone(roof1)  # Returns hub

# validate rules:
- First line is nb_drones
- Exactly 1 start_hub
- Exactly 1 end_hub
- Zone names are unique
- Zone names have no dashes or spaces
- Coordinates are integers
- Zone types are valid (normal/blocked/restricted/priority)
- Capacities are positive integers
- Connections reference existing zones
- No duplicate connections

# Graph
-> its a container that holds everything together:
Store all zones and connections
Store start and end zones
Find neighbors of a zone
Find connection between two zones

# algo
What is Pathfinding?
Pathfinding = Finding a route from point A to point B in a graph/network

Simple Example:
start → A → B → end

Question: How does a drone get from start to end?
Answer: start → A → B → end

That's pathfinding! Finding the sequence of zones to travel through.
Why is it Hard in This Project?

Problem 1: Multiple Paths Exist
        → A → B →
start →           → end
        → C →

Which path should drones use?
Path 1: start → A → B → end (3 steps)
Path 2: start → C → end (2 steps)
Answer: Depends on how many drones and capacity!


Problem 2: Capacity Limits
        → A (capacity=1) →
start →                    → end
        → C (capacity=1) →

With 4 drones:
Path 1 can only handle 1 drone at a time
Path 2 can only handle 1 drone at a time
You need to stagger the drones (send them one by one)



Problem 3: Zone Costs
        → A (restricted, cost=2) →
start →                            → end
        → C (normal, cost=1) →

Path via A costs more turns (restricted zone)
Path via C is faster
Pathfinder should prefer the faster path



Problem 4: Blocked Zones
        → A → BLOCKED → end
start →
        → C → end

Path via A is impossible (blocked zone)
Only path via C is valid
Pathfinder must avoid blocked zones

# pathfinder and simulator jobs
Pathfinder's job:
Find paths from start to end (BFS)
Return a list of possible paths
Respect blocked zones (never include them)

Pathfinder handles:
✅ Blocked zones → Never include them in any path
✅ Restricted zones → Include them but with cost=2 (they're valid, just expensive)
✅ Priority zones → Prefer them over normal zones (same cost=1 but prioritized)
✅ Path cost → Calculate total cost of each path


Simulator's job:
Take those paths
Assign drones to paths
Schedule movements turn by turn
Handle capacity conflicts and waiting
Produce the output

Simulator handles:

✅ Zone capacity (max_drones) → Don't put more drones than allowed in a zone
✅ Connection capacity (max_link_capacity) → Don't send more drones than allowed through a connection at the same turn
✅ Drone assignment → Decide which drone takes which path
✅ Turn scheduling → Move drones turn by turn simultaneously
✅ Waiting → If a zone is full, drone stays in place
✅ Restricted zone transit → Drone spends 2 turns (1 turn on connection, 1 turn arriving)
✅ Output format → Print D1-zone D2-zone per turn
✅ End condition → Stop when all drones reach end zone


# important
Pathfinder = GPS that finds routes
Simulator = Traffic controller that decides which car takes which route and when


Task	                     Pathfinder	      Simulator
Find routes	                ✅	        ❌
Skip blocked zones	        ✅	        ❌
Calculate path cost	        ✅	        ❌
Assign drones to paths	        ❌	        ✅
Check zone capacity	        ❌	        ✅
Check connection capacity	❌	        ✅
Move drones turn by turn	❌	        ✅
Print output	                ❌	        ✅

# important example
came_from tells you the "parent" of each zone:

start ← None
A     ← start
B     ← A
end   ← B

Follow backwards from end:
end → B → A → start

Reverse:
start → A → B → end ✅

#####
came_from = {
    start: None,
    A: start,
    B: A,
    end: B
}

# run func
First: Complete moves from drones that started traveling last turn
Then: Plan new moves for this turn
Finally: Execute new moves

