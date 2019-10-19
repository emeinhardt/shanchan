from functools import reduce
from itertools import takewhile, product, starmap
import numpy as np
from random import choice
from funcy import *

def union(Ss):
    return reduce(set.union, Ss)

def language_concatenation(A, B, concat=None):
    if concat is None:
        concat = lambda u, v: u + v
    return set(starmap(concat,
                       product(A, B)))

leftEdge = '⋊'
rightEdge = '⋉'
edgeSymbols = {leftEdge, rightEdge}



def tupleToDottedString(tuple_string): 
    '''
    Takes a tuple of strings and joins them using '.'.
    '''
    return '.'.join(tuple_string)

def dottedStringToTuple(s): 
    '''
    Takes a '.'-separated string turns it into a tuple of strings.
    '''
    return tuple(s.split('.'))

def t2ds(tuple_string, sep='.'):
    '''
    Takes a tuple of strings and joins them using sep (defaults to '.').
    '''
    if sep == '.':
        return tupleToDottedString(tuple_string)
    else:
        return str_join(sep, tuple_string)

def t2cds(tuple_strings, macrosep=',', microsep='.'):
    '''
    Takes a tuple of (sub)tuples of strings and returns a single string with each
    (sub)tuple separated by macrosep (default=',') and each string within a (sub)tuple
    separated by microsep (default='.')
    '''
    return t2ds(tuple(map(partial(t2ds, sep=microsep), 
                          tuple_strings)), sep=macrosep)

def ds2t(s, macrosep=',', microsep='.', flatten=False):
    '''
    Takes a (comma- and) dot-separated string s and returns a tupled version.
    
    If s contains no commas (macrosep tokens), this returns a tuple of the strings separated
    by dots (microsep).
    
    If s contains commas (macroseps), this returns a tuple of (sub)tuples of strings.
    
    If s contains commas (macroseps), this returns a single flattened tuple of strings.
    '''
    if ',' not in s:
        return dottedStringToTuple(s)
    if not flatten:
        return tuple(map(partial(ds2t, macrosep=macrosep, microsep=microsep, flatten=flatten), 
                         s.split(macrosep)))
    else:
        return tuple(lflatten(tuple(map(dottedStringToTuple,
                                        s.split(macrosep)))))
    
def cds2tds(s, macrosep=',', microsep='.'):
    '''
    Takes a comma and dot-separated string s and returns a tuple of dot- (=microsep-) separated
    strings.
    '''
    return tuple(map(partial(t2ds, sep=microsep), 
                     ds2t(s, macrosep=macrosep, microsep=microsep)))
    
# t2ds = tupleToDottedString
# ds2t = dottedStringToTuple

def coerceDStoLength(ds, l, padChar='?'):
    s_t = ds2t(ds)
    my_l = len(s_t)
    if my_l == l:
        return ds
    elif my_l > l:
        new_s_t = s_t[:l]
        new_ds = t2ds(new_s_t)
        return new_ds
    else:
        n_pad_chars = l - my_l
        pad_ds = str_join('.', [padChar for each in range(n_pad_chars)])
        padded_ds = ds + '.' + pad_ds
        assert len(ds2t(padded_ds)) == l
        return padded_ds

def align_DSs(DSs):
    '''
    Pads each of segments of an iterable of dotted strings for easy
    visual inspection of how two dotted strings compare.
    '''
    padChar = ' '
    maxl = max({len(ds2t(w)) for w in DSs})
    padDS = lambda ds: t2ds( tuple(list(ds2t(ds)) + ([padChar] * (maxl - len(ds2t(ds))))) )
    paddedDSs = tuple(map(padDS, DSs))
    
    col_width = lambda ts, i: len(ts)[i]
    num_cols_per_slot = lambda padded_ds: tuple(map(len, ds2t(padded_ds)))
    ds_by_colwidth = np.stack([np.array(num_cols_per_slot(padded_ds))
                                        for padded_ds in paddedDSs])
    max_colwidths = np.apply_along_axis(max, axis=0, arr=ds_by_colwidth)
    
    pad_col = lambda i: lambda s: s if len(s) == max_colwidths[i] else s + (padChar * (max_colwidths[i] - len(s)))
    column_padders = {i:pad_col(i) for i in range(maxl)}
    pad_cols = lambda ds: t2ds(tuple([column_padders[i](s) for i, s in enumerate(ds2t(ds))]))
    col_padded_paddedDSs = tuple(map(pad_cols,
                                     paddedDSs))
    return col_padded_paddedDSs

