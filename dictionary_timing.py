from random import shuffle
from timeit import timeit

letters = list('abcdefghijklmnopqrstuvwxyz')
mappy = dict((letter, 1) for letter in letters)
letters_copy = list(letters)
shuffle(letters_copy)

def get_each_key_from_map():
    for letter in letters_copy:
        mappy.get(letter)

def average(array):
    return float(sum(array)) / len(array)

def lazy_median(array):
    if not array:
        return None

    length = len(array)
    array = sorted(array)

    if length % 2:
        return array[length / 2]
    else:
        return (array[length / 2 - 1] + array[length / 2]) / 2.0


def main():
    warmup = [timeit(get_each_key_from_map, number=10**4) for i in xrange(100)]
    fast_times = [timeit(get_each_key_from_map, number=10**4) for i in xrange(100)]
    mappy.get(1)
    slow_times = [timeit(get_each_key_from_map, number=10**4) for i in xrange(100)]
    print 'warmup', '\t'*2, '"fast"', '\t'*2, '"slow"'
    print average(warmup), average(fast_times), average(slow_times)
    print lazy_median(warmup), lazy_median(fast_times), lazy_median(slow_times)

if __name__ == '__main__':
    main()
