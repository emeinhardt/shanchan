import json, codecs
import random
from fractions import Fraction
from collections import defaultdict, Counter
from itertools import product, accumulate
from functools import reduce
import operator
from bisect import bisect
# from math import log2, isclose
from math import isclose
import math
from boilerplate import *
import numpy as np

my_epsilon = 1e-13

def norm(dist):
    return sum(dist.values())

def norms(dists):
#     return map(norm, dists)
    return list(map(lambda c: norm(dists[c]), dists))

def isNormalized(dist, epsilon = None):
    if epsilon == None:
        epsilon = my_epsilon
    return abs(norm(dist) - 1) < epsilon

def areNormalized(dists, epsilon = None):
    if epsilon == None:
        epsilon = my_epsilon
    return all(map(lambda k: isNormalized(dists[k], epsilon = epsilon), dists))

def normalizationDefect(dist):
    return abs(norm(dist) - 1)

# import json, codecs

def exportProbDist(fn, dist):
    with codecs.open(fn, 'w', encoding='utf-8') as f:
        json.dump(dist, f, ensure_ascii = False, indent = 4)
        
def importProbDist(fn):
    with open(fn, encoding='utf-8') as data_file:
        dist_in = json.loads(data_file.read())
    return dist_in


# Modified version of Norvig's ProbDist code

# import random
# from fractions import Fraction
# from collections import defaultdict, Counter

is_predicate = callable

def P(event, space): 
    """The probability of an event, given either a sample space of equiprobable outcomes
    or a pmf. 
    event: a collection of outcomes, or a predicate that is true of outcomes in the event. 
    space: a set of outcomes or a probability distribution of {outcome: frequency} pairs."""
    if is_predicate(event):
#         print('Event is a predicate. Constructing a conditional distribution.')
        event = such_that(event, space)
    if isinstance(space, ProbDist):
#         print('Space is a ProbDist.')
        if isinstance(event, str):
#             print('Event is a string.')
            return space[event]
        else:
#             print('Event is not a string.')
            return sum(space[o] for o in space if o in event)
    else:
#         print('Space is not a prob dist and event is assumed to be a collection.')
        return Fraction(len(event & space), len(space))

def such_that(predicate, space): 
    """The outcomes in the sample pace for which the predicate is true.
    If space is a set, return a subset {outcome,...};
    if space is a ProbDist, return a ProbDist {outcome: frequency,...};
    in both cases only with outcomes where predicate(element) is true."""
    if isinstance(space, ProbDist):
        return ProbDist({o:space[o] for o in space if predicate(o)})
    else:
        return {o for o in space if predicate(o)}

# class ProbDist(dict):
class ProbDist(Counter):
    "A Probability Distribution; an {outcome: probability} mapping where probabilities sum to 1."
    def __init__(self, mapping=(), **kwargs):
        self.update(mapping, **kwargs)
        total = sum(self.values())
        if isinstance(total, int): 
            total = Fraction(total, 1)
        for key in self: # Make probabilities sum to 1.
            self[key] = self[key] / total
            
    def __and__(self, predicate): # Call this method by writing `probdist & predicate`
        "A new ProbDist, restricted to the outcomes of this ProbDist for which the predicate is true."
        return ProbDist({e:self[e] for e in self if predicate(e)})
    
    def __repr__(self):
        s = ""
        for k in self:
            if isinstance(self[k], Fraction):
                s+="{0}: {2}/{3} = {1}\n".format(transcriptionReprHack(k), float(self[k]), self[k].numerator, self[k].denominator)
            else:
                s+="{0}: {1}\n".format(transcriptionReprHack(k), float(self[k]))
        return s
    
def transcriptionReprHack(k):
    if type(k) == type(tuple()):
        if all(map(lambda el: type(el) == type(''), k)):
            return tupleToDottedString(k)
    return k.__repr__()    

def Uniform(outcomes): return ProbDist({e: 1 for e in outcomes})

