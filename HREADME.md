# Huffman Coding Compressor

A web application that compresses text files using **Huffman Coding**, built with Python and Flask.

## What is Huffman Coding?

Huffman coding is a lossless compression algorithm that assigns shorter binary codes to frequently occurring characters and longer codes to rare ones, instead of using a fixed number of bits per character (like standard 8-bit ASCII).

```
Input:    AAAABBBCCD
Frequencies: A=4, B=3, C=2, D=1
Codes:       A=0, B=10, C=110, D=111
Output:   0000 10 10 10 110 110 111   (21 bits instead of 80)
```

It builds a binary tree (the "Huffman tree") from character frequencies, then walks the tree to assign each character a unique bit string — no code is ever a prefix of another, so the compressed stream can be decoded unambiguously.

It works best on data with skewed character frequencies, such as natural-language text, log files, or any source where some symbols appear far more often than others.

## Features

- Upload a text file via drag & drop or file browser
- Paste text directly into the input area
- Compress text using Huffman coding (processed server-side in Python)
- View stats: original size (bits), compressed size (bits), ratio, and % saving
- Download the compressed output (codebook + bitstring) as a `.huff` file
- Copy compressed output to clipboard
- Decompress & verify — confirms the round-trip matches the original exactly

## Project Structure

```
project-huffman/
├── huffman_app/
│   └── app.py                 
└── huffman-compressor.html    
```

## Requirements

- Python 3.x
- Flask

Install Flask if you don't have it:

```bash
pip install flask
```

## Running the App

```bash
python huffman_app/app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

## When Huffman Coding Helps vs. Hurts

| Input type                                  | Result              |
|----------------------------------------------|---------------------|
| Skewed frequencies (natural language, logs)  | Smaller output       |
| Few distinct symbols, very repetitive data   | Much smaller output  |
| Already-compressed or encrypted data         | Larger / no gain     |
| Uniformly random / evenly distributed data   | Little to no gain    |

> Unlike RLE, Huffman coding doesn't care about *runs* of repeated characters — it cares about overall *frequency*. A file with no consecutive duplicate characters at all (e.g. `"abcabcabc..."`) can still compress very well with Huffman coding, because each symbol still gets a code shorter than 8 bits on average. The theoretical limit is the Shannon entropy of the input; Huffman coding gets close to it for symbol-by-symbol coding.

## Output Format

The compressed `.huff` output is a small JSON object containing:

- `codebook` — a map from each character to its binary code string (needed to decode)
- `bitstring` — the compressed data as a string of `0`s and `1`s

This isn't a fully bit-packed binary format (each `0`/`1` is stored as a text character for portability and easy inspection/debugging), so the stats panel reports sizes in **bits** to show the true compression ratio achieved by the algorithm itself, independent of how the bits are ultimately packed into bytes on disk.

## Standalone Version

`huffman-compressor.html` is a fully self-contained version that runs entirely in the browser with no server required — the Huffman tree, encoding, and decoding all happen in vanilla JavaScript. Just open the file directly in any browser.
