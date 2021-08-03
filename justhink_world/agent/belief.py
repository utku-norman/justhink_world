import pomdp_py


def initialize_belief(prior={}, representation="histogram"):
    return pomdp_py.Histogram(prior)