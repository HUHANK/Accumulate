#-------------------------A--------------------------
#Here's a memoizing class.
import collections
import functools

class memoized(object):
   '''Decorator. Caches a function's return value each time it is called.
   If called later with the same arguments, the cached value is returned
   (not reevaluated).
   '''
   def __init__(self, func):
      self.func = func
      self.cache = {}
   def __call__(self, *args):
      if not isinstance(args, collections.Hashable):
         # uncacheable. a list, for instance.
         # better to not cache than blow up.
         return self.func(*args)
      if args in self.cache:
         return self.cache[args]
      else:
         value = self.func(*args)
         self.cache[args] = value
         return value
   def __repr__(self): #功能与__str__()类似
      '''Return the function's docstring.'''
      return self.func.__doc__
   def __get__(self, obj, objtype):
      '''Support instance methods.'''
      return functools.partial(self.__call__, obj)

@memoized
def fibonacci(n):
   "Return the nth fibonacci number."
   if n in (0, 1):
      return n
   return fibonacci(n-1) + fibonacci(n-2)

print fibonacci(12)

#-------------------------B--------------------------
#Here's a memoizing function that works on functions, methods, or classes, and exposes the cache publicly.
# note that this decorator ignores **kwargs
def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        if args not in cache:
            cache[args] = obj(*args, **kwargs)
        return cache[args]
    return memoizer

#Here's a modified version that also respects kwargs.
def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer

#This is an idea that interests me, but it only seems to work on functions:
class memoize(dict):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self[args]

    def __missing__(self, key):
        result = self[key] = self.func(*key)
        return result
"""
If a subclass of dict defines a method __missing__() and key is not present, the d[key] operation calls 
that method with the key key as argument. The d[key] operation then returns or raises whatever is returned 
or raised by the __missing__(key) call. No other operations or methods invoke __missing__(). If __missing__() 
is not defined, KeyError is raised. __missing__() must be a method; it cannot be an instance variable:
>>> class Counter(dict):
...     def __missing__(self, key):
...         return 0
>>> c = Counter()
>>> c['red']
0
>>> c['red'] += 1
>>> c['red']
1

The example above shows part of the implementation of collections.Counter. A different __missing__ method 
is used by collections.defaultdict.
"""
#
# Sample use
#

>>> @memoize
... def foo(a, b):
...     return a * b
>>> foo(2, 4)
8
>>> foo
{(2, 4): 8}
>>> foo('hi', 3)
'hihihi'
>>> foo
{(2, 4): 8, ('hi', 3): 'hihihi'}

#Alternate memoize that stores cache between executions
#Additional information and documentation for this decorator is available on https://github.com/brmscheiner/memorize.py

import pickle
import collections
import functools
import inspect
import os.path
import re
import unicodedata


# This configures the place to store cache files globally.
# Set it to False to store cache files next to files for which function calls are cached.
USE_CURRENT_DIR = True


class Memorize(object):
    '''
    A function decorated with @memorize caches its return
    value every time it is called. If the function is called
    later with the same arguments, the cached value is
    returned (the function is not reevaluated). The cache is
    stored as a .cache file in the current directory for reuse
    in future executions. If the Python file containing the
    decorated function has been updated since the last run,
    the current cache is deleted and a new cache is created
    (in case the behavior of the function has changed).
    '''
    def __init__(self, func):
        self.func = func
        function_file = inspect.getfile(func)
        self.parent_filepath = os.path.abspath(function_file)
        self.parent_filename = os.path.basename(function_file)
        self.__name__ = self.func.__name__
        self.cache = None  # lazily initialize cache to account for changed global dir setting (USE_CURRENT_DIR)

    def check_cache(self):
        if self.cache is None:
            if self.cache_exists():
                self.read_cache()  # Sets self.timestamp and self.cache
                if not self.is_safe_cache():
                    self.cache = {}
            else:
                self.cache = {}

    def __call__(self, *args):
        self.check_cache()
        if not isinstance(args, collections.Hashable):
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            self.save_cache()
            return value

    def get_cache_filename(self):
        """
        Sets self.cache_filename to an os-compliant
        version of "file_function.cache"
        """
        filename = _slugify(self.parent_filename.replace('.py', ''))
        funcname = _slugify(self.__name__)
        folder = os.path.curdir if USE_CURRENT_DIR else os.path.dirname(self.parent_filepath)
        return os.path.join(folder, filename + '_' + funcname + '.cache')

    def get_last_update(self):
        """
        Returns the time that the parent file was last
        updated.
        """
        last_update = os.path.getmtime(self.parent_filepath)
        return last_update

    def is_safe_cache(self):
        """
        Returns True if the file containing the memoized
        function has not been updated since the cache was
        last saved.
        """
        if self.get_last_update() > self.timestamp:
            return False
        return True

    def read_cache(self):
        """
        Read a pickled dictionary into self.timestamp and
        self.cache. See self.save_cache.
        """
        with open(self.get_cache_filename(), 'rb') as f:
            data = pickle.loads(f.read())
            self.timestamp = data['timestamp']
            self.cache = data['cache']

    def save_cache(self):
        """
        Pickle the file's timestamp and the function's cache
        in a dictionary object.
        """
        with open(self.get_cache_filename(), 'wb+') as f:
            out = dict()
            out['timestamp'] = self.get_last_update()
            out['cache'] = self.cache
            f.write(pickle.dumps(out))

    def cache_exists(self):
        '''
        Returns True if a matching cache exists in the current directory.
        '''
        if os.path.isfile(self.get_cache_filename()):
            return True
        return False

    def __repr__(self):
        """ Return the function's docstring. """
        return self.func.__doc__

    def __get__(self, obj, objtype):
        """ Support instance methods. """
        return functools.partial(self.__call__, obj)