def joint(A, B):
    """The joint distribution of two independent probability distributions. 
    Result is all entries of the form {(a, b): P(a) * P(b)}"""
    return ProbDist({(a,b): A[a] * B[b]
                    for a in A
                    for b in B})

# from itertools import product, accumulate
# # from functools import reduce
# import operator

def prod(iterable):
    return reduce(operator.mul, iterable, 1)

# def union(iterable):
#     return reduce(set.union, iterable)

def joint2(iter_of_dists):
    #ProbDist({(a,b): A[a] * B[b] for a in A for b in B})
    #ProbDist({ab: A[ab[0]] * B[ab[1]] for ab in product(A,B)})
    return ProbDist({each : prod(dist[each[i]] for i,dist in enumerate(iter_of_dists)) for each in list(product(*iter_of_dists))})

# first = lambda seq: seq[0]
# second = lambda seq: seq[1]

# def first(seq):
#     return seq[0]

# def second(seq):
#     return seq[1]

# from random import choices

# from bisect import bisect

def choices(population, weights=None, k=1):
# def choices(population, weights=None, *, cum_weights=None, k=1):
        """Return a k sized list of population elements chosen with replacement.
        If the relative weights or cumulative weights are not specified,
        the selections are made with equal probability.
        """
        # random = random.random
        cum_weights = None #moved inside
        if cum_weights is None:
            if weights is None:
                _int = int
                total = len(population)
                return [population[_int(random.random() * total)] for i in range(k)]
            cum_weights = list(accumulate(weights))
        elif weights is not None:
            raise TypeError('Cannot specify both weights and cumulative weights')
        if len(cum_weights) != len(population):
            raise ValueError('The number of weights does not match the population')
#         bisect = _bisect.bisect
        total = cum_weights[-1]
        hi = len(cum_weights) - 1
        return [population[bisect(cum_weights, random.random() * total, 0, hi)]
                for i in range(k)]


def sampleFrom(dist, num_samples = None):
    """
    Given a distribution (either an {outcome: probability} mapping where the 
    probabilities sum to 1 or an implicit definition of a distribution via a thunk), 
    this returns a single sample from the distribution, unless num_samples is specified, 
    in which case a generator with num_samples samples is returned.
    """
    if num_samples == None:
        if callable(dist):
            return dist()
        elif isinstance(dist, ProbDist) or isinstance(dist, dict):
            assocMap = tuple(dist.items())
            outcomes = tuple(map(first, assocMap))
            weights = tuple(map(second, assocMap))
            return choices(population=outcomes, weights=weights)[0]
    else:
        if callable(dist):
            return (dist() for each in range(num_samples))
        elif isinstance(dist, ProbDist) or isinstance(dist, dict):
            assocMap = dist.items()
            outcomes = tuple(map(first, assocMap))
            weights = tuple(map(second, assocMap))
            return tuple(choices(population=outcomes, weights=weights, k=num_samples))

# from collections import Counter

def frequencies(samples):
    return Counter(samples)

def makeSampler(dist):
    """
    Given a ProbDist, returns a thunk that when called, returns one sample from dist.
    """
    return lambda: sampleFrom(dist)


def support(dist):
    return {e for e in dist if dist[e] > 0.0}

def trimToSupport(dist):
    if isinstance(dist[getRandomKey(dist)], ProbDist):
        return {conditioning_event:trimToSupport(dist[conditioning_event]) 
                for conditioning_event in dist}
    else:
        return ProbDist({e:dist[e] for e in support(dist)})

def expectation(p, f=None):
    '''
    Given a ProbDist p :: O ⟶ [0,1] and a mapping f :: O ⟶ R, this returns 
    the expected value of f with respect to p.
    
    f can be a dictionary, ProbDist, or function.
    
    Alternatively, given a ProbDist p :: R ⟶ [0,1], this returns the mean of p.
    '''
    if f is None:
        return sum({p[o] * o for o in conditions(p)})
    if type(f) == type(dict()) or type(f) == type(Uniform({0,1})):
        lookup = lambda o: f[o]
    if callable(f):
        lookup = lambda o: f(o)
    return sum({p[o] * lookup(o)
                for o in p})

