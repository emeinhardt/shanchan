from functools import reduce
from random import choice
from itertools import takewhile, product
import funcy
import json, codecs, csv
import os
# from os.path import isfile
from time import localtime, strftime
from datetime import datetime
import psutil
# from joblib import Parallel, delayed

from string_utils import *


def union(Ss):
    return reduce(set.union, Ss)


# dictionary utilities

def getRandomKey(a_dict, printKey = False):
    randKey = choice(list(a_dict.keys()))
    if printKey:
        print('Random key: {0}'.format(randKey))
    return randKey

def testRandomKey(a_dict, printKey = True, printVal = True):
    randKey = getRandomKey(a_dict)
    if printKey:
        print('Random key: {0}'.format(randKey))
    if printVal:
        print('value ⟶ {0}'.format(a_dict[randKey]))
    return {'key': randKey, 'val': a_dict[randKey]}


# def transpose(d, inner_keys, outer_keys):
#     '''
#     Let 
#         As = {'a0', 'a1'}
#         Bs = {'b0', 'b1'}
#         d = {'a0': {'b0': 0, 'b1': 1}, 
#              'a1': {'b0': 0, 'b1': 1}}
#     Then
#         transpose(d, Bs, As) = 
#         {'b0': {'a1': 0, 'a0': 0}, 'b1': {'a1': 1, 'a0': 1}}
        
#     Alternative schematization: Let
#         f: A ⟶ B = {'a0':'b0','a1':'b1'}
#         g: B ⟶ C = {'b0':0,'b1':1}
#         d: A ⟶ B ⟶ C = g ⚬ f
#     Then 
#         d' = transpose(d, Bs, As) = 
#         d': B ⟶ A ⟶ C = flip(g ⚬ f)
#     '''
#     return {inner_key:{outer_key:d[outer_key][inner_key]
#                      for outer_key in outer_keys if outer_key in d and inner_key in d[outer_key]}
#             for inner_key in inner_keys}


def edit_dict(the_dict, the_key, the_new_value):
    '''
    Composable (because it returns a value) but stateful(= in-place) dictionary update.
    '''
    the_dict.update({the_key: the_new_value})
    return the_dict

def modify_dict(the_dict, the_key, the_new_value):
    '''
    Composable and (naively-implemented) non-mutating dictionary update.
    '''
    new_dict = {k:the_dict[k] for k in the_dict}
    new_dict.update({the_key: the_new_value})
    return new_dict

gtZero = lambda k,v: v > 0.0



# def extract(i, Xs, returnAs='l,t,r', combine=funcy.lconcat):
#     x_i = Xs[i]
#     X_l = Xs[:i]
#     X_r = Xs[i+1:]
#     if returnAs == 'l,t,r':
#         return (X_l, x_i, X_r)
#     elif returnAs == 'l_r':
#         return (X_l, X_r)
#     elif returnAs == 'lr':
#         return combine(X_l, X_r)
#     elif returnAs == 't,l_r':
#         return (x_i, (X_l, X_r))
#     elif returnAs == 'l_r,t':
#         return ((X_l, X_r), x_i)
#     else:
#         raise Exception('wtf')

def ensure_dir_exists(dir_path):
    if dir_path != '' and not os.path.exists(dir_path):
        print(f"Making directory '{dir_path}'")
        os.makedirs(dir_path)

# from os.path import isfile
def exists(fname):
    return os.path.isfile(fname)

def loadTSV_as_dictlist(fp, fieldnames=None):
    rows = []

    with open(fp) as csvfile:
        #quoting and quotechar args here are for dealing with the CMU dictionary
        my_reader = csv.DictReader(csvfile, fieldnames=fieldnames, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='@')
        for row in my_reader:
            #print(row)
            rows.append(row)
    return rows

def saveDictList_as_TSV(fp, dl, fields):
    with open(fp, 'w', newline='\n') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar='@')
        
        writer.writeheader()
        writer.writerows(dl)

def importSeqs(seq_fn, f=None):
    if f is None:
        f = set
    phoneSeqsAsStr = []
    with open(seq_fn, 'r') as the_file:
        for row in the_file:
            phoneSeqsAsStr.append(row.rstrip('\r\n'))
    return f(phoneSeqsAsStr)

def exportSeqs(seq_fn, seqs):
    with open(seq_fn, 'w') as the_file:
        for seq in seqs:
            the_file.write(seq + '\n')

def exportDict(fn, d):
    with codecs.open(fn, 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii = False, indent = 4)
        
def importDict(fn):
    with open(fn, encoding='utf-8') as data_file:
        d_in = json.loads(data_file.read())
    return d_in


def exportMatrixMetadata(md_fp, matrix_fp, matrix, dim_md, step_name, nb_name, other_md):
    md = {'matrix fp':matrix_fp,
          'matrix shape':matrix.shape if matrix is not None else 'N/A',
          'Produced in step':step_name,
          'Produced in notebook':nb_name}
    md.update(dim_md)
    md.update(other_md)
    exportDict(md_fp, md)
    print(f'Wrote metadata for \n\t{matrix_fp}\n to \n\t{md_fp}')


# def torch_nbytes(t): #nottttt sure I trust this does what I thought it ought to
#     return t.element_size() * t.nelement()
    
def castValuesToSets(d):
    return {k:set(d[k]) for k in d}

def castSetValuesToTuples(d):
    return {k:tuple(d[k]) for k in d}

