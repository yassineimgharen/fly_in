"""Data models for the drone routing system."""

from typing import Optional


class Zone:
    """Represents a zone (hub) in the drone network."""

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        max_drones: int = 1,
        color: Optional[str] = None
    ) -> None:
        """
        Initialize a Zone.

        Args:
            name: Unique name of the zone
            x: X coordinate
            y: Y coordinate
            zone_type: Type of zone (normal, restricted, priority, blocked)
            max_drones: Maximum number of drones allowed simultaneously
            color: Optional color for visualization
        """
        self.name = name
        self.x = x
        self.y = y
        self.zone_type = zone_type
        self.max_drones = max_drones
        self.color = color

    # @property makes cost look like data but act like a function.
    @property
    def cost(self) -> int:
        """
        Get the movement cost to enter this zone.

        Returns:
            Number of turns required to enter this zone
        """
        if self.zone_type == "restricted":
            return 2
        elif self.zone_type == "blocked":
            return -1
        else:
            return 1

    def is_blocked(self) -> bool:
        """
        Check if this zone is blocked.

        Returns:
            True if zone is blocked, False otherwise
        """
        return self.zone_type == "blocked"

    def __str__(self) -> str:
        """Human-readable string representation."""
        return self.name


class Connection:
    """Represents a bidirectional connection between two zones."""

    def __init__(
        self,
        zone1: Zone,
        zone2: Zone,
        max_link_capacity: int = 1
    ) -> None:
        """
        Initialize a Connection.

        Args:
            zone1: First zone
            zone2: Second zone
            max_link_capacity: Maximum drones that can traverse simultaneously
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = max_link_capacity

    def connects(self, zone_a: Zone, zone_b: Zone) -> bool:
        """
        Check if this connection links two specific zones.

        Args:
            zone_a: First zone to check
            zone_b: Second zone to check

        Returns:
            True if this connection links zone_a and zone_b (in either order)
        """
        return (
            (self.zone1 == zone_a and self.zone2 == zone_b) or
            (self.zone1 == zone_b and self.zone2 == zone_a)
        )

    def get_other_zone(self, zone: Zone) -> Zone:
        """
        Get the zone on the other end of this connection.

        Args:
            zone: The zone we're currently at

        Returns:
            The zone on the other end

        Raises:
            ValueError: If the given zone is not part of this connection
        """
        if self.zone1 == zone:
            return self.zone2
        elif self.zone2 == zone:
            return self.zone1
        else:
            raise ValueError(f"Zone {zone.name} is not part of this connection")


class Drone:
    """Represents a drone that moves through the network."""

    def __init__(self, drone_id: int) -> None:
        """
        Initialize a Drone.

        Args:
            drone_id: Unique identifier for this drone
        """
        self.id = drone_id
