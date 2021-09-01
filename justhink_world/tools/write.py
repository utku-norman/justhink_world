class Bcolors:
    """# To use code like this, you can do something like:

    https://stackoverflow.com/a/287944

    # print(bcolors.WARNING + "Warning: Continue?" + bcolors.ENDC)
    # Or, with Python 3.6+:
    # print(f"{bcolors.WARNING}Warning:Continue?{bcolors.ENDC}")
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def fail(string):
        return f"{Bcolors.FAIL}" + string + f"{Bcolors.ENDC}"

    @staticmethod
    def warn(string):
        return f"{Bcolors.WARNING}" + string + f"{Bcolors.ENDC}"