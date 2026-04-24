"""Parser for drone network input files."""

import sys
from models import Zone


def parse_file(filepath: str) -> None:
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
    start_zone = None
    end_zone = None

    line_number = 1
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

            # Parse name and coordinates
            tokens = main_part.split()
            if len(tokens) != 3:
                print(f"Error on line {line_number}: Invalid zone format, expected '<name> <x> <y>'")
                sys.exit(1)
            name = tokens[0]
            try:
                x = int(tokens[1])
                y = int(tokens[2])
            except ValueError:
                print(f"Error on line {line_number}: Coordinates must be integers")
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
                print(f"✓ Created start_hub: {name} at ({x}, {y})")
            elif zone_type == "end_hub":
                if end_zone is not None:
                    print(f"Error on line {line_number}: Multiple end_hub definitions found")
                    sys.exit(1)
                end_zone = zone
                print(f"✓ Created end_hub: {name} at ({x}, {y})")
            else:
                print(f"✓ Created hub: {name} at ({x}, {y})")

        else:
            # TODO: Parse zones and connections
            print(f"Line {line_number}: {line}")

        line_number += 1
    # Validate we have start and end
    if start_zone is None:
        print("Error: No start_hub defined")
        sys.exit(1)
    if end_zone is None:
        print("Error: No end_hub defined")
        sys.exit(1)

    print(f"\n✓ Total zones parsed: {len(zones)}")
    print(f"✓ Start: {start_zone.name}")
    print(f"✓ End: {end_zone.name}")
