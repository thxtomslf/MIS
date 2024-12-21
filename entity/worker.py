from dataclasses import dataclass

from entity.post import Post


@dataclass
class Worker:
    id: int
    full_name: str
    sex: str
    phone_number: str
    passport_number: str
    passport_series: str
    post: Post
    balance: float