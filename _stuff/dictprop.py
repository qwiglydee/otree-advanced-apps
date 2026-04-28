"""
Combining multiple fields into dictionary
by qwiglydee@gmail.com

Usage:
  class Something(ExtraModel):
      foo_a = models.StringField()
      foo_b = models.StringField()
      foos = dictproperty('foo_', 'AB') # => { 'A': foo_a, 'B': foo_b }

      bar_a1 = models.StringField()
      bar_a2 = models.StringField()
      bars = dictproperty('bar_', ('a1', 'a2')) # => { 'a1': bar_a1, 'B': bar_b }
"""


def dictvalues(obj, prefix, suffixes):
    return {k: getattr(obj, prefix + k.lower()) for k in suffixes}


class dictproperty():
    def __init__(self, prefix, suffixes):
        self.prefix = prefix
        self.suffixes = suffixes

    def __get__(self, instance, owner):
        return dictvalues(instance, self.prefix, self.suffixes)