def expectation_np(f, p):
    '''
    Given an np array f that represents a finite set of outcomes {O_i} ∈ R and
    an np array p that represents a distribution over the same set of outcomes,
    this returns the expectation of f wrt p.
    '''
    return np.dot(f, p)
    

def marginal_np(p, prior):
    '''
    Given a 2D m x n numpy array p representing a family of m conditional 
    distributions {p(Y|x_j)} over n outcomes {x_j} and an array representing 
    a prior p(X) over X = {x_j}, this returns the marginal distribution p(Y).
    '''
    return np.dot(p, prior)
    
def P_marginal_cd(e, cd, prior):
    '''
    Given a dictionary of ProbDists cd representing a family of 
    conditional distributions {p(Y|x_i)}, a prior on the 
    conditions p(X), and an event e, this calculates the marginal
    probability p(e).
    '''
#     uo = uniformOutcomes(cd)
#     if uo is not True:
#         raise Exception('Outcomes are not uniform: {0}'.format(uo))
#     badConditions = {c for c in conditions(cd) if c not in prior}
#     assert len(badConditions) == 0, "Some conditioning events are not in the sample space of the prior: {0}".format(badConditions)
#     conditionNorm = float(sum(prior[c] for c in cd))
#     assert np.isclose(conditionNorm, 1.0), "Sum of probabilities (according to the prior) of conditioning events in cd must be 1, but instead = {0}".format(conditionNorm)
    return sum(prior[c] * P(e, cd[c])
               for c in prior)
    
def MarginalProbDist(cd, prior):
    '''
    Given a dictionary of ProbDists cd representing a family of 
    conditional distributions {p(Y|x_i)} and a prior on the 
    conditions p(X), this returns a ProbDist representing the 
    marginal distribution P(Y).
    '''
#     uo = uniformOutcomes(cd)
#     if uo is not True:
#         raise Exception('Outcomes are not uniform: {0}'.format(uo))
#     badConditions = {c for c in conditions(cd) if c not in prior}
#     assert len(badConditions) == 0, "Some conditioning events are not in the sample space of the prior: {0}".format(badConditions)
#     conditionNorm = float(sum(prior[c] for c in cd))
#     assert np.isclose(conditionNorm, 1.0), "Sum of probabilities (according to the prior) of conditioning events in cd must be 1, but instead = {0}".format(conditionNorm)
    
    O = outcomes(cd)
    return ProbDist({o:sum(prior[c] * cd[c][o]
                           for c in prior)
                     for o in O})

# from math import log2

def log(x):
    if type(x) == type(Fraction(1,2)):
#         return np.log2(float(x))
        return math.log2(x)
#     if x == 0.0:
#         return 0.0
    return np.log2(x)
#     return math.log2(x)

def h_prime(prob):
    return -1.0 * log(prob)

def surprisals(space):
    '''
    Given a ProbDist p(X), returns a dictionary mapping
    each outcome x to h(p(X)).
    '''
    return {o:h_prime(space[o]) for o in space}

def h(event, space):
    p = P(event, space)
#     p = space[event]
    return -1.0 * log(p)

def prod_prime(iterable):
    return reduce(mul_prime, iterable, 1)

def mul_prime(a, b):
    if type(a) == type(Fraction(1,2)):
        a = float(a)
    if type(b) == type(Fraction(1,2)):
        b = float(b)
    if (np.isclose(a, 0.0) and abs(b) == np.infty) or (abs(a) == np.infty and np.isclose(b, 0.0)):
        return 0.0
    return a * b

def couldBeAProbability(p):
    return 0.0 <= p and p <= 1.0

