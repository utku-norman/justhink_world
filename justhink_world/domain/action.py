import pomdp_py


class Action(pomdp_py.Action):
    def __init__(self, name, agent_name):
        self.name = name
        self.agent_name = agent_name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Action):
            return self.name == other.name \
                and self.agent_name == other.agent_name
        elif type(other) == str:
            return self.name == other

    def __str__(self):
        return self.name

    def __repr__(self):
        # return "Action(%s)" % self.name
        return 'Action({},{})'.format(self.name, self.agent_name)


NullAction = Action(name='no-op', agent_name='human')


class PickAction(Action):
    def __init__(self, edge, agent_name='human'):
        # self.edge = tuple(list(edge))
        self.edge = edge
        super().__init__('pick({},{})'.format(
            self.edge[0], self.edge[1]), agent_name)


class UnpickAction(Action):
    def __init__(self, edge, agent_name='human'):  # , quality='sub-optimal'):
        # self.edge = tuple(sorted(edge))
        # self.edge = tuple(list(edge))
        self.edge = edge
        # self.quality = quality
        super().__init__('unpick({},{})'.format(
            self.edge[0], self.edge[1]), agent_name)


class AgreeAction(Action):
    def __init__(self, agent_name='human'):
        super().__init__('agree', agent_name)


class ClearAction(Action):
    def __init__(self, agent_name='human'):
        super().__init__('clear', agent_name)


class DisagreeAction(Action):
    def __init__(self, agent_name='human'):
        super().__init__('disagree', agent_name)


class SubmitAction(Action):
    def __init__(self, agent_name='human'):
        super().__init__('submit', agent_name)


class SuggestPickAction(Action):
    def __init__(self, edge, agent_name='human'):
        self.edge = edge
        super().__init__('suggest-pick({},{})'.format(
            self.edge[0], self.edge[1]), agent_name)


class SuggestSubmitAction(Action):
    def __init__(self, agent_name='human'):
        super().__init__('suggest-submit', agent_name)


class ClearSuggestSubmitAction(Action):
    def __init__(self, agent_name='human'):
        super().__init__('clear-suggest-submit', agent_name)
