#!/usr/bin/env python3
"""match.py
Copyright Erich Blume 2012 <blume.erich@gmail.com>
All rights granted to the redditgifts team for the use of this code at their discression.

Implements one function, `match`. Also implements a Participant class describing the minimal
necessary representation for the algorithm to run.
"""

import sys

class Participant:
  def __init__(self, id, country, international):
    """Basic placeholder class to model Participants."""
    self.id = id # beware, id is from args, not from built-in funcs
    self.country = country
    self.international = international

class __Sifter:
  def __init__(self):
    """Collection of sets allowing sorting by country. A helper class."""
    self.nations = {}
    self.num = 0

  def add(self, participant):
    try:
      self.nations[participant.country].add(participant)
    except KeyError as err:
      self.nations[participant.country] = {participant}
    self.num += 1

  def country(self, country):
    "Return a set with all participants from this country."
    try:
      return self.nations[country].copy()
    except KeyError as err:
      return set()

  def __len__(self):
    return self.num

  def pop(self):
    "Return a random member and remove it."
    for nation_name,nation in self.nations.items():
      if nation:
        self.num -= 1
        result = nation.pop()
        if len(nation) == 0:
          del self.nations[nation_name]
        return result
    raise KeyError('No participants in this set.')

  def pop_from(self, country):
    "Return some member of this country, and remove it."
    result = self.nations[country].pop()
    self.num -= 1
    if len(self.nations[country]) == 0:
      del self.nations[country]
    return result

  def pop_from_most(self):
    "Return and remove a random member from the most abundant country."
    ## IMPORTANT NOTE
    # In production code, this should be replaced with an internal priority queue (heap)
    # to make finding the top country fast at the expense of a bit more work for every add
    # and pop... *probably*. I didn't do it because I have a suspicion that even though we
    # are sorting on every single call to this function, I think this function will be called
    # not very often and will result in a faster runspeed overall. Profiling needed.
    top_country = sorted(self.nations, key=lambda x: len(self.nations[x]), reverse=True)[0]
    result = self.nations[top_country].pop()
    self.num -= 1
    if len(self.nations[top_country]) == 0:
      del self.nations[top_country]
    return result


def match(participants):
  """List of participants -> list of tuples of participants, indicating their matches."""
  
  # See README.md for the explanation. Some documentation will be inline.

  ### Step 1: Create basic partition sets.

  internationals = __Sifter() 
  nationals = __Sifter()
  def partition(gifter):
    # Could be a lambda, but got a bit long.
    if gifter.international:
      internationals.add(gifter)
    else:
      nationals.add(gifter)
  list(map(partition, participants))

  ### Step 2: Enforce size constraints

  # First pass, pull from internationals
  for nation_name,nation in nationals.nations.items():
    if len(nation) <= 2 and internationals.country(nation_name):
      nation.add(internationals.pop_from(nation_name))
      # Run the same check a second time to get up to len(nation) == 3 if possible.
      if len(nation) <= 2 and internationals.country(nation_name):
        nation.add(internationals.pop_from(nation_name))
    elif len(nation) == 1:
      # Forever alone :( Either enter an ERROR STATE or else just add to international.
      # For now, add to international.
      internationals.add(nation.pop())
  # Make sure internationals isn't len == 1
  if len(internationals) == 1:
    # Forever alone :( Let's put her back in her country.
    nationals.add(internationals.pop())


  ### Step 3: Make gifter chains
  # As a somewhat strange optimization, we will represent a chain as a list, where each
  # element is assigned the one that *preceeds* it. The first element is assigned the
  # last one.

  # For the national chains, just coerce the sets in to lists. Result: list of lists.
  national_chains = map(list,nationals.nations.values())
  # International chains are more complicated. Luckily the __Sifter class will help.
  intl_chain = []
  while len(internationals) > 0:
    intl_chain.append(internationals.pop_from_most())

  ### Step 4: Construct the result
  result = []
  for chain in national_chains:
    for position,gifter in enumerate(chain):
      giftee = chain[position-1]
      result.append((gifter.id, giftee.id))
  for position,gifter in enumerate(intl_chain):
    giftee = intl_chain[position-1]
    result.append((gifter.id, giftee.id))

  ### And we're done!
  return result



def _fake_data_set():
  """Create a fake Participant data set for testing purposes."""
  data = [
    (0,"US",False),
    (1,"US",False),
    (2,"US",False),
    (3,"US",False),
    (4,"US",False),
    (5,"US",False),
    (6,"US",False),
    (7,"US",False),
    (8,"US",False),
    (9,"US",False),
    (10,"US",False),
    (11,"US",False),
    (12,"US",False),
    (13,"US",False),
    (14,"US",True),
    (15,"US",True),
    (16,"US",True),
    (17,"US",True),
    (18,"GA",False),    # These 3 should get matched together.
    (19,"GA",False),    #
    (20,"GA",True),     #
    (21,"BO",False),  # These 2 should get matched together
    (22,"BO",True),   #
    (23,"AW",True),     # International only
  ]

  return list(map(lambda x: Participant(*x), data))





