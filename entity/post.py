from dataclasses import dataclass, field
from typing import List

@dataclass
class Post:
    id: int
    title: str
    duties: List[str] = field(default_factory=list)
