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