#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import getopt
import itertools
from collections import defaultdict

REGEX_MATCHER = {    
    '*': '.*',
    '+': '.+'
}


def best_match(pattern_fields):

    _best_match, _highest_score = None, None
    for pattern in pattern_fields:
        _index_sum = [1 if p != '*' else 0 for p in pattern.split(',')]

        _sum_index, _sum_highest = sum(_index_sum), sum(_highest_score or [])
        if not _highest_score or _sum_index > _sum_highest:
            _highest_score = _index_sum
            _best_match = pattern
        elif _sum_index == _sum_highest:
            for a, b in zip(_index_sum, _highest_score):
                if a or b and not a == b:
                    if a > b:
                        _highest_score = _index_sum
                        _best_match = pattern
                    break

    return _best_match


class PatternMatcher(object):

    """
    The mapping is stored as:

    defaultdict( <type 'list'> , {
        3: [('*,b,*', [
                ('*', <_sre.SRE_Pattern object at 0x105d757b0> ),
                ('b', < _sre.SRE_Pattern object at 0x105d47608 > ),
                ('*', < _sre.SRE_Pattern object at 0x105d757b0 > )]),
            ('a,*,*', [
                ('a', < _sre.SRE_Pattern object at 0x105d47690 > ),
                ('*', < _sre.SRE_Pattern object at 0x105d757b0 > ),
                ('*', < _sre.SRE_Pattern object at 0x105d757b0 > )]),
            ('*,*,c', [('*', < _sre.SRE_Pattern object at 0x105d757b0 > ),
                ('*', < _sre.SRE_Pattern object at 0x105d757b0 > ),
                ('c', < _sre.SRE_Pattern object at 0x105d47718 > )]),
            ('foo,bar,baz', [('foo', < _sre.SRE_Pattern object at 0x105c63f48 > ),
                             ('bar', < _sre.SRE_Pattern object at 0x105d76030 > ),
                             ('baz', < _sre.SRE_Pattern object at 0x105d760d8 > )])],
    })

    Here, the key '3' is the length of the patterns - example '*,b,*' has length 3
    """

    n_patterns = 0
    compiled_patterns = defaultdict(list)

    def compile_n_patterns(self, patterns, n):

        self.n_patterns = n
        for pattern in patterns:
            pattern = pattern.strip()
            _split = pattern.split(',')

            _compiled_pattern = (
                pattern,
                map(lambda x: (x, re.compile(REGEX_MATCHER.get(x, x))), _split)
            )
            self.compiled_patterns[len(_split)].append(_compiled_pattern)

    def do_match(self, input_str_list):

        _matched_pattern_list, _matched_pattern = [], None
        compiled_patterns = self.compiled_patterns[len(input_str_list)]

        for compiled_pattern in compiled_patterns:
            match_string, _pattern = compiled_pattern
            #Check for exact match
            if all([_string == _pattern_string for _string, (_pattern_string, _)
                    in zip(input_str_list, _pattern)]):
                #Exact match found !
                _matched_pattern = match_string
                break

            elif all([_regex.match(_string) for _string, (_pattern_string, _regex)
                      in zip(input_str_list, _pattern)]):
                #Now make a list of candidates if no exact match to find best match
                _matched_pattern_list.append(match_string)

        if not _matched_pattern:
            #Now look for the best match
            _matched_pattern = best_match(_matched_pattern_list)

        return _matched_pattern


def process_file(input_file):

    _result_set = []
    with open(input_file, 'r+') as fh:

        pattern_matcher = PatternMatcher()
        _result_set = []

        #Fetch the n patterns specified in line #1 of the input file
        _n_patterns = int(fh.readline().strip())

        patterns_list = itertools.islice(fh, _n_patterns)
        pattern_matcher.compile_n_patterns(patterns_list, _n_patterns)

        # This is the count of number of patterns
        _n_strings = fh.next()

        for i, x in enumerate(fh):
            if i == _n_strings:
                #fh[:n] would evaluate, which is not very memory
                #efficient. Hence the if i == n hack.
                break

            _match = pattern_matcher.do_match(x.strip().strip('/').split('/'))
            _result_set.append(_match or 'NO MATCH')

    return _result_set


if __name__ == '__main__':

    result_set = process_file('input.txt')

    _resultset_str = "\n".join(result_set)


    with open('output.txt', 'w+') as out_fh:
        out_fh.write(_resultset_str)


