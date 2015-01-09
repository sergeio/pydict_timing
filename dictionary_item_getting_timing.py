from timeit import timeit

mappy = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

def bracket_getter():
    return mappy['a']

def dotget_getter():
    return mappy.get('a')

print 'brackets', timeit(bracket_getter, number=10**5)
print 'dotget', timeit(dotget_getter, number=10**5)