def pprint_aligned_DSs(alignedDSs):
# def pprint_aligned_DSs(alignedDSs, colLabelsTop=True, colLabelsBottom=True, rowLabels=True):
    tableLength = len(alignedDSs)

    tableWidth = len(list(alignedDSs)[0])
#     collabels = ''.join( take(tableWidth, cycle('0123456789')) )
    
#     if colLabelsTop:
#         if not rowLabels:
#             print(collabels)
#         else:
#             print('  ' + collabels)
    
#     if rowLabels:
#         rowlabels = ''.join( take( len(alignedDSs), cycle(list(map(lambda i_str: i_str + ' ',
#                                                                    '01234567890'))) ) )
#     else:
#         rowlabels = ''.join( take( len(alignedDSs), cycle('') ) )
#     if rowLabels:
#         for r_label, ds in zip(rowlabels, alignedDSs):
#             print(r_label + ' ' +  ds)
#     else:
#         for ds in alignedDSs:
#             print(ds)
    for ds in alignedDSs:
        print(ds)
        
#     if colLabelsBottom:
#         if not rowLabels:
#             print(collabels)
#         else:
#             print('  ' + collabels)

# does not work when there are diphthongs or affricates
# def ds_l(s):
#     #let 
#     #  l = len(s)              ; length of a dotted string s as a string
#     #  n = len(  ds2t(s)  )    ; # of symbols in s
#     #  d = l - n               ; # of dots in s
#     #  
#     #  ∀s, d = n-1 ∴ l = n + (n - 1) = 2n - 1
#     #  ∴ n = (l+1)/2
#     return (len(s)+1)/2

def padInputSequenceWithBoundaries(inputSeq):
    temp = list(dottedStringToTuple(inputSeq))
    temp = tuple([leftEdge] + temp + [rightEdge])
    return tupleToDottedString(temp)

def trimBoundariesFromSequence(seq):
    temp = list(dottedStringToTuple(seq))
    if len(temp) < 1:
        return seq
    if temp[0] == leftEdge:
        temp = temp[1:]
    if len(temp) < 1:
        return tupleToDottedString(tuple(temp))
    if temp[-1] == rightEdge:
        temp = temp[:-1]
    if temp[-1] == rightEdge:
        temp = temp[:-1]
    return tupleToDottedString(tuple(temp))


def dsToInventory(s):
    s_t = ds2t(s)
    symbols = set(s_t)
    return symbols

def lexiconToInventory(DSs):
    inventories = list(map(dsToInventory, DSs))
    return union(inventories)



def subInDS(dottedString, to_replace, replacement):
    '''
    Replace each instance of symbol 'to_replace' 
    with 'replacement' symbol in 'dottedString'.
    '''
    old_symbol_tuple = dottedStringToTuple( dottedString )

    replacer = lambda symb: symb if symb != to_replace else replacement
    new_symbol_tuple = tuple( map(replacer, old_symbol_tuple) )

    dottedSymbols = tupleToDottedString( new_symbol_tuple ) 
    return dottedSymbols


def dsToKfactors(k, ds):
    seq = ds2t(ds)
    l = len(seq)
    if k > l:
        return tuple()
    kFactor_start_indices = takewhile(lambda pair: pair[0] <= l-k, enumerate(seq))
    kFactors = tuple(seq[index[0]:index[0]+k] for index in kFactor_start_indices)
    return set(map(t2ds, kFactors))

def dsTo2factors(ds):
    return dsToKfactors(2, ds)
def dsTo3factors(ds):
    return dsToKfactors(3, ds)

def lexiconToKfactors(DSs, k):
    myDsToKfactors = lambda ds: dsToKfactors(k, ds)
    return union(map(set, map(myDsToKfactors, DSs)))

