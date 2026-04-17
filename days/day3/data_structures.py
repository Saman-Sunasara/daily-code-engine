"""
Day 3 - Data Structures & Algorithms
Task: Segment tree with lazy propagation
"""

from __future__ import annotations
import argparse


class SegmentTree:
    def __init__(self, data: list[int]) -> None:
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        self._build(1, 0, self.n - 1, data)

    def _build(self, node: int, left: int, right: int, data: list[int]) -> None:
        if left == right:
            self.tree[node] = data[left]
            return
        mid = (left + right) // 2
        self._build(node * 2, left, mid, data)
        self._build(node * 2 + 1, mid + 1, right, data)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def _push(self, node: int, left: int, right: int) -> None:
        if self.lazy[node] != 0:
            self.tree[node] += (right - left + 1) * self.lazy[node]
            if left != right:
                self.lazy[node * 2] += self.lazy[node]
                self.lazy[node * 2 + 1] += self.lazy[node]
            self.lazy[node] = 0

    def update_range(self, ql: int, qr: int, delta: int) -> None:
        self._update(1, 0, self.n - 1, ql, qr, delta)

    def _update(self, node: int, left: int, right: int, ql: int, qr: int, delta: int) -> None:
        self._push(node, left, right)
        if qr < left or right < ql:
            return
        if ql <= left and right <= qr:
            self.lazy[node] += delta
            self._push(node, left, right)
            return
        mid = (left + right) // 2
        self._update(node * 2, left, mid, ql, qr, delta)
        self._update(node * 2 + 1, mid + 1, right, ql, qr, delta)
        self.tree[node] = self.tree[node * 2] + self.tree[node * 2 + 1]

    def query_range(self, ql: int, qr: int) -> int:
        return self._query(1, 0, self.n - 1, ql, qr)

    def _query(self, node: int, left: int, right: int, ql: int, qr: int) -> int:
        self._push(node, left, right)
        if qr < left or right < ql:
            return 0
        if ql <= left and right <= qr:
            return self.tree[node]
        mid = (left + right) // 2
        return self._query(node * 2, left, mid, ql, qr) + self._query(node * 2 + 1, mid + 1, right, ql, qr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arr", nargs="*", type=int, default=[2, 1, 3, 4, 5, 2, 6])
    args = parser.parse_args()
    seg = SegmentTree(args.arr)
    print("Initial sum [1,5] =", seg.query_range(1, 5))
    seg.update_range(2, 4, 3)
    print("After +3 on [2,4], sum [1,5] =", seg.query_range(1, 5))


if __name__ == "__main__":
    main()