def _slugify(value):
    """
    Normalizes string, converts to lowercase, removes
    non-alpha characters, and converts spaces to
    hyphens. From
    http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = re.sub(r'[^\w\s-]', '', value.decode('utf-8', 'ignore'))
    value = value.strip().lower()
    value = re.sub(r'[-\s]+', '-', value)
    return value

##Cached Properties

import time

class cached_property(object):
    '''Decorator for read-only properties evaluated only once within TTL period.

    It can be used to create a cached property like this::

        import random

        # the class containing the property must be a new-style class
        class MyClass(object):
            # create property whose value is cached for ten minutes
            @cached_property(ttl=600)
            def randint(self):
                # will only be evaluated every 10 min. at maximum.
                return random.randint(0, 100)

    The value is cached  in the '_cache' attribute of the object instance that
    has the property getter method wrapped by this decorator. The '_cache'
    attribute value is a dictionary which has a key for every property of the
    object which is wrapped by this decorator. Each entry in the cache is
    created only when the property is accessed for the first time and is a
    two-element tuple with the last computed property value and the last time
    it was updated in seconds since the epoch.

    The default time-to-live (TTL) is 300 seconds (5 minutes). Set the TTL to
    zero for the cached value to never expire.

    To expire a cached property value manually just do::

        del instance._cache[<property name>]

    '''
    def __init__(self, ttl=300):
        self.ttl = ttl

    def __call__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__
        self.__module__ = fget.__module__
        return self

    def __get__(self, inst, owner):
        now = time.time()
        try:
            value, last_update = inst._cache[self.__name__]
            if self.ttl > 0 and now - last_update > self.ttl:
                raise AttributeError
        except (KeyError, AttributeError):
            value = self.fget(inst)
            try:
                cache = inst._cache
            except AttributeError:
                cache = inst._cache = {}
            cache[self.__name__] = (value, now)
        return value


##Retry
"""
Call a function which returns True/False to indicate success or failure. On failure, wait, 
and try the function again. On repeated failures, wait longer between each successive attempt. 
If the decorator runs out of attempts, then it gives up and returns False, but you could 
just as easily raise some exception.
"""
import time
import math

# Retry decorator with exponential backoff
def retry(tries, delay=3, backoff=2):
  '''Retries a function or method until it returns True.

  delay sets the initial delay in seconds, and backoff sets the factor by which
  the delay should lengthen after each failure. backoff must be greater than 1,
  or else it isn't really a backoff. tries must be at least 0, and delay
  greater than 0.'''

  if backoff <= 1:
    raise ValueError("backoff must be greater than 1")

  tries = math.floor(tries)
  if tries < 0:
    raise ValueError("tries must be 0 or greater")

  if delay <= 0:
    raise ValueError("delay must be greater than 0")

  def deco_retry(f):
    def f_retry(*args, **kwargs):
      mtries, mdelay = tries, delay # make mutable

      rv = f(*args, **kwargs) # first attempt
      while mtries > 0:
        if rv is True: # Done on success
          return True

        mtries -= 1      # consume an attempt
        time.sleep(mdelay) # wait...
        mdelay *= backoff  # make future wait longer

        rv = f(*args, **kwargs) # Try again

      return False # Ran out of tries :-(

    return f_retry # true decorator -> decorated function
  return deco_retry  # @retry(arg[, ...]) -> true decorator


##functools.partial()
#you can use functools.partial() to emulate currying (which works even for keyword arguments)

class curried(object):
  '''
  Decorator that returns a function that keeps returning functions
  until all arguments are supplied; then the original function is
  evaluated.
  '''

  def __init__(self, func, *a):
    self.func = func
    self.args = a

  def __call__(self, *a):
    args = self.args + a
    if len(args) < self.func.func_code.co_argcount:
      return curried(self.func, *args)
    else:
      return self.func(*args)


@curried
def add(a, b):
    return a + b

add1 = add(1)

print add1(2)





























