def lexiconTo2factors(DSs):
    return union(map(set, map(dsTo2factors, DSs)))
def lexiconTo3factors(DSs):
    return union(map(set, map(dsTo3factors, DSs)))


def compareKfactors(DSs_A, DSs_B, k):
    A = lexiconToKfactors(DSs_A, k)
    B = lexiconToKfactors(DSs_B, k)
    return {"A == B":A == B, "A - B": A - B, "B - A": B - A}

def sameKfactors(DSs_A, DSs_B, k):
    return compareKfactors(DSs_A, DSs_B, k)["A == B"]

def hasIllicitKfactors(W, illicit_k_factors):
    if type(W) == str:      
        # gather the k-factors into an immutable data structure
        illicit_kfs = tuple(illicit_k_factors)
        # get the set of k-factor lengths (values of k) among the illicit_kfs
        illicit_factor_lengths = set([len(ds2t(kf)) for kf in illicit_kfs])
        # map each k to the set of k-factors of dotted string ds
        kFactorSets = {kf_l:dsToKfactors(kf_l, W) for kf_l in illicit_factor_lengths}
        illegal_kfactors_discovered = tuple(ikf for ikf in illicit_kfs if ikf in kFactorSets[len(ds2t(ikf))])
        if illegal_kfactors_discovered == tuple():
            return False
        return illegal_kfactors_discovered
    else:
        myFunc = lambda w: hasIllicitKfactors(w, illicit_k_factors)
        results = tuple(map(myFunc, W))
        if not any(results):
            return False
        return set(t2ds(each) for each in results if each != False)


    
def sigmaK(sigma, k):
    return product(sigma, repeat=k)



def dsToKfactorSequence(k, ds):
    seq = ds2t(ds)
    l = len(seq)
    if k > l:
        return tuple()
    kFactor_start_indices = takewhile(lambda pair: pair[0] <= l-k, enumerate(seq))
    kFactors = tuple(seq[index[0]:index[0]+k] for index in kFactor_start_indices)
    return tuple(map(t2ds, kFactors))

def threeFactorSequenceToDS(threeFactors):
    wLE = ds2t(threeFactors[0])[0]
    wRE = ds2t(threeFactors[-1])[-1]
    w_NE = '.'.join([ds2t(eachTriphone)[1] for eachTriphone in threeFactors])
    return '.'.join([wLE, w_NE, wRE])



def randomString(sigma, l, hasLeftEdge=True):
    s_t = tuple([choice(list(sigma)) for each in range(l)])
    s = t2ds(s_t)
    if hasLeftEdge:
        return leftEdge + '.' + s
    return s

# def randomPrefix(l, alphabet):
#     return randomString(alphabet, l, hasLeftEdge=True)

#BROKEN
# def randomPrefixFromTriphones(triphones, l, hasLeftEdge=True):
#     def foo(triphonesSoFar, max_length):
#         s = threeFactorSequenceToDS(triphonesSoFar)
#         s_t = ds2t(s)
#         l = len(s_t)
#         if l == max_length:
#             return s

#         rightmost_symbol = s_t[-1]
#         triphonesBeginningWithRMS = {t for t in triphones if ds2t(t)[0] == rightmost_symbol}
#         if l + 2 == max_length:
#             wordFinalTriphones = list({t for t in triphonesBeginningWithRMS if ds2t(t)[2] == rightEdge})
#             triphonesToChooseFrom = wordFinalTriphones
#         else:
#             wordMedialTriphones = list({t for t in triphonesBeginningWithRMS if ds2t(t)[2] != rightEdge})
#             triphonesToChooseFrom = wordMedialTriphones
#         nextTriphone = choice(triphonesToChooseFrom)
#         triphonesSoFar.append(nextTriphone)
#         return foo(triphonesSoFar, max_length)
#     if hasLeftEdge:
#         wordInitialTriphones = list({t for t in triphones if ds2t(t)[0] == leftEdge})
#         return foo([choice(wordInitialTriphones)], max_length = l)
#     else:
#         raise Exception("Currently unsupported.")
# #         return foo([choice(wordInitialTriphones)

