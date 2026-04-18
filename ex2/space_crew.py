#!/usr/bin/env python3
"""
Exercise 2: Space Crew Management Validation
Demonstrates nested Pydantic models where a SpaceMission contains
a list of CrewMember objects, each individually validated.
"""

from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(Enum):
    """
    Enumeration of official crew ranks.
    """
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """
    Pydantic model representing a single crew member.
    Used as a nested type inside SpaceMission.crew.
    """
    member_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=2, max_length=50)
    rank: Rank = Field(...)
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(..., min_length=3, max_length=30)
    years_experience: int = Field(..., ge=0, le=50)
    is_active: bool = Field(default=True)


class SpaceMission(BaseModel):
    """
    Pydantic model for a complete space mission with its crew roster.
    Each crew member is validated as a CrewMember before mission-level
    rules are applied.
    """
    mission_id: str = Field(..., min_length=5, max_length=15)
    mission_name: str = Field(..., min_length=3, max_length=100)
    destination: str = Field(..., min_length=3, max_length=50)
    launch_date: datetime = Field(...)
    duration_days: int = Field(..., ge=1, le=3650)
    crew: List[CrewMember] = Field(..., min_length=1, max_length=12)
    mission_status: str = Field(default="planned")
    budget_millions: float = Field(..., ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def apply_safety_requirements(self) -> "SpaceMission":
        """
        Enforce mission safety rules after all field-level validation passes.

        Rules:
        1. mission_id must start with "M".
        2. At least one crew member must be Captain or Commander.
        3. Long missions (> 365 days) need 50% experienced crew (5+ years).
        4. All crew members must be on active duty.

        Returns
        -------
        SpaceMission
            The validated instance.

        Raises
        ------
        ValueError
            If any safety requirement is violated.
        """
        # Rule 1: mission ID prefix
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        # Rule 2: must have a senior commanding officer
        high_ranking_roles = {Rank.CAPTAIN, Rank.COMMANDER}
        has_senior_officer: bool = any(
            member.rank in high_ranking_roles for member in self.crew
        )
        if not has_senior_officer:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        # Rule 3: long missions need an experienced majority
        if self.duration_days > 365:
            experienced_count: int = sum(
                1 for member in self.crew if member.years_experience >= 5
            )
            required_count: int = len(self.crew) // 2
            if experienced_count < required_count:
                raise ValueError(
                    "Long missions (> 365 days) require at least 50% "
                    "of crew to have 5+ years of experience"
                )

        # Rule 4: all assigned crew must be active
        inactive_names: List[str] = [
            member.name for member in self.crew if not member.is_active
        ]
        if inactive_names:
            raise ValueError(
                f"Inactive crew members cannot be assigned: "
                f"{', '.join(inactive_names)}"
            )

        return self


def display_mission(mission: SpaceMission) -> None:
    """
    Print formatted details about a mission and its crew roster.

    Parameters
    ----------
    mission : SpaceMission
        The validated mission instance to display.

    Returns
    -------
    None
    """
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for member in mission.crew:
        print(
            f"  - {member.name} ({member.rank.value})"
            f" - {member.specialization}"
        )


def main() -> None:
    """
    Demonstrate SpaceMission nested model validation.

    Creates one valid long-duration mission, then triggers the
    missing-commander rule to show a validation error.

    Returns
    -------
    None
    """
    print("Space Mission Crew Validation")
    print("=" * 41)

    # Build crew members individually first
    commander_sarah: CrewMember = CrewMember(
        member_id="CM001",
        name="Sarah Connor",
        rank=Rank.COMMANDER,
        age=42,
        specialization="Mission Command",
        years_experience=18,
    )
    lieutenant_john: CrewMember = CrewMember(
        member_id="CM002",
        name="John Smith",
        rank=Rank.LIEUTENANT,
        age=35,
        specialization="Navigation",
        years_experience=10,
    )
    officer_alice: CrewMember = CrewMember(
        member_id="CM003",
        name="Alice Johnson",
        rank=Rank.OFFICER,
        age=29,
        specialization="Engineering",
        years_experience=6,
    )

    valid_mission: SpaceMission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date="2024-06-01T08:00:00",  # type: ignore[arg-type]
        duration_days=900,
        crew=[commander_sarah, lieutenant_john, officer_alice],
        budget_millions=2500.0,
    )

    print("Valid mission created:")
    display_mission(valid_mission)
    print("=" * 41)

    print("Expected validation error:")
    try:
        cadet_bob: CrewMember = CrewMember(
            member_id="CM010",
            name="Bob Lee",
            rank=Rank.CADET,
            age=22,
            specialization="Maintenance",
            years_experience=1,
        )
        SpaceMission(
            mission_id="M2024_FAIL",
            mission_name="Underprepared Expedition",
            destination="Moon",
            launch_date="2024-07-01T08:00:00",  # type: ignore[arg-type]
            duration_days=30,
            crew=[cadet_bob],  # No captain or commander
            budget_millions=100.0,
        )
    except ValidationError as error:
        first_error_message: str = error.errors()[0]["msg"]
        clean_message: str = first_error_message.replace("Value error, ", "")
        print(clean_message)


if __name__ == "__main__":
    main()
