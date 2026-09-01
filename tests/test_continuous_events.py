#!/usr/bin/env python3
from __future__ import annotations
import json, tempfile, unittest
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from lib.continuous_events import bisection_root, merge_intervals, interval_union_length

class ContinuousEventTests(unittest.TestCase):
    def test_narrow_event_inside_two_samples(self):
        # A reusable event contract must not assume a sample hits the event.
        left=bisection_root(lambda x:(x-0.49)*(x-0.51),0.0,0.5)
        right=bisection_root(lambda x:(x-0.49)*(x-0.51),0.5,1.0)
        self.assertAlmostEqual(left,0.49,places=7);self.assertAlmostEqual(right,0.51,places=7)
    def test_endpoint_and_touching_intervals(self):
        self.assertEqual(merge_intervals([(0,1),(1,2),(2,2)]),[(0,2)])
    def test_overlapping_union(self):
        self.assertAlmostEqual(interval_union_length([(0,2),(1,3),(5,6)]),4.0)
    def test_non_bracketed_root_rejected(self):
        with self.assertRaises(ValueError):bisection_root(lambda x:x*x+1,-1,1)

if __name__=='__main__':unittest.main()
