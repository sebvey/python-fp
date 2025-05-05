# Curry de python coroutine function
def xcurry2(cofunc):
    # on retourne une fonction qui prend 1 arg et qui retourne une cofunc
    def curried(first_arg):
        async def applied(*other_args):
            return await cofunc(first_arg, *other_args)

        return applied

    return curried
