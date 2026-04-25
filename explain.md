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
Store all zones and connections
Store start and end zones
Find neighbors of a zone
Find connection between two zones