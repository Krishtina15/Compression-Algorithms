import heapq


class Node:
    def __init__(self, char, freq, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right

    def __lt__(self, other):
        return self.freq < other.freq


def build_tree(text):
    freq = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1

    heap = [Node(ch, f) for ch, f in freq.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)

    return heap[0]


def build_codes(node, prefix="", codebook=None):
    if codebook is None:
        codebook = {}
    if node is None:
        return codebook
    if node.char is not None:
        codebook[node.char] = prefix or "0"
        return codebook
    build_codes(node.left, prefix + "0", codebook)
    build_codes(node.right, prefix + "1", codebook)
    return codebook


def print_tree(node, prefix="", is_left=True):
    if node is None:
        return
    label = f"'{node.char}'({node.freq})" if node.char is not None else f"({node.freq})"
    print(prefix + ("├── " if is_left else "└── ") + label)
    new_prefix = prefix + ("│   " if is_left else "    ")
    print_tree(node.left, new_prefix, True)
    print_tree(node.right, new_prefix, False)


def encode(text, codebook):
    return "".join(codebook[ch] for ch in text)


def decode(bits, root):
    result = []
    node = root
    for bit in bits:
        node = node.left if bit == "0" else node.right
        if node.char is not None:
            result.append(node.char)
            node = root
    return "".join(result)


if __name__ == "__main__":
    text = input("Enter text to compress: ")

    root = build_tree(text)
    codebook = build_codes(root)
    encoded = encode(text, codebook)
    decoded = decode(encoded, root)

    print("\nHuffman Tree:")
    print_tree(root)

    print("\nCodes:")
    for ch, code in sorted(codebook.items()):
        display = repr(ch) if ch in (" ", "\n", "\t") else ch
        print(f"  {display}: {code}")

    print(f"\nOriginal text:   {text}")
    print(f"Original bits:   {len(text) * 8} (8 bits/char)")
    print(f"Encoded bits:    {len(encoded)}")
    print(f"Encoded string:  {encoded}")
    print(f"Decoded text:    {decoded}")
    print(f"Match original:  {decoded == text}")