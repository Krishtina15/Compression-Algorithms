# RLE Compressor

A web application that compresses text files using the **Run-Length Encoding (RLE)** algorithm, built with Python and Flask.

## What is RLE?

Run-Length Encoding is a simple compression algorithm that replaces consecutive repeated characters with a count and the character itself.

```
Input:    AAABBBCCCDDD
Output:   3A3B3C3D
```

It works best on data with long runs of repeated characters, such as simple images, binary data, or log files with repetitive padding.

## Features

- Upload a text file via drag & drop or file browser
- Paste text directly into the input area
- Compress text using RLE (processed server-side in Python)
- View stats: original size, compressed size, ratio, and % saving
- Download the compressed output as a `.rle` file
- Copy compressed output to clipboard
- Decompress & verify — confirms the round-trip matches the original exactly

## Project Structure

```
project-algo/
├── rle_app/
│   └── app.py            # Flask app — RLE logic + HTML template + API routes
└── rle-compressor.html   # Standalone HTML version (no server needed)
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
python rle_app/app.py
```

Then open your browser and go to:

```
http://127.0.0.1:5000
```

## API Endpoints

| Method | Endpoint      | Description                          |
|--------|---------------|--------------------------------------|
| GET    | `/`           | Serves the web UI                    |
| POST   | `/compress`   | Compresses text, returns JSON stats  |
| POST   | `/decompress` | Decodes RLE-encoded text             |
| POST   | `/download`   | Returns compressed text as a file    |

### Example

```bash
curl -X POST http://127.0.0.1:5000/compress \
  -H "Content-Type: application/json" \
  -d '{"text": "AAABBBCCC"}'
```

```json
{
  "compressed": "3A3B3C",
  "original_bytes": 9,
  "compressed_bytes": 6,
  "ratio": 0.67,
  "saving_pct": "-33.0%",
  "message": "RLE reduced the file by 33.0%."
}
```

## When RLE Helps vs. Hurts

| Input type                        | Result              |
|-----------------------------------|---------------------|
| Repeated characters (`AAAABBBB`)  | Smaller output      |
| Natural language / prose          | Larger output       |
| Binary/image data with solid runs | Smaller output      |
| Random or varied characters       | Larger output       |

> Normal English text will almost always produce a larger compressed output because each unique character gets a `1` prefix (e.g. `"the"` → `"1t1h1e"`), roughly doubling the size.

## Standalone Version

`rle-compressor.html` is a fully self-contained version that runs entirely in the browser with no server required. Just open the file directly in any browser.
