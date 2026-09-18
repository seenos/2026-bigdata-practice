"""Task 1: Jaccard similarity, MinHash, and LSH."""

import argparse

# Textbook example and verification harness from the course starter file:
# https://github.com/codingchild2424/2026-lecture-bigdata-practice/blob/main/w03-lsh/task1_minhash.py
BOOK = [[1, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
        [0, 0, 1, 0]]
BOOK_HASHES = [lambda r: (r + 1) % 5, lambda r: (3 * r + 1) % 5]


def jaccard(a, b):
    """Return intersection size / union size for sets; empty union gives 0."""
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def minhash_signatures(columns, hashes, n_rows):
    """Return one signature per column using a single pass over row numbers.

    columns contains sets of row numbers; hashes contains hash functions.
    Empty columns retain infinity in every signature position.
    """
    signatures = [[float("inf")] * len(hashes) for _ in columns]

    for r in range(n_rows):
        # Compute each hash once per row and reuse it across columns.
        hash_values = [h(r) for h in hashes]
        for c, column in enumerate(columns):
            if r in column:
                for i, value in enumerate(hash_values):
                    signatures[c][i] = min(signatures[c][i], value)

    return signatures


def lsh_candidates(signatures, bands):
    """Return pairs (i, j), i < j, matching in at least one band.

    Require positive, equal signature lengths divisible by bands.
    Reject leftover rows with ValueError rather than discarding them.
    """
    if not isinstance(bands, int) or isinstance(bands, bool) or bands <= 0:
        raise ValueError("bands must be a positive integer")
    if not signatures:
        return set()

    length = len(signatures[0])
    if any(len(signature) != length for signature in signatures):
        raise ValueError("all signatures must have the same length")
    if length == 0 or length % bands != 0:
        raise ValueError("signature length must be positive and divisible by bands")

    rows_per_band = length // bands
    candidates = set()
    for band in range(bands):
        start = band * rows_per_band
        buckets = {}
        for j, signature in enumerate(signatures):
            key = tuple(signature[start:start + rows_per_band])
            bucket = buckets.setdefault(key, [])
            for i in bucket:
                candidates.add((i, j))
            bucket.append(j)

    return candidates


def columns_from_matrix(matrix):
    n_rows, n_cols = len(matrix), len(matrix[0])
    return [{r for r in range(n_rows) if matrix[r][c]} for c in range(n_cols)]


def verify():
    fails = 0

    def check(label, got, want):
        nonlocal fails
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<44} {got}"
              + ("" if ok else f"\n{'':>54}want {want}"))
        fails += not ok

    cols = columns_from_matrix(BOOK)
    try:
        check("jaccard(S1, S4)", round(jaccard(cols[0], cols[3]), 4), round(2 / 3, 4))
        check("jaccard(S1, S2)", jaccard(cols[0], cols[1]), 0.0)
        check("jaccard on empty sets", jaccard(set(), set()), 0)
    except NotImplementedError:
        print("  jaccard is still a stub")
        return 1
    try:
        sig = minhash_signatures(cols, BOOK_HASHES, len(BOOK))
    except NotImplementedError:
        print("  minhash_signatures is still a stub")
        return 1

    check("signature of S1", sig[0], [1, 0])
    check("signature of S2", sig[1], [3, 2])
    check("signature of S3", sig[2], [0, 0])
    check("signature of S4", sig[3], [1, 0])
    try:
        cands = lsh_candidates([[1, 0], [3, 2], [0, 0], [1, 0]], bands=2)
    except NotImplementedError:
        print("  lsh_candidates is still a stub")
        return 1
    check("S1 and S4 are candidates", (0, 3) in cands, True)
    check("S1 and S2 are not", (0, 1) in cands, False)
    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    if not fails:
        print("  Note that S1 and S4 agree in both signature positions, which "
              "estimates\n  their similarity as 1.0 when it is actually 2/3. "
              "Two hashes is not many.")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
