#!/usr/bin/env python3
"""Week 6 · Task 3 — Make pass two fit.

Textbook §6.3 (PCY), §6.3.2 - §6.3.4.

`PlainApriori` does what Task 1 asked: use pass one to drop infrequent items,
then count every pair of surviving items. That is already much better than
counting all pairs. It is still not enough, because the surviving items are the
common ones, and the common ones appear together constantly.

The harness measures **the peak number of pair counters you held**, because
that is the thing that decides whether the algorithm runs at all. §6.3 is about
spending pass one's spare memory to shrink it.

    python3 bench.py
    python3 bench.py --yours

Correctness first: you must find exactly the same frequent pairs. Finding fewer
is not an optimisation.
"""
from collections import Counter
from itertools import combinations
from array import array
import sys


class PlainApriori:
    """Pass one drops infrequent items. Pass two counts every surviving pair."""

    def __init__(self, support):
        self.support = support
        self.peak_counters = 0

    def run(self, baskets):
        counts = Counter()
        for basket in baskets:
            counts.update(basket)
        frequent = {i for i, c in counts.items() if c >= self.support}

        pair_counts = Counter()
        for basket in baskets:
            items = sorted(basket & frequent)
            for pair in combinations(items, 2):
                pair_counts[pair] += 1
            self.peak_counters = max(self.peak_counters, len(pair_counts))

        return {frozenset(p): c for p, c in pair_counts.items()
                if c >= self.support}


class YourAlgorithm:
    """Your frequent-pair finder.

        __init__(support)
        run(baskets) -> {frozenset({a, b}): count}
        .peak_counters -> the most pair counters you ever held at once

    Same pairs as the baseline. Fewer counters.

    Pass one only needs one integer per item, and there are not many items. The
    rest of your memory is sitting idle while you do it. §6.3 spends it: hash
    every pair you see in pass one into a fixed array of buckets, and count the
    buckets rather than the pairs.

    A bucket whose total is below the support threshold cannot contain a
    frequent pair. In pass two you skip every pair landing in such a bucket -
    and the bucket array collapses to a bitmap, one bit each, before you need
    the memory for counters.

    Two things to be careful of:

      * a bucket being frequent does not make its pairs frequent. It is a
        filter, not an answer
      * `peak_counters` is on your honour. Count the pair counters you hold at
        the same time. The bitmap is not a pair counter, but if you keep the
        full bucket counts alive into pass two, that is not free either -
        observation.md asks about it
    """

    def __init__(self, support, buckets=1 << 20):
        if not isinstance(support, int) or not 1 <= support <= 0xffffffff:
            raise ValueError("support must fit a positive uint32")
        if not isinstance(buckets, int) or buckets < 1:
            raise ValueError("buckets must be positive")
        self.support, self.buckets = support, buckets
        self.peak_counters = 0

    def _bucket(self, pair):
        # Stable for the integer item IDs supplied by the course generator.
        a, b = pair
        value = (a * 0x9e3779b1) ^ (b * 0x85ebca77)
        value ^= value >> 16
        return value % self.buckets

    def run(self, baskets):
        if iter(baskets) is baskets:
            raise TypeError("baskets must support two passes")
        self.peak_counters = 0
        counts = Counter()
        buckets = array('I', [0]) * self.buckets
        self.bucket_array_bytes = sys.getsizeof(buckets)
        for basket in baskets:
            items = sorted(set(basket))
            counts.update(items)
            for pair in combinations(items, 2):
                slot = self._bucket(pair)
                # Only whether the count reaches support matters to the filter.
                if buckets[slot] < self.support:
                    buckets[slot] += 1
        frequent = {i for i,c in counts.items() if c >= self.support}
        del counts
        bitmap = bytearray((self.buckets + 7) // 8)
        self.frequent_buckets = 0
        for slot, count in enumerate(buckets):
            if count >= self.support:
                bitmap[slot // 8] |= 1 << (slot % 8)
                self.frequent_buckets += 1
        self.bitmap_bytes = sys.getsizeof(bitmap)
        del buckets  # Release integer counters before allocating pair counters.
        pair_counts = Counter()
        for basket in baskets:
            items = sorted(set(basket) & frequent)
            for pair in combinations(items, 2):
                slot = self._bucket(pair)
                if bitmap[slot // 8] & (1 << (slot % 8)):
                    pair_counts[pair] += 1
        self.counted_pairs = len(pair_counts)
        result = {frozenset(p):c for p,c in pair_counts.items() if c>=self.support}
        # Conservatively include both dictionaries while constructing output.
        self.peak_counters = self.counted_pairs + len(result)
        return result
