#!/usr/bin/env python3
"""
Exercise 0: Space Station Data Validation
Demonstrates basic Pydantic model creation with BaseModel and Field validation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ValidationError


class SpaceStation(BaseModel):
    """
    Pydantic model representing a monitored space station.

    Validates all incoming station telemetry before it enters the system,
    ensuring data integrity across the Cosmic Data Observatory network.
    """

    station_id: str = Field(
        ...,
        min_length=3,
        max_length=10,
        description="Unique station identifier code",
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Human-readable station name",
    )
    crew_size: int = Field(
        ...,
        ge=1,
        le=20,
        description="Number of crew members currently aboard",
    )
    power_level: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Current power level as a percentage",
    )
    oxygen_level: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Current oxygen level as a percentage",
    )
    last_maintenance: datetime = Field(
        ...,
        description="Date and time of the last maintenance check",
    )
    is_operational: bool = Field(
        default=True,
        description="Whether the station is currently operational",
    )
    notes: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Optional maintenance or status notes",
    )


def display_station(station: SpaceStation) -> None:
    """
    Print formatted information about a space station.

    Parameters
    ----------
    station : SpaceStation
        The validated space station instance to display.

    Returns
    -------
    None
    """
    status_label: str = "Operational" if station.is_operational else "Offline"
    print(f"ID: {station.station_id}")
    print(f"Name: {station.name}")
    print(f"Crew: {station.crew_size} people")
    print(f"Power: {station.power_level}%")
    print(f"Oxygen: {station.oxygen_level}%")
    print(f"Status: {status_label}")
    if station.notes:
        print(f"Notes: {station.notes}")


def main() -> None:
    """
    Demonstrate SpaceStation model validation with valid and invalid data.

    Creates one valid station to show successful parsing, then attempts
    to create an invalid station to show the validation error output.

    Returns
    -------
    None
    """
    print("Space Station Data Validation")
    print("=" * 40)

    valid_station: SpaceStation = SpaceStation(
        station_id="ISS001",
        name="International Space Station",
        crew_size=6,
        power_level=85.5,
        oxygen_level=92.3,
        last_maintenance="2024-01-15T10:30:00",  # type: ignore[arg-type]
        is_operational=True,
        notes="All systems nominal",
    )

    print("Valid station created:")
    display_station(valid_station)
    print("=" * 40)

    print("Expected validation error:")
    try:
        SpaceStation(
            station_id="BAD001",
            name="Overcrowded Station",
            crew_size=25,
            power_level=80.0,
            oxygen_level=90.0,
            last_maintenance="2024-01-15T10:30:00",  # type: ignore[arg-type]
        )
    except ValidationError as error:
        first_error_message: str = error.errors()[0]["msg"]
        print(first_error_message)


if __name__ == "__main__":
    main()
