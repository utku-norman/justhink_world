import pomdp_py

from ..agent.agent import HumanAgent  # , RobotAgent


class Action(pomdp_py.Action):
    def __init__(self, name, agent):
        self.name = name
        self.agent = agent

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Action):
            return self.name == other.name \
                and self.agent == other.agent
        elif type(other) == str:
            return self.name == other

    def __str__(self):
        return self.name

    def __repr__(self):
        # return "Action(%s)" % self.name
        return 'Action({},{})'.format(self.name, self.agent.name)


# NullAction = Action(name='no-op', agent=HumanAgent)

class SetStateAction(Action):
    def __init__(self, state, agent=HumanAgent):
        self.state = state
        super().__init__('set-state({})'.format(
            state), agent)


class SuggestPickAction(Action):
    def __init__(self, edge, agent=HumanAgent):
        self.edge = edge
        super().__init__('suggest-pick({},{})'.format(
            self.edge[0], self.edge[1]), agent)


class PickAction(Action):
    def __init__(self, edge, agent=HumanAgent):
        # self.edge = tuple(list(edge))
        self.edge = edge
        super().__init__('pick({},{})'.format(
            self.edge[0], self.edge[1]), agent)


class UnpickAction(Action):
    def __init__(self, edge, agent=HumanAgent):  # , quality='sub-optimal'):
        # self.edge = tuple(sorted(edge))
        # self.edge = tuple(list(edge))
        self.edge = edge
        # self.quality = quality
        super().__init__('unpick({},{})'.format(
            self.edge[0], self.edge[1]), agent)


class AgreeAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('agree', agent)


class DisagreeAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('disagree', agent)


class ClearAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('clear', agent)


# class SuggestSubmitAction(Action):
#     def __init__(self, agent=HumanAgent):
#         super().__init__('suggest-submit', agent)


class SubmitAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('submit', agent)


class AttemptSubmitAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('attempt-submit', agent)


class ContinueAction(Action):
    def __init__(self, agent=HumanAgent):
        super().__init__('continue', agent)


# class ClearSuggestSubmitAction(Action):
#     def __init__(self, agent=HumanAgent):
#         super().__init__('clear-suggest-submit', agent)
