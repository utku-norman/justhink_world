import pomdp_py

from ..agent.agent import Agent, HumanAgent
from .state import EnvironmentState


class Action(pomdp_py.Action):
    """A base class to represent actions in JUSThink world.

    The proper actions should subclass this.

    Attributes:
        name (str):
            the string representation of the action built by
            the inheriting/actual action class
        agent (Agent):
            the agent of the action, as the class itself
            i.e. agent = HumanAgent rather than agent = HumanAgent()
    """

    def __init__(self, name, agent):
        assert isinstance(name, str)
        assert issubclass(agent, Agent)

        self.name = name
        self.agent = agent

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        """"Check if two actions are equivalent.

        They are the same if their string representations,
        agents and types are equal.
        """
        return isinstance(other, Action) \
            and self.name == other.name \
            and self.agent == other.agent

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'Action({},{})'.format(self.name, self.agent.name)


class SetStateAction(Action):
    """TODO

    Attributes:
        state (EnvironmentState):
            the state that he action will set the environment
        agent (Agent, optional):
            the agent of the action (default HumanAgent)
    """

    def __init__(self, state, agent=HumanAgent):
        assert isinstance(state, EnvironmentState)
        assert issubclass(agent, Agent)

        self.state = state

        name = 'set-state({})'.format(state)

        super().__init__(name, agent)


class SetPauseAction(Action):
    def __init__(self, is_paused, agent=HumanAgent):
        assert isinstance(is_paused, bool)

        self.is_paused = is_paused

        name = 'set-paused({})'.format(is_paused)

        super().__init__(name, agent)


class SuggestPickAction(Action):
    def __init__(self, edge, agent=HumanAgent):
        self.edge = edge

        name = 'suggest-pick({},{})'.format(self.edge[0], self.edge[1])

        super().__init__(name, agent)


class PickAction(Action):
    def __init__(self, edge, agent=HumanAgent):
        self.edge = edge

        name = 'pick({},{})'.format(self.edge[0], self.edge[1])

        super().__init__(name, agent)


class UnpickAction(Action):
    def __init__(self, edge, agent=HumanAgent):
        self.edge = edge

        name = 'unpick({},{})'.format(self.edge[0], self.edge[1])

        super().__init__(name, agent)


class AgreeAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('agree', agent)


class DisagreeAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('disagree', agent)


class ClearAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('clear', agent)


class AttemptSubmitAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('attempt-submit', agent)


class ContinueAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('continue', agent)


class SubmitAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('submit', agent)