# adapted from https://stackoverflow.com/a/32009595
def toHuman(size, precision=2, asString=True):
    suffixes=['B','KB','MB','GB','TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1 #increment the index of the suffix
        size = size/1024.0 #apply the division
    if asString:
        return "%.*f%s"%(precision,size,suffixes[suffixIndex])
    return size

# adapted from https://stackoverflow.com/a/32009595
def bytesTo(size_bytes, scale='GB'):
    scales = ('B', 'KB', 'MB', 'GB', 'TB')
    assert scale in scales, f'scale must be one of {scales}, got {scale} instead.'
    scaleIndex = scales.index(scale)
    return size_bytes / (1024 ** scaleIndex)


def memTotal(units='GB'):
    return bytesTo(psutil.virtual_memory().total, units)


def memAvailable(units='GB'):
    return bytesTo(psutil.virtual_memory().available, units)


def memUsed(units='GB'):
    return bytesTo(psutil.virtual_memory().used, units)


def memTrigger(mem_left_trigger_GB=2.0):
    if memAvailable() <= mem_left_trigger_GB:
        raise MemoryError(f"Less than {mem_left_trigger_GB} left!")

def memDiff(m0, m1):
    return m1 - m0
        

# Parallel dictionary definition and data processing w/ progress reports


# from time import localtime, strftime
def stamp(include_date=False):
    if include_date:
        return strftime('%Y-%m-%d %H:%M:%S', localtime())
    return strftime('%H:%M:%S', localtime())

def stampedNote(note, printResult=True, returnResult=False, log_fp=None, log_f=None):
    result = '{0} @ {1}'.format(note, stamp())
    if printResult:
        if log_fp is None and log_f is None:
            print(result)
        elif log_f is not None:
            print(result, file=log_f)
        else:
            with open(log_fp, 'a') as f:
                print(result, file=f)
    if returnResult:
        return result
       

def startNote(note=None):
    if note is None:
        note = ''
    stampedNote('Start ' + note)
    
def endNote(note=None):
    if note is None:
        note = ''
    stampedNote('End ' + note)

def timeDiff(t0_string, t1_string, asSeconds=True):
    if '-' not in t0_string and '-' not in t1_string:
        FMT = '%H:%M:%S'
        tDelta = datetime.strptime(t1_string, FMT) - datetime.strptime(t0_string, FMT)
    elif '-' in t0_string and '-' in t1_string:
        FMT = '%Y-%m-%d %H:%M:%S'
        tDelta = datetime.strptime(t1_string, FMT) - datetime.strptime(t0_string, FMT)
    else:
        raise Exception('Either both date-time strings should include times AND dates or just times')
    if not asSeconds:
        return tDelta
    return tDelta.total_seconds()

def stampedMemNote(msg='', units='GB', includeGPU=False, printResult=True, returnResult=False, log_fp=None, log_f=None):
    mem_usage = 'VM used vs. available: {0:.2f}{2} vs. {1:.2f}{2}'.format(memUsed(units), memAvailable(units), units)
    if includeGPU:
#         g_info = gpuMem()
#         total, alloc, cached = g_info['total'], g_info['allocated'], g_info['cached']
#         gpu_usage = 'GPU mem allocated, cached, total: {0:.2f}MB vs. {1:.2f}MB vs. {1:.2f}MB'.format(alloc, cached, total)
        pass
    if msg == '':
        if returnResult:
            return stampedNote(mem_usage, printResult=printResult, returnResult=returnResult, log_fp=log_fp, log_f=log_f)
        else:
            stampedNote(mem_usage, printResult=printResult, returnResult=returnResult, log_fp=log_fp, log_f=log_f)
#         if g and includeGPU:
#             print(gpu_usage)
        
    if returnResult:
        stamped_msg = stampedNote(msg, printResult=printResult, returnResult=returnResult, log_fp=log_fp, log_f=log_f)
        mem_msg = '\t'+mem_usage
        if printResult:
            if log_fp is None and log_f is None:
                print(mem_msg)
            elif log_f is not None:
                print(mem_msg, file=log_f)
            else:
                with open(log_fp, 'a') as f:
                    print(mem_msg, file=f)
        total_msg = stamped_msg + '\n' + mem_msg
        return total_msg
    else:
        stampedNote(msg, printResult=printResult, returnResult=returnResult, log_fp=log_fp, log_f=log_f)
        if log_fp is None and log_f is None:
            print('\t'+mem_usage)
        elif log_f is not None:
            print('\t'+mem_usage, file=log_f)
        else:
            with open(log_fp, 'a') as f:
                print('\t'+mem_usage, file=f)
    
    
# def processDataWProgressUpdates(f, data):
#     print('Start @ {0}'.format(stamp()))
#     l = len(data)
#     benchmarkPercentages = [1,2,3,5,10,20,30,40,50,60,70,80,90,95,96,97,98,99,100]
#     benchmarkIndices = [round(each/100.0 * l) for each in benchmarkPercentages]
#     for i, d in enumerate(data):
#         if i in benchmarkIndices:
#             print('{0} | {0}/{1} = {2} | {3} | {4}'.format(i, l, i/l, d, stamp()))
#         f(d)
#     print('Finish @ {0}'.format(stamp()))
        
# def constructDictWProgressUpdates(f, data, a_dict):
#     def g(d):
#         a_dict.update({d:f(d)})
#     processDataWProgressUpdates(g, data)
    
# def parallelDictDefinition(f, data, jobs, backend="multiprocessing", verbosity=5):
#     def g(d):
#         return (d, f(d))
#     return dict( Parallel(n_jobs=jobs, backend=backend, verbose=verbosity)(delayed(g)(d) for d in data) )


