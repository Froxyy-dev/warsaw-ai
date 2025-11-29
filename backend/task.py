from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Place:
    name: str
    phone: str


@dataclass
class Task:
    task_id: str
    notes_for_agent: str
    places: List[Place]


test_task = Task(
    task_id="test-001",
    notes_for_agent=(
        "Umawiasz wizytę dla użytkownika Mateusza. "
        "Numer telefonu Mateusza, jeśli będzie potrzebny do rejestracji, to: +48 886 859 039. "
        "Celem rozmowy jest umówienie wizyty u fryzjera na jutro o godzinie 18:00 na strzyżenie męskie. "
        "Jeśli jutro o 18:00 nie ma wolnych miejsc, spróbuj zaproponować najpierw 18:30, potem 17:30, "
        "a jeśli nadal się nie da, zapytaj o najbliższy możliwy termin w kolejnych dniach po 17:00. "
        "Jeśli salon poprosi o dodatkowe dane, podaj, że Mateusz woli krótkie, proste strzyżenie, bez skomplikowanych fryzur. "
        "Pod koniec rozmowy podsumuj ustalenia — dzień, godzinę i ewentualną cenę, jeśli ją poznasz."
    ),
    places=[
        Place(
            name="Studio metamorfozy",
            phone="+48886859039",
        )
    ],
)