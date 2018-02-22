class MethodError(Exception):
    def __init__(self):
        print('{0}: is not implemented'.format(__class__))


class InitError(Exception):
    def __init__(self):
        print("{0}: either '-i' or '-p' could be given, but not both".format(__class__))