def extract(i, Xs, returnAs='l,t,r', combine=lconcat):
    x_i = Xs[i]
    X_l = Xs[:i]
    X_r = Xs[i+1:]
    if returnAs == 'l,t,r':
        return (X_l, x_i, X_r)
    elif returnAs == 'l_r':
        return (X_l, X_r)
    elif returnAs == 'lr':
        return combine(X_l, X_r)
    elif returnAs == 't,l_r':
        return (x_i, (X_l, X_r))
    elif returnAs == 'l_r,t':
        return ((X_l, X_r), x_i)
    else:
        raise Exception('wtf')

def replaceXj(s, j, x):
    s_t = ds2t(s)
    s_l = list(s_t)
    s_l[j] = x
    s_t = tuple(s_l)
    return t2ds(s_t)

def removeXj(s, j):
    return replaceXj(s, j, '_')

def removeXi(x0k):
    l = len(ds2t(x0k))
    return removeXj(x0k, l-2)



def getPrefixes(s):
    if type(s) == str:
        sAsTup = ds2t(s)
    elif type(s) == tuple:
        sAsTup = s
    else:
        raise Exception('s must be a string or a tuple.')
    prefsAsTuples = set(sAsTup[0:i] for i in range(1, len(sAsTup)+1))
    return set(map(t2ds, prefsAsTuples))

def getProperPrefixes(s):
    Ps = getPrefixes(s)
    return {p for p in Ps if p[-1] != rightEdge}

def isProperPrefix(word, prefix):
    PPs = getProperPrefixes(word)
    return prefix in PPs

def hasAsPrefix(word, prefix):
    if type(prefix) == str:
        prefix_t = ds2t(prefix)
    elif type(prefix) == tuple:
        prefix_t = prefix
    else:
        raise Exception('prefix should be a dotted string or a tuple.')
    if type(word) == str:
        word_t = ds2t(word)
    elif type(word) == tuple:
        word_t = word
    else:
        raise Exception('word should be a dotted string or a tuple.')
    
    l = len(prefix_t)
    return word_t[0:l] == prefix_t

def wordsWithPrefix(p, Ws):
    return {w for w in Ws if hasAsPrefix(w, p)}



def d_s(x, y):
    '''
    Hamming distance between symbol x and symbol y.
    '''
    return x != y

def d_h(u, v):
    '''
    Hamming distance between strings u and v.
    '''
    u_t = ds2t(u)
    v_t = ds2t(v)
    if len(u_t) != len(v_t):
        return np.infty
    return sum(tuple(starmap(d_s, zip(u_t,v_t))))

def hamming_neighbors(s, W):
    '''
    Returns the strings of W that are exactly Hamming distance 1 from s.
    '''
    return h_sphere(1, s, W)

def h_sphere(k, s, W, exclude_s = False):
    '''
    Returns the strings of W that are exactly Hamming distance k from s.
    '''
    sphere = {v for v in W if d_h(s,v) == k}
    if exclude_s:
        return sphere - {s}
    return sphere

def h_neighborhood(k, s, W, exclude_s = False):
    '''
    Returns all strings of W whose Hamming distance from s is <= k.
    '''
    N = {v for v in W if d_h(s,v) <= k}
    if exclude_s:
        return N - {s}
    return N

def getSpheres(s, W):
    '''
    Returns a mapping from [0,len(s)-1] to the corresponding 
    Hamming spheres of s in W.
    '''
    D = range(len(ds2t(s)))
    spheres = {d:h_sphere(d, s, W) for d in D}
    return spheres

def neighborhood_measures(k, s, W, M, exclude_s = False):
    '''
    Applies a measure M (dictionary) to each of the k-neighbors
    of s in W.
    '''
    N = h_neighborhood(k, s, W, exclude_s)
    Ms = {v:M[v] for v in N}
    return Ms

def are_k_cousins(prefix, wordform, k, prefixes, exactlyK = True):
    if exactlyK:
        k_cousins = h_sphere(k, prefix, prefixes)
    else:
        k_cousins = h_neighborhood(k, prefix, prefixes)
    prefixesOfw = getPrefixes(wordform)
    return any(p in k_cousins for p in prefixesOfw)

