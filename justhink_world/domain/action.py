import pomdp_py

from ..agent.agent import Agent
# from justhink_world.agent.agent import Agent
from .state import EnvState


class Action(pomdp_py.Action):
    """A base class to represent actions in JUSThink world.

    The proper actions should subclass this.

    Attributes:
        name (str):
            the string representation of the action built by
            the inheriting/actual action class
        agent (Actor):
            the agent of the action, as the class itself
            i.e. agent = Agent.HUMAN rather than agent = Agent.HUMAN()
    """

    def __init__(self, name, agent):
        assert isinstance(name, str)
        # assert issubclass(agent, Actor)

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

    def __lt__(self, other):
        return str(self) < str(other)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'Action({},{})'.format(self.name, self.agent)


class ResetAction(Action):
    def __init__(self, agent=Agent.MANAGER):
        super().__init__('reset', agent)


class SetStateAction(Action):
    """TODO

    Attributes:
        state (EnvState):
            the state that he action will set the environment
        agent (Actor, optional):
            the agent of the action (default Agent.HUMAN)
    """

    def __init__(self, state, agent=Agent.MANAGER):
        assert isinstance(state, EnvState)
        # assert issubclass(agent, Actor)

        self.state = state

        name = 'set-state({})'.format(state)

        super().__init__(name, agent)


class SetPauseAction(Action):
    def __init__(self, is_paused, agent=Agent.HUMAN):
        assert isinstance(is_paused, bool)
        self.is_paused = is_paused
        name = 'set-paused({})'.format(is_paused)
        super().__init__(name, agent)


class SuggestPickAction(Action):
    def __init__(self, edge, agent=Agent.HUMAN):
        self.edge = edge
        name = 'suggest-pick({})'.format(format_edge(self.edge))
        super().__init__(name, agent)


class PickAction(Action):
    def __init__(self, edge, agent=Agent.HUMAN):
        self.edge = edge
        name = 'pick({})'.format(format_edge(self.edge))
        super().__init__(name, agent)

    # def __eq__(self, other):
    #     """"Check if two actions are equivalent."""
    #     u, v = self.edge
    #     uu, vv = other.edge
    #     return isinstance(other, PickAction) \
    #         and (((u == uu) and (v == vv)) or ((u == vv) and (v == uu))) \
    #         and self.agent == other.agent


class UnpickAction(Action):
    def __init__(self, edge, agent=Agent.HUMAN):
        self.edge = edge
        name = 'unpick({})'.format(format_edge(self.edge))
        super().__init__(name, agent)


class ObserveAction(Action):
    def __init__(self, agent=Agent.HUMAN):
        super().__init__('observe', agent)


class AgreeAction(Action):
    def __init__(self, agent=Agent.HUMAN):
        super().__init__('agree', agent)


class DisagreeAction(Action):
    def __init__(self, agent=Agent.HUMAN):
        super().__init__('disagree', agent)


class ClearAction(Action):
    def __init__(self, agent=Agent.HUMAN):
        super().__init__('clear', agent)


class AttemptSubmitAction(Action):
    def __init__(self, agent=Agent.HUMAN):
        super().__init__('attempt-submit', agent)


class ContinueAction(Action):
    def __init__(self, agent=Agent.HUMAN):
        super().__init__('continue', agent)


class SubmitAction(Action):
    def __init__(self, agent=Agent.HUMAN):
        super().__init__('submit', agent)


def format_edge(edge):
    try:
        s = (int(edge[0]), int(edge[1]))
    except Exception as e:
        print(e)
        s = (edge[0], edge[1])
    s = '{},{}'.format(s[0], s[1])

    return s