def isNormalized_np(p):
    return np.isclose(p.sum(), 1.0)

def areNormalized_np(p):
    return np.allclose(p.sum(axis=0), np.ones(shape=(p.shape[1])))

def normalize_np(p):
    return p / p.sum()

def normalizeCondDist_np(p):
    col_sums = p.sum(axis=0, keepdims=True)
    p_normalized = p / col_sums
    return p_normalized

def is_a_distribution_np(p):
    return isNormalized_np(p) and all(list(map(couldBeAProbability, p)))

def H_np(p, prior=None, paranoid=False):
    '''
    Given a numpy array p representing a probability distribition p(X), this
    returns the Shannon entropy of the distribution H(X).
    
    Given a 2D m x n numpy array p representing a family of m conditional 
    distributions {p(Y|x_j)} over n outcomes {x_j}, this retuns the m conditional
    entropies as an array.
    
    Given a 2D m x n numpy array p representing a family of m conditional 
    distributions {p(Y|x_j)} over n outcomes {x_j} and an array representing 
    a prior p(X) over X = {x_j}, this returns the expected conditional entropy
    H(Y|X).
    '''
    if p.squeeze().ndim == 1:
        if paranoid:
            badValues = [(i, p_i) for i, p_i in enumerate(p) if not couldBeAProbability(p_i)]
            assert len(badValues) == 0, "{0} cannot represent probabilities".format(badValues)
            assert isNormalized_np(p), "Probabilities do not sum to 1.\n  Sum: {0}\n  Vector: {1}".format(np.sum(p), p)
        return np.dot(p, -1.0 * np.log2(p, where=(p != 0.0)))
#         return np.nansum(p * (-1.0 * np.log2(p)))
    if prior is None:
        return np.apply_along_axis(H_np, 0, p)
    return np.dot( np.apply_along_axis(H_np, 0, p), prior )
    

def H(space, prior = None):
    """
    Given a ProbDist p(X), returns the Shannon entropy H(X).
    
    Given a dictionary representing a family of conditional 
    distributions p(Y|X) and a prior p(X), returns H(Y|X).
    """
    if prior is not None and isinstance(space[getRandomKey(space)], ProbDist):
#         assert set(prior.keys()) == set(space.keys())
        support_of_prior = set([k for k in prior.keys() if prior[k] > 0.0])
        assert all([e in support_of_prior for e in space])
        
        prior_probs = tuple([P(event, prior) for event in sorted(space)])
        entropies = tuple([H(space[event]) for event in sorted(space)])
        terms = tuple(zip(prior_probs, entropies))
#         prods = tuple(map(prod, terms))
        prods = tuple(map(prod_prime, terms))
        s = sum(prods)
        return s
    else:
        probs = tuple([P(event, space) for event in sorted(space)])
    #     probs = tuple([space[event] for event in sorted(space)])
        surprisals = tuple([h(event, space) for event in sorted(space)])
        terms = tuple(zip(probs, surprisals))
#         prods = tuple(map(prod, terms))
        prods = tuple(map(prod_prime, terms))
        s = sum(prods)
        return s

def pDKL(event, p, q):
    '''
    Pointwise KL diveregence from p to q at event.
    '''
    return log(P(event, p)) - log(P(event, q))
#     return log(p[event] / q[event])

def DKL(p, q, rel_tol=1e-09):
    """
    Given two spaces p, q, returns the Kullback-Leibler divergence from P to Q.
    
    If the naive result is slightly negative but within rel_tol of 0.0, this will
    return 0.0; otherwise it will throw an assertion error.
    """
    assert p.keys() == q.keys(), "P and Q must share a common event space."
