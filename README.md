# Redditgifts Matchmaking Problem #

Solution by Erich Blume <blume.erich@gmail.com>
Hereby licensed without restriction to the redditgifts team, part of the reddit.com social empire.

## Problem Statement ##

When participants sign up for a gift exchange on redditgifts they specify two properties that are used within our matching process:

* Shipping Country (string)
* Shipping Preferences - whether or not they are willing to ship internationally (boolean)

Your program needs to find the best possible way to match participants such that:

* Whenever possible, the participants shipping preferences are adhered to.
* Whenever possible, participants who send a gift to a country other than their own are more likely to receive a gift from a country other than their own. Participants who indicate that they are willing to ship internationally typically wish to receive internationally, so amongst those who are willing to ship internationally, maximize the number of people who receive a gift from a country other than their own.
* Whenever possible, participants should not receive a gift from the same person they send a gift to.
* Every participant must be matched.
* The matching process should runs efficiently, meaning the execution time is short.

Your program should take 1 parameter as input, a list (array) where each item is a list (array) that represents a participant and has these three elements:

* unique id of participant (integer)
* shipping country of participant (string)
* willing to ship internationally (boolean)

Example: [[234, ‘US’, True], [235, ‘US’, False],]

Your program should return a list (array) where each element is a 2 item list (array) containing:

* Unique id of participant giving the gift
* Unique id of participant receiving the gift

Example: [[234, 235], [235, 234],]

Your solution should be representative of how you program. You should be able to explain the program and understand its strengths and weaknesses. You may write this program in any language you’d like to, but it needs to be executable (no pseudo code please).

For your reference, here is a spreadsheet containing numbers from Secret Santa 2011 of participants from each country and their shipping preferences. You can use this to generate a dataset that you use for testing.

Send your solution and anything else you think might help show us how rad you are to jobs@redditgifts.com! We like github links, we love reading code, we LOVE seeing examples of previous work, especially if you tell us what you did and why it's a good (or bad) example. Please email us at jobs@redditgifts.com and we will get back to you!

## Vocabulary ##

First, a word on vocabulary used in this solution:

* _Gifter_, _Participant_, _Node_, and _Person_ all refer to the same thing - someone participating in an exchange.
* A _Match_ refers to the participant whom another participant is assigned to send a gift to.
* A _Giftee_ refers to the paritcipant whom was matched to another participant (the inverse relationship between Participant and Match).

## Synthesis ##

First, note that the resulting data structure is equivalently expressed as a bijective map from every single particpant to her match (or, in reverse, from every participant to her sender). This can be equivalently expressed as a collection of acyclic graphs (where the nodes areparticipants) called here **match sets**, referring to the fact that a single strongly-connected 'chain' can be constructed out of any such set with size N > 2 such that every participant is assigned a match that is not herself, nor is her match matched with her. (The construction of such a chain is left as a trivial task, it involves a random walk through the set constructing a circular linked list.) For a set with size N = 2, a chain could be constructed but would violate the no-two-way-match constraint that will be introduced later. Constructing these chains allows the efficient creation of the resulting data structure for this algorithm, and this solution will concern the construction of such **match sets** to create such chains.

### Constraints

The **match sets** will be subject to the following constraints and properties:

1. The size of any set MUST be larger than 1 and SHOULD be larger than 2. This will be called the **no-two-way-match** constraint and is used to ensure that each resulting chain has the desirable property that **no gifter should be her match's match**, and especially that **no gifter will be her own giftee**. (The international set may have size == 0 after running.)
2. Each set will be composed of participants, and will conform to the properties of a mathematical set (uniqueness, unorderdness).
3. After the algorithm is run, each participant will have one match and one giftee. (Before the algorithm is run, neither is true.)
4. Each **match set** will either be labeled as an *international* set or as a *local* set.
5. There will be only one *international* set.
6. To the maximum possible extent without violating the **no-two-way-match** constraint, **all** participants who elected for an international exchange will be placed in the *international* set.
7. **No** participant who did not elect for an international exchange will be placed in the *international* set.

These set of constraints will ensure that the problem is answered, and will also aid in the construction of the algorithm for the solution.

### Process

Rather than giving a pseudocode implementation of the algorithm, a general process will be described. The accompanying implementation should serve as an easy-to-read algorithm.

As mentioned, we begin by representing the list of participants as an entirely unconnected 'graph' (no edges exist yet) of nodes, where each node represents a participant. We will then enforce the constraints to create a collection of **match sets**, from which we will construct the solution.

First, add all participants that indicated an international interest to the international set.

Then, partition all remaining participants in to one set per country.

Next, check each national set to see if it violates the **no-to-way-match** constraint (size N <= 2). If so, try and find an international participant in the same country and pull it out of the international set and in to that national set. (One easy change is to only perform this on N == 1, if two-way matches are more desirable than failing to match an international candidate.) If any set still has only size N == 1, we are in an **inconsistent state** and must perform error correction. Either add the sole participant to the international exchange against her will, or else inform her that she can't participate unless she makes that change.

Next, check that the international set has at least two participants. If not, remove the sole participant and place her in her nation's set - there will be no international gifting this exchange. :(

Partitioning is now complete! Next, we will synthesize the match chains.

For each non-international chain, the process is simple - construct the chain by performing a random walk throught the set creating a single-linked chain, and connect the last such node to the first node once the walk is complete.

For the international chain, a slightly more complex process is needed to avoid accidentally matching two locals together that happened to be in the international set. We still create the chain as a singlely-linked-list in a stepwise fashion, but instead of chosing the next node randomly, we choose it using the following selection: First, (temporarily) remove all nodes from the remaining nodes which share the last linked node's nation. Then, group all the remaining nodes by their nation, and count the size of each group. Finally, select a random node from the nation group with the highest count.

In the worst case scenario you might have an international set which groups like USA: 100, Brazil: 1, Spain: 1, Switerzland: 1. In this case, the above algorithm will match the maximum number of international people, and then match people from the USA to eachother as if they were in a local set. While not the ideal result, it is provably optimal for the scenario. (Alternatelly, we could enter an error state and prompt users for input - not a likely solution, though.)

Finally we have a collection of chains. Simply walk through each chain and construct the result structure, and return.

## Implementation

The solution is implemented as a Python 3 module (and might work with Python 2.6+, not tested.)

The module, `match.py`, implements only one public function: `match(participants)`, which returns the resulting list-of-2ples-of-participants after being given the input list-of-participants. (The input may in fact be any iterable of participants.)

## Testing

I am normally a large adherent to test-driven-development but I found that this particular problem didn't lend itself to it, as a testing harness would either be far larger than the implementation (it would need to reason about a dependency graph) or else the testing would need to be done in integration with a data source (much more likely, but beyond the scope of this submission.)

In a serious development environment, I'd start by writing a factory for sample data sets and then either A) write a library that reasons about the algorithm output or B) create some sample data sets, store them, and then write integration tests based on expected output.

In this case, you can approximate the testing process by running the following code:

>>> import match
>>> participants = match._fake_data_set()
>>> match.match(participants)

The result should show four distinct 'loops' that aren't too hard to find:

* 18, 19, and 20 are in a loop. ("GA" local)
* 21 and 22 are in a loop. ("BO" local)
* 0-13 are in a loop. ("US" local)
* 14-17 and 23 are in a loop. (international)

## Questions, comments:

Email me at blume.erich@gmail.com

Erich Blume
+1.9257863079







