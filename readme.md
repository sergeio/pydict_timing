# Pydict-timing

Reading the chapter on Python dictionaries in Oram and Wilson's *Beautiful
Code*, this caught my eye.

    [Dictionaries employ] a different trick: an individual dictionary uses a
    string-only function until a search for non-string data is requested, and
    then a more general function is used.

    ...

    (CPython trivia: this means that a dictionary with only string keys will
    become slightly slower if you issue d.get(1), even though the search can’t
    possibly succeed. All subsequent code in the program that refers to the
    dictionary will also go through the more general function and incur a
    slight slowdown.)

Neat! And testable!

## Let's try

```python
from timeit import timeit

mappy = {'a': 1}

def map_getter():
    return mappy.get('a')

def main():
    print timeit(map_getter, number=10**5)
    print timeit(map_getter, number=10**5)
    print timeit(map_getter, number=10**5)
    print timeit(map_getter, number=10**5)
    print timeit(map_getter, number=10**5)
    print timeit(map_getter, number=10**5)
    mappy.get(1)
    print 'And now it should be slow:'
    print timeit(map_getter, number=10**5)
    print timeit(map_getter, number=10**5)
    print timeit(map_getter, number=10**5)
    print timeit(map_getter, number=10**5)
    print timeit(map_getter, number=10**5)
    print timeit(map_getter, number=10**5)

if __name__ == '__main__':
    main()
```

Run it...

```bash
code/pydict_timing$ python dictionary_timing.py
0.0308029651642
0.0310020446777
0.0313718318939
0.0310368537903
0.031347990036
0.0306680202484
And now it should be slow:
0.0314359664917
0.0314090251923
0.0307240486145
0.0307958126068
0.0308310985565
0.0309820175171
```

Hmm.  Not exactly night and day.

OK. Maybe statistics can shed a light:

```python
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
    fast_times = [timeit(map_getter, number=10**5) for i in xrange(100)]
    mappy.get(1)
    slow_times = [timeit(map_getter, number=10**5) for i in xrange(100)]
    print '"fast"', '\t'*2, '"slow"'
    print average(fast_times), average(slow_times)
    print lazy_median(fast_times), lazy_median(slow_times)
```

```bash
code/pydict_timing$ python dictionary_timing.py
"fast"          "slow"
0.0336379671097 0.0334746313095
0.0336126089096 0.0333735942841
```

Hmmm.  Still very little difference, and contradictory to **Beautiful Code**'s
claim.

Maybe python or the OS is doing some sort of caching.  Or maybe it's something
to do with virtual memory.

Let's try warming up the memory by adding another category:

```python
def main():
    warmup = [timeit(map_getter, number=10**5) for i in xrange(100)]
    fast_times = [timeit(map_getter, number=10**5) for i in xrange(100)]
    mappy.get(1)
    slow_times = [timeit(map_getter, number=10**5) for i in xrange(100)]
    print 'warmup', '\t'*2, '"fast"', '\t'*2, '"slow"'
    print average(warmup), average(fast_times), average(slow_times)
    print lazy_median(warmup), lazy_median(fast_times), lazy_median(slow_times)
```

```bash
code/pydict_timing$ python dictionary_timing.py
warmup          "fast"          "slow"
0.0298159503937 0.0298064899445 0.0297101378441
0.029746055603 0.0297679901123 0.0296894311905
code/pydict_timing$ python dictionary_timing.py
warmup          "fast"          "slow"
0.0298805856705 0.0298972535133 0.0299680829048
0.0298104286194 0.0298410654068 0.0299055576324
```

That doesn't seem solve our problem (although the first retrieval from a
dictionary does seem to be slower as shown by this test:

```python
def main():
    for i in xrange(10):
        print timeit(map_getter, number=1)
```

Output:

```bash
4.05311584473e-06
3.09944152832e-06
2.86102294922e-06
2.86102294922e-06
3.09944152832e-06
2.86102294922e-06
2.86102294922e-06
2.86102294922e-06
2.86102294922e-06
3.09944152832e-06
```

## A (Slightly) More Realistic Scenario

Maybe the problem is that our dictionary is not very realistic.  Let's start
over:

If we change how we define our `mappy`, and update `main()` accordingly:

```python
from random import shuffle
from timeit import timeit

letters = list('abcdefghijklmnopqrstuvwxyz')
mappy = dict((letter, letters.index(letter)) for letter in letters)
letters_copy = list(letters)
shuffle(letters_copy)

...


def main():
    warmup = [timeit(get_each_key_from_map, number=10**4) for i in xrange(100)]
    fast_times = [timeit(get_each_key_from_map, number=10**4) for i in xrange(100)]
    mappy.get(1)
    slow_times = [timeit(get_each_key_from_map, number=10**4) for i in xrange(100)]
    print 'warmup', '\t'*2, '"fast"', '\t'*2, '"slow"'
    print average(warmup), average(fast_times), average(slow_times)
    print lazy_median(warmup), lazy_median(fast_times), lazy_median(slow_times)
```

We get this:

```bash
code/pydict_timing$ python dictionary_timing.py
warmup          "fast"          "slow"
0.0505058693886 0.050186882019 0.050145406723
0.0498259067535 0.0498830080032 0.0500988960266
code/pydict_timing$ python dictionary_timing.py
warmup          "fast"          "slow"
0.0518154883385 0.051748316288 0.051896750927
0.0517410039902 0.0516785383224 0.0518684387207
code/pydict_timing$ python dictionary_timing.py
warmup          "fast"          "slow"
0.0519949626923 0.0520069241524 0.0520055985451
0.0519568920135 0.0519568920135 0.0519590377808
```

Again, this is unsatisfying.  The average and median times have different
winners, and the margin of victory changes by orders of magnitude between runs.

I also tried making the keys decently long (20 chars), in case the shortness of
the keys was responsible for both key-comparator functions having
near-identical runtimes, but that did not make a difference either.

## Conclusion

I'm calling shenanigans.  In some cases, doing `get()`s on a string-keys-only
dictionary after doing a `.get(1)` will slow future `get()`s by .0025%

In other cases, they speed up.

In any case, it is insignificant and does not matter.


One modestly-useful discovery is that using the `.get()` syntax to access
dictionaries is 50% slower than using the bracket syntax.

```python
from timeit import timeit

mappy = {'a': 1, 'b': 2, 'c': 3, 'd': 4}

def bracket_getter():
    return mappy['a']

def dotget_getter():
    return mappy.get('a')

print 'brackets', timeit(bracket_getter, number=10**5)
print 'dotget', timeit(dotget_getter, number=10**5)
```

```bash
code/pydict_timing$ python dictionary_item_getting_timing.py
brackets 0.0194668769836
dotget 0.0307769775391
```
