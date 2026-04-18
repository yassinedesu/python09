#!/usr/bin/env python3
"""
Exercise 1: Alien Contact Log Validation
Demonstrates custom Pydantic validation using @model_validator for complex
business rules that span multiple fields simultaneously.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ValidationError, model_validator


class ContactType(Enum):
    """
    Enumeration of recognised alien contact categories.

    Using an Enum forces callers to pick an exact value from a fixed set,
    preventing typos like "Radio" or "RADIO" from slipping through.
    """

    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    """
    Pydantic model representing a single alien contact report.

    Field-level constraints handle basic range/length checks.
    The @model_validator handles cross-field business rules.
    """

    contact_id: str = Field(..., min_length=5, max_length=15)
    timestamp: datetime = Field(...)
    location: str = Field(..., min_length=3, max_length=100)
    contact_type: ContactType = Field(...)
    signal_strength: float = Field(..., ge=0.0, le=10.0)
    duration_minutes: int = Field(..., ge=1, le=1440)
    witness_count: int = Field(..., ge=1, le=100)
    message_received: Optional[str] = Field(default=None, max_length=500)
    is_verified: bool = Field(default=False)

    @model_validator(mode="after")
    def apply_business_rules(self) -> "AlienContact":
        """
        Enforce cross-field validation rules after all individual fields pass.

        Rules:
        1. contact_id must start with "AC".
        2. Physical contacts must be verified.
        3. Telepathic contacts require at least 3 witnesses.
        4. Strong signals (> 7.0) must include a received message.

        Returns
        -------
        AlienContact
            The validated instance.

        Raises
        ------
        ValueError
            If any business rule is violated.
        """
        if not self.contact_id.startswith("AC"):
            raise ValueError("Contact ID must start with 'AC' (Alien Contact)")

        if self.contact_type == ContactType.PHYSICAL and not self.is_verified:
            raise ValueError("Physical contact reports must be verified")
        condition = ContactType.TELEPATHIC and self.witness_count < 3
        if self.contact_type == condition:
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses")

        if self.signal_strength > 7.0 and self.message_received is None:
            raise ValueError(
                "Strong signal (> 7.0) should include a received message"
            )

        return self


def display_contact(contact: AlienContact) -> None:
    """
    Print formatted information about an alien contact report.

    Parameters
    ----------
    contact : AlienContact
        The validated contact instance to display.

    Returns
    -------
    None
    """
    print(f"ID: {contact.contact_id}")
    print(f"Type: {contact.contact_type.value}")
    print(f"Location: {contact.location}")
    print(f"Signal: {contact.signal_strength}/10")
    print(f"Duration: {contact.duration_minutes} minutes")
    print(f"Witnesses: {contact.witness_count}")
    if contact.message_received:
        print(f"Message: '{contact.message_received}'")


def main() -> None:
    """
    Demonstrate AlienContact validation with valid and invalid reports.

    Returns
    -------
    None
    """
    print("Alien Contact Log Validation")
    print("=" * 38)

    valid_contact: AlienContact = AlienContact(
        contact_id="AC_2024_001",
        timestamp="2024-01-15T14:30:00",  # type: ignore[arg-type]
        location="Area 51, Nevada",
        contact_type=ContactType.RADIO,
        signal_strength=8.5,
        duration_minutes=45,
        witness_count=5,
        message_received="Greetings from Zeta Reticuli",
        is_verified=False,
    )

    print("Valid contact report:")
    display_contact(valid_contact)
    print("=" * 38)

    print("Expected validation error:")
    try:
        AlienContact(
            contact_id="AC_2024_002",
            timestamp="2024-01-16T09:15:00",  # type: ignore[arg-type]
            location="Roswell, New Mexico",
            contact_type=ContactType.TELEPATHIC,
            signal_strength=6.2,
            duration_minutes=30,
            witness_count=1,
            is_verified=False,
        )
    except ValidationError as error:
        first_error_message: str = error.errors()[0]["msg"]
        clean_message: str = first_error_message.replace("Value error, ", "")
        print(clean_message)


if __name__ == "__main__":
    main()