def get_k_cousins(prefix, k, Ws, prefixes, exactlyK = True):
    if exactlyK:
        k_cousins = h_sphere(k, prefix, prefixes)
    else:
        k_cousins = h_neighborhood(k, prefix, prefixes)
    return {w for w in Ws if any(p in k_cousins for p in getPrefixes(w))}

def count_k_cousins(prefix, k, Ws, prefixes, exactlyK = True):
    if exactlyK:
        k_cousins = h_sphere(k, prefix, prefixes)
    else:
        k_cousins = h_neighborhood(k, prefix, prefixes)
    return len({w for w in Ws if any(p in k_cousins for p in getPrefixes(w))})

# def hamming_neighbors(s, W, withSameLength=None):
#     '''
#     Returns the strings of W that are exactly Hamming distance 1 from s.
#     '''
#     if withSameLength is None:
#         my_l = len(ds2t(s))
#         withSameLength = {v for v in W if len(ds2t(v)) == my_l}
#     return h_sphere(1, s, W, withSameLength=withSameLength)

# def h_sphere(k, s, W, exclude_s = False, withSameLength=None):
#     '''
#     Returns the strings of W that are exactly Hamming distance k from s.
#     '''
#     if withSameLength is None:
#         my_l = len(ds2t(s))
#         withSameLength = {v for v in W if len(ds2t(v)) == my_l}
    
#     sphere = {v for v in withSameLength if d_h(s,v) == k}
# #     sphere = {v for v in W if d_h(s,v) == k}
#     if exclude_s:
#         return sphere - {s}
#     return sphere

# def h_neighborhood(k, s, W, exclude_s = False, withSameLength=None):
#     '''
#     Returns all strings of W whose Hamming distance from s is <= k.
#     '''
#     if withSameLength is None:
#         my_l = len(ds2t(s))
#         withSameLength = {v for v in W if len(ds2t(v)) == my_l}
    
#     N = {v for v in withSameLength if d_h(s,v) <= k}
# #     N = {v for v in W if d_h(s,v) <= k}
#     if exclude_s:
#         return N - {s}
#     return N

# def getSpheres(s, W, withSameLength=None):
#     '''
#     Returns a mapping from [0,len(s)-1] to the corresponding 
#     Hamming spheres of s in W.
#     '''
#     if withSameLength is None:
#         my_l = len(ds2t(s))
#         withSameLength = {v for v in W if len(ds2t(v)) == my_l}
        
#     D = range(len(ds2t(s)))
#     spheres = {d:h_sphere(d, s, W, withSameLength=withSameLength) for d in D}
#     return spheres

# def neighborhood_measures(k, s, W, M, exclude_s = False, withSameLength=None):
#     '''
#     Applies a measure M (dictionary) to each of the k-neighbors
#     of s in W.
#     '''
#     if withSameLength is None:
#         my_l = len(ds2t(s))
#         withSameLength = {v for v in W if len(ds2t(v)) == my_l}
        
#     N = h_neighborhood(k, s, W, exclude_s, withSameLength=withSameLength)
#     Ms = {v:M[v] for v in N}
#     return Ms

# def are_k_cousins(prefix, wordform, k, prefixes, exactlyK = True, withSameLength=None):
#     prefixesOfw = getPrefixes(wordform)
#     my_l = len(ds2t(prefix))
    
#     if withSameLength is None:
#         withSameLength = {p for p in prefixes if len(ds2t(p)) == my_l}
        
#     if exactlyK:
#         k_cousins = h_sphere(k, prefix, prefixes, withSameLength=withSameLength)
#         relevant_prefixesOfw = {p for p in prefixesOfw if len(ds2t(p)) == my_l}
#     else:
#         k_cousins = h_neighborhood(k, prefix, prefixes, withSameLength=withSameLength)
#         relevant_prefixesOfw = prefixesOfw
    
#     return any(p in k_cousins for p in relevant_prefixesOfw)

# def get_k_cousins(prefix, k, Ws, prefixes, exactlyK = True, withSameLength=None):
#     my_l = len(ds2t(prefix))
    
#     if withSameLength is None:        
#         withSameLength = {p for p in prefixes if len(ds2t(p)) == my_l}
    
