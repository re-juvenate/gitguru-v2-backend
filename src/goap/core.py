import asyncio
import heapq
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


    def async_precondition(self, key):
        def decorator(condition):
            async def checked_condition(state: State):
                result = await condition(state[key])
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

    def async_affects(self, key):
        def decorator(function):
            async def effect(state):
                result = await function(state[key])
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

    async def atest(self, state: State):
        mutation = state.substate()
        if self.will_run_given(mutation):
            effects = filter(asyncio.iscoroutine, self.effects)
            _ = asyncio.gather(*[effect(mutation) for effect in effects])
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
            self.distance_metrics[key] = lambda x, y: 1
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

    def plan(self, current_state: State, goals: list[Goal], actions: list[Action]) -> list[Action]:
        """
        Returns a sequence of actions that transforms current_state into a state
        that satisfies one of the goals. This implementation uses an A* search algorithm.
        """
        # If no goals, nothing to plan
        if not goals:
            return []

        # For simplicity, pick the first unsatisfied goal.
        target_goal = None
        for goal in goals:
            if not goal.evaluate(current_state):
                target_goal = goal
                break

        # If all goals are already satisfied
        if target_goal is None:
            return []

        # Each entry in the open set is a tuple (f, g, state, plan)
        # f = total estimated cost, g = cost so far, state = current state, plan = actions taken.
        open_set = []
        closed_set = set()

        # Start node
        start_state = current_state.substate()
        start_h = target_goal.goal_distance(start_state)
        start_node = (start_h, 0, start_state, [])
        heapq.heappush(open_set, start_node)

        while open_set:
            f, g, state, plan = heapq.heappop(open_set)

            # Use a tuple of sorted items as a hashable state representation.
            state_key = tuple(sorted(state.items()))
            if state_key in closed_set:
                continue
            closed_set.add(state_key)

            # Check if the goal is met
            if target_goal.evaluate(state):
                return plan

            # Expand all applicable actions
            for action in actions:
                if action.will_run_given(state):
                    # Simulate the action on a deep copy to avoid side effects.
                    new_state = action.test(state)  # action.__call__ applies its effects
                    new_plan = plan + [action]
                    new_g = g + 1  # Assuming uniform cost of 1 per action
                    new_h = target_goal.goal_distance(new_state)
                    new_f = new_g + new_h

                    new_state_key = tuple(sorted(new_state.items()))
                    if new_state_key in closed_set:
                        continue

                    heapq.heappush(open_set, (new_f, new_g, new_state, new_plan))
                    
        return []


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
            for action in actions:
                print("Plan:", action.name)
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

    # Define some actions
    action1 = agent.action("Action 1")

    @action1.precondition("value")
    def precondition_value_greater_than_5(value):
        return value > 5

    @action1.affects("value")
    def effect_increment_value(value):
        return value + 3
    
    action2 = agent.action("Action 2")

    @action2.precondition("value")
    def precondition_value_less_than_50(value):
        return value < 50

    @action2.affects("value")
    def effect_decrement_value(value):
        return value - 2


    # Define a goal
    goal = Goal("Goal 1", value=10)
    goal.set_metric("value", lambda x, y: abs(x - y))

    # Add goal to agent
    agent.goals.append(goal)

    # Set initial state
    agent.state.value = 6
    # Run the agent
    print("Initial state:", agent.state)
    agent.run()
    agent.run()
    print("Final state:", agent.state)

