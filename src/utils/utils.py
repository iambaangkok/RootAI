def perform(function: any, *args):
    return lambda: function(*args)
