"""
Day 12 - Data Structures & Algorithms
Task: Trie-based autocomplete with frequency ranking (variant 12)
"""

from __future__ import annotations
import argparse


class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.end = False
        self.freq = 0


class Trie:
    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            node = node.children.setdefault(ch, TrieNode())
        node.end = True
        node.freq += 1

    def suggest(self, prefix: str, limit: int = 5) -> list[tuple[str, int]]:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return []
            node = node.children[ch]
        out: list[tuple[str, int]] = []
        self._dfs(node, prefix, out)
        out.sort(key=lambda x: (-x[1], x[0]))
        return out[:limit]

    def _dfs(self, node: TrieNode, cur: str, out: list[tuple[str, int]]) -> None:
        if node.end:
            out.append((cur, node.freq))
        for ch, nxt in node.children.items():
            self._dfs(nxt, cur + ch, out)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="net")
    args = parser.parse_args()
    trie = Trie()
    for word in ["network", "netcode", "netcat", "nested", "node", "network", "netcode", "next"]:
        trie.insert(word)
    print("Suggestions:", trie.suggest(args.prefix))


if __name__ == "__main__":
    main()