#     def qZeroImpliesPzero(event):
#         if P(event, q) == 0.0:
#             if P(event, p) == 0.0:
#                 return True
#             else:
#                 return False
#         return True
    events = set(p.keys())
    badEvent = lambda event: P(event, q) == 0.0 and P(event, p) != 0.0
    badEvents = {e for e in events if badEvent(e)}
    assert len(badEvents) == 0, "∀x Q(x) = 0 must ⇒ P(x) = 0. Bad events [(e, Q(e), P(e))] = {0}".format({(e, P(e, q), P(e, p)) for e in badEvents})
    
    #This seems necessary due to 
    #what seem like floating point arithmetic errors 
    #that lead to tiny (∝1e-16) but slightly negative divergences.
    if p == q: 
        return 0.0
    
    probs = tuple([P(event, p) for event in p])
#     probs = tuple([p[event] for event in p])
    pointwiseDivergences = tuple([pDKL(event, p, q) for event in p])
    assert len(probs) == len(pointwiseDivergences)
    terms = tuple(zip(probs, pointwiseDivergences))
#     prods = tuple(map(prod, terms))
    prods = tuple(map(prod_prime, terms))
    s = sum(prods)
    
    #math.isclose does NOT do what it ought to...
    if s <= 0.0 and np.isclose(s, 0.0, rtol=rel_tol):
        return 0.0
    
    assert s >= 0.0, "KL divergence {0} should be non-negative.\n  Probs: {1}\n  Pointwise divergences: {2}\n  Products: {3}".format(s, probs, pointwiseDivergences, prods)
    return s

def zeros1d(a):
    return np.setdiff1d( np.arange(a.shape[0]), a.nonzero()[0] )

def DKL_np(p, q):
#     p_zs = zeros1d(p)
#     q_zs = zeros1d(q)
    d = p / q
    log_d = np.log2(d, where=(p != 0) & (q != 0))
    return np.dot(p, log_d)

def binary_mixture(p, q, l):
    """
    Given two spaces P, Q, and the weight (l = "λ") of P, returns a new space R s.t.
        R = λP + (1-λ)Q
    """
    assert 0.0 < l and 1.0 >= l
    outcomes = set.union(set(p.keys()), set(q.keys()))
    R_dict = {o:l*p[o] + (1.0-l) * q[o]
              for o in outcomes}
    return ProbDist(R_dict)

def LD(p, q, l=0.5):
    """
    Given two spaces p, q, and the weight (l = "λ") of p, returns the λ-divergence:
        D_λ(P||Q) = λD_KL(P||λP + μQ) + μD_KL(Q||λP + μQ)
    where μ = 1 - λ.
    """
    r = binary_mixture(p, q, l)
    left_term = DKL(p, r)
    right_term = DKL(q, r)
    mu = 1.0 - l
    return l*left_term + mu*right_term

def JS(p,q):
    """
    Given two spaces p, q, returns the canonical Jensen-Shannon divergence between 
    them.
    """
    return LD(p, q, 0.5)

def mixture(Ps, mixture_probs=None, mixture_labels=None):
    '''
    Given 
     - a collection of probability distributions Ps
       on a common outcome space
     - a same-length collection of mixture probabilities
    
    This returns a ('flat') ProbDist R representing the 
    natural mixture distribution over outcomes.
    
    If given a set of mixture labels instead of a collection
    of mixture probabilities, this returns a conditional 
    distribution.
    '''
    
    Os = conditions(Ps[0])
    if mixture_labels is None:
        assert len(mixture_probs) == len(Ps)
        mixture_dist_np = np.array(mixture_probs)
        assert is_a_distribution_np(mixture_dist_np)
        index_to_obj_map = {i:i for i in range(len(mixture_dist_np))}
        mixture_dist = NPdistToDist(mixture_dist_np, 
                                    outcomeToIndexMap=index_to_obj_map
#                                     indexToOutcomeMap=index_to_obj_map
                                   )
#         print(mixture_dist)
        # map each o to its marginal probability under the mixture distribution
        R = {o:expectation(mixture_dist, {i:Ps[i][o]
                                          for i in index_to_obj_map})
             for o in Os}
        return ProbDist(R)
    else:
        assert len(mixture_labels) == len(Ps)
        return {c:Ps[i]
                for i,c in enumerate(mixture_labels)}

