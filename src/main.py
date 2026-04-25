from parser import parse_file

if __name__ == "__main__":
    nb_drones, zones, connections, start_zone, end_zone = parse_file("maps/medium/03_priority_puzzle.txt")
    print(f"\nReady to simulate {nb_drones} drones!")