#     if exactlyK:
#         k_cousins = h_sphere(k, prefix, prefixes, withSameLength=withSameLength)
#         relevant_prefixesOfW = {w:{p for p in getPrefixes(w) if len(ds2t(p)) == my_l}
#                                 for w in Ws}
#     else:
#         k_cousins = h_neighborhood(k, prefix, prefixes, withSameLength=withSameLength)
#         relevant_prefixesOfW = {w:getPrefixes(w) for w in Ws}
        
#     return {w for w in Ws if any(p in k_cousins for p in relevant_prefixesOfW[w])}

# def count_k_cousins(prefix, k, Ws, prefixes, exactlyK = True, withSameLength=None):
#     my_l = len(ds2t(prefix))
    
#     if withSameLength is None:
#         withSameLength = {p for p in prefixes if len(ds2t(p)) == my_l}
    
#     if exactlyK:
#         k_cousins = h_sphere(k, prefix, prefixes, withSameLength=withSameLength)
# #         relevant_prefixesOfw = {p for p in prefixesOfw if len(ds2t(p)) == my_l}
#         relevant_prefixesOfW = {w:{p for p in getPrefixes(w) if len(ds2t(p)) == my_l}
#                         for w in Ws}
#     else:
#         k_cousins = h_neighborhood(k, prefix, prefixes, withSameLength=withSameLength)
#         relevant_prefixesOfW = {w:getPrefixes(w) for w in Ws}
        
#     return len({w for w in Ws if any(p in k_cousins for p in relevant_prefixesOfW[w])})


#'string' rather than 'word' because we also will want this
# for use with prefixes; other code that uses the term 'word'
# is specific to *words* because of edges
def stringLengths(L, includingEdges = False):
    if includingEdges:
        return {len(ds2t(s)) for s in L}
    L_no_edges = {trimBoundariesFromSequence(s) for s in L}
    return stringLengths(L_no_edges, includingEdges = True)

def LbyLength(L, includingEdges = False):
    lengths = stringLengths(L, includingEdges=includingEdges)
#     if includingEdges:
#         my_L = L
#     else:
#         my_L = {trimBoundariesFromSequence(s) for s in L}
    l_to_s = {l:set() for l in lengths}
    for s in L:
        if includingEdges:
            my_s = s
        else:
            my_s = trimBoundariesFromSequence(s)
        my_l = len(ds2t(my_s))
        l_to_s[my_l].add(s)
    return l_to_s

def wordformsOfLength(l, Ws, includingEdges = False):
    #Ws assumed to have word edges
    if includingEdges:
        return {w for w in Ws if len(ds2t(w)) == l}
    return {w for w in Ws if (len(ds2t(w)) + 2) == l}

def wordformsAtLeastLlong(l, Ws, includingEdges = False):
    #Ws assumed to have word edges
#     maxL = len( ds2t(sorted(list(Ws), key=len, reverse=True)[0]) )
    if includingEdges:
#         maxL = max(wordlengthsInclEdges)
        return {w for w in Ws if len(ds2t(w)) >= l}
#         return union([wordformsOfLength(eachl, Ws, includingEdges) for eachl in range(l, maxL+1)])
    if not includingEdges:
#         maxL = max(wordlengthsNotIncludingEdges)
#         maxL = maxL - 2
        return {w for w in Ws if (len(ds2t(w)) - 2) >= l}
#         return union([wordformsOfLength(eachl, Ws, includingEdges) for eachl in range(l, maxL+1)])
    
def getWordformsWithx(x, Ws):
    return {w for w in Ws if x in ds2t(w)}

def wordsWhereXiIs(x, i, Ws):
#     wordsWithX = xToWs[x]
    wordsWithX = getWordformsWithx(x, Ws)
    ws = set(map(ds2t, wordsWithX))
    return {t2ds(w) for w in ws if i <= len(w) - 1 and w[i] == x}


def rev(t):
    return tuple(reversed(t))