# mixture([ProbDist({'H':0.25, 'T':0.75}), ProbDist({'H':0.75, 'T':0.25})], mixture_probs=[0.5, 0.5])
# mixture([ProbDist({'H':0.25, 'T':0.75}), ProbDist({'H':0.75, 'T':0.25})], mixture_probs=[0.99, 0.01])
# mixture([ProbDist({'H':0.25, 'T':0.75}), ProbDist({'H':0.50, 'T':0.50})], mixture_labels=['biased', 'fair'])

def DJS(mixture_components, component_dist):
    '''
    This is the generalized Jensen-Shannon divergence,
    abstracted to accomodate mixture models with more 
    than two components and with an arbitrary 
    distribution over components.
    
    Let M(x) be a mixture distribution over X defined by
        - [π_0...π_n]
        - P(π_i)
    
    Then,
        D_JS([π_0...π_n], P(π_i))
         = 𝚺_i P(π_i) D_KL(π_i(x) || M(x))
    
    In terms of types, mixture_components should be a
    finite ordered collection of ProbDists and 
    component_dist should be a finite ordered collection
    that defines a probability distribution.
    '''
    assert sum(component_dist) == 1
    assert len(component_dist) == len(mixture_components)
    
    C = mixture_components
    pC = component_dist
    M = mixture(C, pC)
    
    DKL_terms = [DKL(c, M) for c in C]
    weighted_terms = [pC[i] * t for i,t in enumerate(DKL_terms)]
    DJS_result = sum(weighted_terms)
    return DJS_result

# DJS([ProbDist({'H':0.25, 'T':0.75}), ProbDist({'H':0.75, 'T':0.25})], component_dist=[0.5, 0.5])
# JS(ProbDist({'H':0.25, 'T':0.75}), ProbDist({'H':0.75, 'T':0.25}))

def condDistsAsProbDists(condDist):
    return {i:ProbDist(condDist[i]) for i in condDist}

def condProbDistAsDicts(condDistFamily):
    return {i:dict(condDistFamily[i]) for i in condDistFamily}

def condProbDistAsDicts_for_export(condDistFamily):
    return {i:mapValues(float, dict(condDistFamily[i])) for i in condDistFamily}

def distToNP(pO):
    pO_np = np.array([float(pO[o]) for o in sorted(pO.keys())])
    return pO_np

def NPdistToDist(pO_np, outcomeToIndexMap=None, indexToOutcomeMap=None):
    assert not (outcomeToIndexMap is None) and (indexToOutcomeMap is None)
    
    if outcomeToIndexMap is not None:
        pO = ProbDist({o:pO_np[outcomeToIndexMap[o]] for o in outcomeToIndexMap})
    if indexToOutcomeMap is not None:
        pO = ProbDist({indexToOutcomeMap[idx]:pO_np[idx] for idx in indexToOutcomeMap})
    return pO

def testNPdist(pO_np, outcomeMap, pO):
    assert all([ isclose(pO_np[outcomeMap[o]], pO[o]) for o in outcomeMap])
    
def condDistFamilyToNP(pOutIn):
    sorted_conditions = sorted(pOutIn.keys())
    sorted_outcomes = sorted(outcomes(pOutIn))
    pOutIn_np = np.array([[float(pOutIn[i][o]) for o in sorted_outcomes] for i in sorted_conditions])
    pOutIn_np = pOutIn_np.T
    return pOutIn_np

