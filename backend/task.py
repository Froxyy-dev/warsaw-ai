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