def seqsToIndexMap(seqs):
    '''
    Given a collection (of sequences) S, this function:
      1. sorts the collection
      2. returns a dictionary mapping elements of S to 
          their index in the sorted version of S.
    '''
    sorted_seqs = sorted(seqs)
    myIndexMap = dict(map(rev, enumerate(sorted_seqs)))
    return myIndexMap

def indexToSeqMap(seqs):
    '''
    Given a collection (of sequences) S, this function:
      1. sorts the collection
      2. returns a dictionary mapping an index of the sorted
         collection to the corresponding element of S.
    '''
    sorted_seqs = sorted(seqs)
    mySeqMap = dict(enumerate(sorted_seqs))
    return mySeqMap

def areInverses(dictA, dictB):
    return all(dictB[dictA[k]] == k for k in dictA)

def seqMapToOneHots(seqMap):
    '''
    Given a dict mapping elements of a collection (of sequences)
    S to their index in a sorted version of S, where |S| = n
    this function constructs and returns a square (n,n) matrix where 
    row/column i represents the one-hot vector for element i of
    the sorted version of S.
    '''
    n = len(seqMap.keys())
    
    #For each seq, we want a OH vector.
    #
    #That OH vector has to have 
    # the same number of elements as 
    # there are seqs.
    one_hots = np.zeros((n,n))
    
    for (seq, idx) in seqMap.items():
        one_hots[idx][idx] = 1.0
    return one_hots

def seqToOneHot(seq, seqMap, one_hots):
    return one_hots[seqMap[seq]]

def seqsToOneHotMap(seqs):
    '''
    Given a collection (of sequences) S, this function
    returns a dictionary mapping elements of S to their
    natural one-hot vector.
    '''
    seqMap = seqsToIndexMap(seqs)
    one_hots = seqMapToOneHots(seqMap)
    return {seq:one_hots[seqMap[seq]]
            for seq in seqMap}

def oneHotToSeqMap(seqs):
    '''
    Given a collection (of sequences) S, this function
    returns a function mapping a one-hot vector to its
    corresponding element of S.
    '''
    sorted_seqs = sorted(seqs)
#     seqsToOHmap = seqsToOneHotMap(seqs)
#     seqsToOHmap_t = mapValues(tuple, seqsToOHmap)
#     OHtoSeqs = dict(map(rev, seqsToOHmap_t.items()))
    def OHtoSeq(OH_vector):
        seq_idx = OH_vector.nonzero()[0].item()
        return sorted_seqs[seq_idx]
#         OH_t = tuple(OH_vector)
#         return OHtoSeqs[OH_t]
    return OHtoSeq

# def oneHotToSeqMap(seqs):
#     '''
#     Given a collection (of sequences) S, this function
#     returns a function mapping a one-hot vector to its
#     corresponding element of S.
#     '''
#     sorted_seqs = sorted(seqs)
#     seqsToOHmap = seqsToOneHotMap(seqs)
#     seqsToOHmap_t = mapValues(tuple, seqsToOHmap)
#     OHtoSeqs = dict(map(rev, seqsToOHmap_t.items()))
#     def OHtoSeq(OH_vector):
#         OH_t = tuple(OH_vector)
#         return OHtoSeqs[OH_t]
#     return OHtoSeq

def seqStackToIndexStack(seqStack, seqToIndexMap):
    '''
    Given 
     - a mapping seqToIndexMap from elements of a collection S
       to their indices in a sorted version of S
     - a finite sequence of elements of S
    
    this returns an array that maps seqToIndexMap over the sequence.
    '''
    return np.array(lmap(lambda seq: seqToIndexMap[seq], seqStack))

def seqStackToOHstack(seqStack, seqToOHmap):
    '''
    Given 
     - a mapping seqToOHmap from elements of a collection S
       to their one-hot vectors
     - a finite sequence of elements of S
    
    this returns an array that maps seqToOHmap over the sequence.
    '''
    return np.array(lmap(lambda seq: seqToOHmap[seq], seqStack))

def OHstackToSeqStack(OHstack, OHtoSeqMap):
    '''
    Given
     - a function mapping one-hot vectors to elements of a collection S
     - a finite sequence of one-hot vectors
     
    this returns a corresponding list of elements of S.
    '''
    return lmap(OHtoSeqMap, OHstack)