def condDistNPtoCondProbDist(pOutIn_np, conditionToIndexMap=None, indexToConditionMap=None, outcomeToIndexMap=None, indexToOutcomeMap=None, condition_axis=0):
    assert not (conditionToIndexMap is None) and (indexToConditionMap is None)
    assert not (outcomeToIndexMap is None) and (indexToOutcomeMap is None)
    
    if indexToConditionMap is not None:
        Cs = {indexToConditionMap[idx] for idx in indexToConditionMap}
        conditionToIndexMap = {indexToConditionMap[idx]:idx for idx in indexToConditionMap[idx]}
    else:
        Cs = set(conditionToIndexMap.keys())
    if indexToOutcomeMap is not None:
        Os = {indexToOutcomeMap[idx] for idx in indexToOutcomeMap}
        outcomeToIndexMap = {indexToOutcomeMap[idx]:idx for idx in indexToOutcomeMap[idx]}
    else:
        Os = set(outcomeToIndexMap.keys())
    
    if condition_axis == 0:
        pOutIn = {c:ProbDist({o:pOutIn_np[conditionToIndexMap[c]][outcomeToIndexMap[o]]
                              for o in Os})
                  for c in Cs}
    elif condition_axis == 1:
        pOutIn = {c:ProbDist({o:pOutIn_np[outcomeToIndexMap[o]][conditionToIndexMap[c]]
                              for o in Os})
                  for c in Cs}
    else:
        raise Exception(f'condition axis must be either 0 or 1, got {condition_axis} instead')
    return pOutIn

def testNPcondDist(pOutIn_np, inMap, outMap, pOutIn):
    assert all( isclose(pOutIn_np[outMap[o], inMap[i]], pOutIn[i][o]) for i in inMap for o in outMap)

def conditions(condDist):
    return condDist.keys()

def uniformOutcomes(condDist):
    outcomes = {c:frozenset(condDist[c].keys()) for c in condDist}
    outcomesAsSets = {Os for Os in outcomes.values()}
    if len( outcomesAsSets ) == 1:
        return True
    return outcomesAsSets

def outcomes(condDist):
    c = random.choice(list(condDist.keys()))
    return set(condDist[c].keys())

def divergences(c_star, condDists):
    return {c_prime:DKL(condDists[c_star], condDists[c_prime])
            for c_prime in condDists}

def avgDivergence(c_star, condDists, prior = None):
    if prior is None:
        prior = Uniform(conditions(condDists))
    
    divs = divergences(c_star, condDists)
    return sum(prior[c_prime]*divs[c_prime] for c_prime in conditions(condDists))

def discriminability(c_A, c_B, condDists, prior = None):
    if prior is None:
        mixPrior_X = Uniform({c_A, c_B})
    else:
        assert c_A in prior
        assert c_B in prior
        mixPrior_X = prior
    mix_Y_given_X = {c:ProbDist({o:condDists[c][o]
                                 for o in condDists[c_A]})
                     for c in mixPrior_X}
    mix_Y = ProbDist({o:(mixPrior_X[c_A]*condDists[c_A][o] + mixPrior_X[c_B]*condDists[c_B][o])
                      for o in condDists[c_A]})
    results = {'p(X)':mixPrior_X,
               'p(Y|X)':mix_Y_given_X,
               'p(Y)':mix_Y,
               'H(X)':H(mixPrior_X),
               'H(Y)':H(mix_Y),
               'H(Y|X)':H(mix_Y_given_X, mixPrior_X),
               'I(Y;X)':H(mix_Y) - H(mix_Y_given_X, mixPrior_X)}
    return results

def discriminabilities(c_star, condDists, c_primeToPriorMap = None):
    if symbolToPriorMap is None:
        symbolToPriorMap = {c_prime:Uniform({c_star, c_prime}) for c_prime in condDists}
    return {c_prime:discriminability(c_star, c_prime, condDists, symbolToPriorMap[c_prime])
            for c_prime in condDists}

def avgDiscriminability(c_star, condDists, c_primeToPriorMap = None, prior = None):
    if prior is None:
        prior = Uniform(conditions(condDists))
    
    discrims = discriminabilities(c_star, condDists, c_primeToPriorMap)
    return sum(prior[c_prime]*discrims[c_prime]['I(Y;X)'] for c_prime in conditions(condDists))
