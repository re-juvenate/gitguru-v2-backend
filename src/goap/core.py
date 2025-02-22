import asyncio
from dis import disco
from functools import partial
from typing import Callable, Awaitable


class State(dict):
    def __init__(self, **state):
        super().__init__(state)

    def substate(self, *keys: str):
        if not keys:
            keys = tuple(self.keys())
        inner_substate = {
            key: self.get(key) for key in filter(lambda x: x in self, keys)
        }
        return State(**inner_substate)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__dict__[key]

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __delattr__(self, item):
        self.__delitem__(item)

    def __eq__(self, state):
        return state.items() == self.items()


class Action:
    def __init__(self, name: str):

        self.name = name
        self.preconditions = []
        self.effects = []

    def precondition(self, key):
        def decorator(condition):
            def checked_condition(state: State):
                result = condition(state[key])
                if not isinstance(result, bool):
                    raise ValueError("Condition must return a boolean.")
                return result

            self.preconditions.append(checked_condition)
            return checked_condition

        return decorator

    def affects(self, key):
        def decorator(function):
            def effect(state):
                result = function(state[key])
                if isinstance(result, type(state[key])):
                    state[key] = result

            self.effects.append(effect)
            return effect

        return decorator

    def will_run_given(self, state: State, qualifier: Callable[..., bool] = all):
        if self.preconditions == []:
            return True
        return qualifier([condition(state) for condition in self.preconditions])

    def test(self, state: State):
        mutation = state.substate()
        if self.will_run_given(mutation):
            for effect in self.effects:
                effect(mutation)
        return mutation

    def __call__(self, state: State):
        if self.will_run_given(state):
            for effect in self.effects:
                effect(state)


class Goal:
    def __init__(self, name: str, **kwargs):
        self.name = name
        self._final_state = State(**kwargs)
        self.distance_metrics = {}

    def set_metric(self, key, metric):
        self.distance_metrics[key] = metric
        return self

    def _metric(self, key):
        if key not in self.distance_metrics:
            self.distance_metrics[key] = lambda x, y: abs(x - y)
        return self.distance_metrics[key]

    def goal_distance(self, state: State):
        distance = 0
        for key, value in self._final_state.items():
            if state[key] != value:
                distance += self._metric(key)(state[key], value)
        return distance

    def evaluate(self, state: State):
        return state == self._final_state


class Planner:
    def __init__(self, name: str):
        self.name = name

    def plan(self, current_state: State, goals: list[Goal], actions: list[Action]):
        return actions


class Agent:
    def __init__(self, name: str, planner: Planner):
        self.name = name
        self._planner = planner
        self.actions = []
        self.goals = []

        self.state = State()

    def action(self, name: str):
        action = Action(name)
        self.actions.append(action)
        return action

    def _plan(self):
        return self._planner.plan(self.state, self.goals, self.actions)

    def run(self):
        while self.goals:
            actions = self._plan()
            print("Plan:", actions)
            for action in actions:
                action(self.state)
            for goal in self.goals:
                if goal.evaluate(self.state):
                    self.goals.remove(goal)

if __name__ == "__main__":
    # Test
    # Create a planner
    planner = Planner("Test Planner")

    # Create an agent with the planner
    agent = Agent("Test Agent", planner)
    agent.state.value = 6

    # Define some actions
    action1 = agent.action("Action 1")

    @action1.precondition("value")
    def precondition_value_greater_than_5(value):
        return value > 5

    @action1.affects("value")
    def effect_increment_value(value):
        return value + 1


    # Define a goal
    goal = Goal("Goal 1", value=10)
    goal.set_metric("value", lambda x, y: abs(x - y))

    # Add goal to agent
    agent.goals.append(goal)

    # Set initial state
    # Run the agent
    print("Initial state:", agent.state)
    agent.run()
    agent.run()
    print("Final state:", agent.state)

