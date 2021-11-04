import pomdp_py


def initialize_belief(prior={}, representation="histogram"):
    return pomdp_py.Histogram(prior)

    # # Update agent belief
    # current_mpe_state = agent.cur_belief.mpe()
    # next_robot_position = agent.transition_model.sample(
    #     current_mpe_state, real_action).robot_position

    # next_state_space = set({})
    # for state in agent.cur_belief:
    #     next_state = copy.deepcopy(state)
    #     next_state.robot_position = next_robot_position
    #     next_state_space.add(next_state)

    # new_belief = pomdp_py.update_histogram_belief(
    #     agent.cur_belief, real_action, real_observation,
    #     agent.observation_model, agent.transition_model,
    #     next_state_space=next_state_space)

    # agent.set_belief(new_belief)
