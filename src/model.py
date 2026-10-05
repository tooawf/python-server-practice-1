"""In-memory data model for practical assignment variant 1."""

from __future__ import annotations

import time
from typing import Dict, List, Tuple

Actor = Tuple[int, int, str, str]
Instruction = Tuple[int, int, str, int, str]
Response = Tuple[int, int, str, str, str, int]


class DataModel:
    """Stores all records in memory as tuples."""

    def __init__(self) -> None:
        self.actors: List[Actor] = []
        self.instructions: List[Instruction] = []
        self.responses: List[Response] = []

    @staticmethod
    def _find_index(rows: list, key: int) -> int:
        for index, row in enumerate(rows):
            if row[0] == key:
                return index
        raise KeyError(f"Record with key={key} not found")

    @staticmethod
    def _ensure_unique(rows: list, key: int) -> None:
        if any(row[0] == key for row in rows):
            raise ValueError(f"Record with key={key} already exists")

    @staticmethod
    def _validate_key(key: int) -> None:
        if not isinstance(key, int) or isinstance(key, bool) or key < 0:
            raise ValueError("key must be a non-negative integer")

    @staticmethod
    def _validate_time(value: int) -> None:
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("time must be an integer")

    # Actor: key, time, ip, user_agent
    def create_actor(self, key: int, created: int, ip: str, user_agent: str) -> Actor:
        self._validate_key(key)
        self._validate_time(created)
        if not isinstance(ip, str) or not isinstance(user_agent, str):
            raise ValueError("ip and user_agent must be strings")
        self._ensure_unique(self.actors, key)
        row = (key, created, ip, user_agent)
        self.actors.append(row)
        return row

    def delete_actor(self, key: int) -> Actor:
        index = self._find_index(self.actors, key)
        return self.actors.pop(index)

    def get_all_actors(self) -> List[Actor]:
        return list(self.actors)

    def update_actor(self, key: int, created: int, ip: str, user_agent: str) -> Actor:
        index = self._find_index(self.actors, key)
        self._validate_time(created)
        if not isinstance(ip, str) or not isinstance(user_agent, str):
            raise ValueError("ip and user_agent must be strings")
        row = (key, created, ip, user_agent)
        self.actors[index] = row
        return row

    # Instruction: key, time, content, actor, status
    def create_instruction(
        self, key: int, created: int, content: str, actor: int, status: str
    ) -> Instruction:
        self._validate_key(key)
        self._validate_time(created)
        self._validate_key(actor)
        if not isinstance(content, str) or not isinstance(status, str):
            raise ValueError("content and status must be strings")
        self._ensure_unique(self.instructions, key)
        row = (key, created, content, actor, status)
        self.instructions.append(row)
        return row

    def delete_instruction(self, key: int) -> Instruction:
        index = self._find_index(self.instructions, key)
        return self.instructions.pop(index)

    def get_all_instructions(self) -> List[Instruction]:
        return list(self.instructions)

    def update_instruction(
        self, key: int, created: int, content: str, actor: int, status: str
    ) -> Instruction:
        index = self._find_index(self.instructions, key)
        self._validate_time(created)
        self._validate_key(actor)
        if not isinstance(content, str) or not isinstance(status, str):
            raise ValueError("content and status must be strings")
        row = (key, created, content, actor, status)
        self.instructions[index] = row
        return row

    # Response: key, time, output, status, failure, instruction
    def create_response(
        self,
        key: int,
        created: int,
        output: str,
        status: str,
        failure: str,
        instruction: int,
    ) -> Response:
        self._validate_key(key)
        self._validate_time(created)
        self._validate_key(instruction)
        if not all(isinstance(value, str) for value in (output, status, failure)):
            raise ValueError("output, status and failure must be strings")
        self._ensure_unique(self.responses, key)
        row = (key, created, output, status, failure, instruction)
        self.responses.append(row)
        return row

    def delete_response(self, key: int) -> Response:
        index = self._find_index(self.responses, key)
        return self.responses.pop(index)

    def get_all_responses(self) -> List[Response]:
        return list(self.responses)

    def update_response(
        self,
        key: int,
        created: int,
        output: str,
        status: str,
        failure: str,
        instruction: int,
    ) -> Response:
        index = self._find_index(self.responses, key)
        self._validate_time(created)
        self._validate_key(instruction)
        if not all(isinstance(value, str) for value in (output, status, failure)):
            raise ValueError("output, status and failure must be strings")
        row = (key, created, output, status, failure, instruction)
        self.responses[index] = row
        return row

    def select_recent_instructions(self, now: int | None = None) -> List[Tuple[str, str]]:
        """Implements π(user_agent, content)(σ(time >= now-5min)(Actor ⟕ Instruction))."""
        current = int(time.time()) if now is None else now
        actor_map: Dict[int, str] = {row[0]: row[3] for row in self.actors}
        result: List[Tuple[str, str]] = []
        for instruction in self.instructions:
            if instruction[1] < current - 300:
                continue
            user_agent = actor_map.get(instruction[3])
            if user_agent is not None:
                result.append((user_agent, instruction[2]))
        return result

    def snapshot(self) -> dict:
        return {
            "actors": self.get_all_actors(),
            "instructions": self.get_all_instructions(),
            "responses": self.get_all_responses(),
        }
