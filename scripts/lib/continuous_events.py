#!/usr/bin/env python3
"""Generic continuous-event utilities and tests; intentionally domain-neutral."""
from __future__ import annotations
from typing import Callable

def bisection_root(fn: Callable[[float], float], lo: float, hi: float, tol: float = 1e-9) -> float:
    flo, fhi = fn(lo), fn(hi)
    if flo == 0: return lo
    if fhi == 0: return hi
    if flo * fhi > 0: raise ValueError("root is not bracketed")
    for _ in range(200):
        mid=(lo+hi)/2; fm=fn(mid)
        if hi-lo <= tol:return mid
        if flo*fm <= 0:hi,fhi=mid,fm
        else:lo,flo=mid,fm
    return (lo+hi)/2

def merge_intervals(intervals, eps=1e-12):
    out=[]
    for a,b in sorted((float(a),float(b)) for a,b in intervals if b>a):
        if not out or a>out[-1][1]+eps:out.append([a,b])
        else:out[-1][1]=max(out[-1][1],b)
    return [(a,b) for a,b in out]

def interval_union_length(intervals):return sum(b-a for a,b in merge_intervals(intervals))
