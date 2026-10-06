from __future__ import annotations

import threading
import time

from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule

from src.model import DataModel
from src.rpc import RPCClient, RPCServer


class RPCTestMachine(RuleBasedStateMachine):
    def __init__(self) -> None:
        super().__init__()
        self.model = DataModel()
        self.server_model = DataModel()
        self.server = RPCServer(self.server_model)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.03)
        self.client = RPCClient()
        self.known_actor_keys: list[int] = []
        self.known_instruction_keys: list[int] = []
        self.known_response_keys: list[int] = []

    @rule(
        key=st.integers(min_value=0, max_value=10000),
        created=st.integers(min_value=0, max_value=2_000_000_000),
        ip=st.text(min_size=0, max_size=12),
        user_agent=st.text(min_size=0, max_size=20),
    )
    def create_actor_rule(self, key, created, ip, user_agent):
        if key in self.known_actor_keys:
            return
        expected = self.model.create_actor(key, created, ip, user_agent)
        actual = self.client.create_actor(key, created, ip, user_agent)
        assert tuple(actual) == expected
        self.known_actor_keys.append(key)

    @rule(key=st.integers(min_value=0, max_value=10000))
    def get_actors_rule(self, key):
        assert [tuple(x) for x in self.client.get_all_actors()] == self.model.get_all_actors()

    @rule(
        key=st.integers(min_value=0, max_value=10000),
        created=st.integers(min_value=0, max_value=2_000_000_000),
        ip=st.text(min_size=0, max_size=12),
        user_agent=st.text(min_size=0, max_size=20),
    )
    def update_actor_rule(self, key, created, ip, user_agent):
        if not self.known_actor_keys:
            return
        key = self.known_actor_keys[0]
        expected = self.model.update_actor(key, created, ip, user_agent)
        actual = self.client.update_actor(key, created, ip, user_agent)
        assert tuple(actual) == expected

    @rule(key=st.integers(min_value=0, max_value=10000))
    def delete_actor_rule(self, key):
        if not self.known_actor_keys:
            return
        key = self.known_actor_keys[0]
        expected = self.model.delete_actor(key)
        actual = self.client.delete_actor(key)
        assert tuple(actual) == expected
        self.known_actor_keys.remove(key)

    @rule(
        key=st.integers(min_value=0, max_value=10000),
        created=st.integers(min_value=0, max_value=2_000_000_000),
        content=st.text(max_size=20),
        actor=st.integers(min_value=0, max_value=10000),
        status=st.text(max_size=12),
    )
    def create_instruction_rule(self, key, created, content, actor, status):
        if key in self.known_instruction_keys:
            return
        expected = self.model.create_instruction(key, created, content, actor, status)
        actual = self.client.create_instruction(key, created, content, actor, status)
        assert tuple(actual) == expected
        self.known_instruction_keys.append(key)

    @rule(key=st.integers(min_value=0, max_value=10000))
    def get_instructions_rule(self, key):
        assert [tuple(x) for x in self.client.get_all_instructions()] == self.model.get_all_instructions()

    @rule(key=st.integers(min_value=0, max_value=10000))
    def delete_instruction_rule(self, key):
        if not self.known_instruction_keys:
            return
        key = self.known_instruction_keys[0]
        expected = self.model.delete_instruction(key)
        actual = self.client.delete_instruction(key)
        assert tuple(actual) == expected
        self.known_instruction_keys.remove(key)

    @rule(
        key=st.integers(min_value=0, max_value=10000),
        created=st.integers(min_value=0, max_value=2_000_000_000),
        content=st.text(max_size=20),
        actor=st.integers(min_value=0, max_value=10000),
        status=st.text(max_size=12),
    )
    def update_instruction_rule(self, key, created, content, actor, status):
        if not self.known_instruction_keys:
            return
        key = self.known_instruction_keys[0]
        expected = self.model.update_instruction(
            key, created, content, actor, status
        )
        actual = self.client.update_instruction(
            key, created, content, actor, status
        )
        assert tuple(actual) == expected

    @rule(
        key=st.integers(min_value=0, max_value=10000),
        created=st.integers(min_value=0, max_value=2_000_000_000),
        output=st.text(max_size=20),
        status=st.text(max_size=12),
        failure=st.text(max_size=12),
        instruction=st.integers(min_value=0, max_value=10000),
    )
    def create_response_rule(self, key, created, output, status, failure, instruction):
        if key in self.known_response_keys:
            return
        expected = self.model.create_response(key, created, output, status, failure, instruction)
        actual = self.client.create_response(key, created, output, status, failure, instruction)
        assert tuple(actual) == expected
        self.known_response_keys.append(key)

    @rule(key=st.integers(min_value=0, max_value=10000))
    def get_responses_rule(self, key):
        assert [tuple(x) for x in self.client.get_all_responses()] == self.model.get_all_responses()

    @rule(key=st.integers(min_value=0, max_value=10000))
    def delete_response_rule(self, key):
        if not self.known_response_keys:
            return
        key = self.known_response_keys[0]
        expected = self.model.delete_response(key)
        actual = self.client.delete_response(key)
        assert tuple(actual) == expected
        self.known_response_keys.remove(key)

    @rule(
        key=st.integers(min_value=0, max_value=10000),
        created=st.integers(min_value=0, max_value=2_000_000_000),
        output=st.text(max_size=20),
        status=st.text(max_size=12),
        failure=st.text(max_size=12),
        instruction=st.integers(min_value=0, max_value=10000),
    )
    def update_response_rule(
        self,
        key,
        created,
        output,
        status,
        failure,
        instruction,
    ):
        if not self.known_response_keys:
            return
        key = self.known_response_keys[0]
        expected = self.model.update_response(
            key,
            created,
            output,
            status,
            failure,
            instruction,
        )
        actual = self.client.update_response(
            key,
            created,
            output,
            status,
            failure,
            instruction,
        )
        assert tuple(actual) == expected

    @rule(now=st.integers(min_value=0, max_value=2_000_000_000))
    def recent_rule(self, now):
        actual = [tuple(x) for x in self.client.select_recent_instructions(now)]
        assert actual == self.model.select_recent_instructions(now)

    @invariant()
    def state_matches(self):
        assert [tuple(x) for x in self.client.get_all_actors()] == self.model.get_all_actors()
        assert [tuple(x) for x in self.client.get_all_instructions()] == self.model.get_all_instructions()
        assert [tuple(x) for x in self.client.get_all_responses()] == self.model.get_all_responses()

    def teardown(self) -> None:
        self.server.stop()
        super().teardown()


TestRPCTestMachine = RPCTestMachine.TestCase
