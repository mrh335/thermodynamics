import math
import multiprocessing

def run_parallel_search():
    # -*- coding: utf-8 -*-
    """
    Created on Sat Apr  5 10:46:47 2025

    @author: markh
    """


    # ---------------- Core Functions ----------------

    def get_nth_permutation(elements, index):
        elements = list(elements)
        n = len(elements)
        permutation = []
        index = index % math.factorial(n)

        for i in range(n):
            f = math.factorial(n - 1 - i)
            pos = index // f
            index %= f
            permutation.append(elements.pop(pos))

        return permutation

    def rank_permutation(perm):
        elements = list(perm)
        n = len(elements)
        available = sorted(elements)
        rank = 0

        for i in range(n):
            pos = available.index(elements[i])
            rank += pos * math.factorial(n - 1 - i)
            available.pop(pos)

        return rank

    def index_to_n_permutations(index, n, k):
        factorial_k = math.factorial(k)
        permutations = []
        base_elements = list(range(k))

        for _ in range(n):
            index, rem = divmod(index, factorial_k)
            perm = get_nth_permutation(base_elements, rem)
            permutations.insert(0, perm)

        return permutations

    def n_permutations_to_index(permutations):
        k = len(permutations[0])
        factorial_k = math.factorial(k)
        index = 0

        for perm in permutations:
            rank = rank_permutation(perm)
            index = index * factorial_k + rank

        return index

    # ---------------- Parallel Evaluation ----------------

    def evaluate_index(args):
        index, n, k, target_score = args
        perms = index_to_n_permutations(index, n, k)
        score = sum(sum(p) for p in perms)

        if score == target_score:
            recovered_index = n_permutations_to_index(perms)
            return {
                "index": index,
                "perms": perms,
                "recovered_index": recovered_index
            }
        return None

    # ---------------- Main Process ----------------

    if __name__ == "__main__":
        n, k = 1, 8  # Keep small for demo
        target_score = 24
        total = math.factorial(k) ** n

        print("Searching in parallel...")
        with multiprocessing.Pool() as pool:
            args_iter = ((i, n, k, target_score) for i in range(total))
            for result in pool.imap_unordered(evaluate_index, args_iter, chunksize=100000):
                if result:
                    print(f"Match found at index {result['index']}")
                    for i, p in enumerate(result['perms']):
                        print(f" Group {i+1}: {p}")
                    print("Recovered index:", result['recovered_index'])
                    print("Match check:", result['index'] == result['recovered_index'])
                    break

if __name__ == "__main__":
    run_parallel_search()