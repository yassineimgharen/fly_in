"""Parser for drone network input files."""

import sys
from models import Zone, Connection


def parse_file(filepath: str) -> tuple[int, list[Zone], list[Connection], Zone, Zone]:
    """
    Parse the input file and create the network.

    Args:
        filepath: Path to the input file

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If parsing fails
    """
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Error: Cannot find file '{filepath}'")
        print("Please check that the file exists and the path is correct.")
        sys.exit(1)

    nb_drones = 0
    first_line_parsed = False
    zones = []
    connections = []
    start_zone = None
    end_zone = None

    line_number = 1

    def find_zone_by_name(name: str):
        """Find a zone by its name."""
        for zone in zones:
            if zone.name == name:
                return zone
        return None

    for line in lines:
        line = line.strip()
        if line == "" or line.startswith('#'):
            line_number += 1
            continue

        # First non-comment line must be nb_drones
        if not first_line_parsed:
            if not line.startswith("nb_drones:"):
                print(f"Error on line {line_number}: First line must be 'nb_drones: <number>'")
                sys.exit(1)

            parts = line.split(":")
            if len(parts) != 2:
                print(f"Error on line {line_number}: Invalid format for nb_drones")
                sys.exit(1)

            number_str = parts[1].strip()

            # Convert to integer
            try:
                nb_drones = int(number_str)
            except ValueError:
                print(f"Error on line {line_number}: Invalid number '{number_str}' for nb_drones")
                sys.exit(1)
            if nb_drones <= 0:
                print(f"Error on line {line_number}: nb_drones must be a positive integer, got {nb_drones}")
                sys.exit(1)

            print(f"✓ Parsed nb_drones: {nb_drones}")
            first_line_parsed = True

        elif line.startswith("start_hub:") or line.startswith("end_hub:") or line.startswith("hub:"):
            parts = line.split(":", 1)
            zone_type = parts[0]
            rest = parts[1].strip()

            # Step 3: Check if metadata exists
            if "[" in rest:
                main_part, metadata_part = rest.split("[", 1)

                main_part = main_part.strip()
                metadata_part = metadata_part.rstrip("]")
            else:
                main_part = rest
                metadata_part = None

            # Parse metadata
            zone_type_attr = "normal"
            color = None
            max_drones = 1
            if metadata_part is not None:
                tokens = metadata_part.split()
                for token in tokens:
                    if "=" not in token:
                        print(f"Error on line {line_number}: Invalid metadata format '{token}'")
                        sys.exit(1)
                    key, value = token.split("=", 1)
                    if key == "zone":
                        zone_type_attr = value
                    elif key == "color":
                        color = value
                    elif key == "max_drones":
                        try:
                            max_drones = int(value)
                        except ValueError:
                            print(f"Error on line {line_number}: max_drones must be an integer, got '{value}'")
                            sys.exit(1)
                        if max_drones <= 0:
                            print(f"Error on line {line_number}: max_drones must be positive, got {max_drones}")
                            sys.exit(1)

            # parse zone type, (must be valid)
            valid_types = ["normal", "blocked", "restricted", "priority"]
            if zone_type_attr not in valid_types:
                print(f"Error on line {line_number}: Invalid zone type '{zone_type_attr}'")
                sys.exit(1)

            # Parse name and coordinates
            tokens = main_part.split()
            if len(tokens) != 3:
                print(f"Error on line {line_number}: Invalid zone format, expected '<name> <x> <y>'")
                sys.exit(1)
            name = tokens[0]
            # ADD HERE - validate name has no dashes
            if "-" in name:
                print(f"Error on line {line_number}: Zone name '{name}' cannot contain dashes")
                sys.exit(1)
            try:
                x = int(tokens[1])
                y = int(tokens[2])
            except ValueError:
                print(f"Error on line {line_number}: Coordinates must be integers")
                sys.exit(1)

            # check for duplicate zone name
            if find_zone_by_name(name) is not None:
                print(f"Error on line {line_number}: Zone '{name}' already defined")
                sys.exit(1)
            # create Zone obj
            zone = Zone(name, x, y, zone_type_attr, max_drones, color)
            zones.append(zone)

            # Track start and end zones
            if zone_type == "start_hub":
                if start_zone is not None:
                    print(f"Error on line {line_number}: Multiple start_hub definitions found")
                    sys.exit(1)
                start_zone = zone

            elif zone_type == "end_hub":
                if end_zone is not None:
                    print(f"Error on line {line_number}: Multiple end_hub definitions found")
                    sys.exit(1)
                end_zone = zone


        else:
            # Parse connections
            if line.startswith("connection:"):
                # Split by ":"
                parts = line.split(":", 1)
                rest = parts[1].strip()

                # Check for metadata
                if "[" in rest:
                    main_part, metadata_part = rest.split("[", 1)
                    main_part = main_part.strip()
                    metadata_part = metadata_part.rstrip("]")
                else:
                    main_part = rest
                    metadata_part = None

                # Split zone names by "-"
                zone_names = main_part.split("-")

                # Find Zone objects by name
                name1 = zone_names[0]
                name2 = zone_names[1]

                zone1 = find_zone_by_name(name1)
                zone2 = find_zone_by_name(name2)
                # Validate zones exist
                if zone1 is None:
                    print(f"Error on line {line_number}: Unknown zone '{name1}'")
                    sys.exit(1)
                if zone2 is None:
                    print(f"Error on line {line_number}: Unknown zone '{name2}'")
                    sys.exit(1)

                # Check for duplicate connections
                for existing in connections:
                    if existing.connects(zone1, zone2):
                        print(f"Error on line {line_number}: Duplicate connection '{name1}-{name2}'")
                        sys.exit(1)

                # Parse max_link_capacity from metadata
                max_link_capacity = 1

                if metadata_part is not None:
                    tokens = metadata_part.split()
                    for token in tokens:
                        if "=" not in token:
                            print(f"Error on line {line_number}: Invalid metadata format '{token}'")
                            sys.exit(1)
                        key, value = token.split("=", 1)
                        if key == "max_link_capacity":
                            try:
                                max_link_capacity = int(value)
                            except ValueError:
                                print(f"Error on line {line_number}: max_link_capacity must be an integer")
                                sys.exit(1)
                            if max_link_capacity <= 0:
                                print(f"Error on line {line_number}: max_link_capacity must be positive")
                                sys.exit(1)

                # Create Connection object
                connection = Connection(zone1, zone2, max_link_capacity)
                connections.append(connection)

            else:
                print(f"Line {line_number}: Unknown line format: {line}")

        line_number += 1
    # Validate we have start and end
    if start_zone is None:
        print("Error: No start_hub defined")
        sys.exit(1)
    if end_zone is None:
        print("Error: No end_hub defined")
        sys.exit(1)

    return nb_drones, zones, connections, start_zone, end_zone
