from flask import Flask, request, jsonify, render_template_string, send_file
import io

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>RLE Compressor</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: system-ui, -apple-system, sans-serif;
      background: #f5f5f5;
      color: #222;
      min-height: 100vh;
      padding: 32px 16px;
    }

    .container { max-width: 720px; margin: 0 auto; }

    header { margin-bottom: 32px; }
    header h1 { font-size: 1.6rem; font-weight: 700; letter-spacing: -0.5px; }
    header p  { margin-top: 6px; color: #666; font-size: 0.9rem; }

    .card {
      background: #fff;
      border: 1px solid #e0e0e0;
      border-radius: 10px;
      padding: 24px;
      margin-bottom: 16px;
    }

    .card-title {
      font-size: 0.78rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: #888;
      margin-bottom: 12px;
    }

    .drop-zone {
      border: 2px dashed #d0d0d0;
      border-radius: 8px;
      padding: 28px;
      text-align: center;
      cursor: pointer;
      transition: border-color 0.2s, background 0.2s;
      margin-bottom: 12px;
    }

    .drop-zone:hover, .drop-zone.dragover {
      border-color: #4a90e2;
      background: #f0f6ff;
    }

    .drop-zone svg { display: block; margin: 0 auto 10px; color: #aaa; }
    .drop-zone p   { color: #666; font-size: 0.9rem; }
    .drop-zone span { color: #4a90e2; font-weight: 500; }

    #file-input { display: none; }

    textarea {
      width: 100%;
      border: 1px solid #ddd;
      border-radius: 6px;
      padding: 12px;
      font-family: 'Courier New', monospace;
      font-size: 0.85rem;
      resize: vertical;
      outline: none;
      transition: border-color 0.2s;
      background: #fafafa;
      color: #222;
      line-height: 1.5;
    }

    textarea:focus  { border-color: #4a90e2; background: #fff; }
    .input-area     { height: 140px; }
    .output-area    { height: 140px; background: #f9f9f9; }

    .row {
      display: flex;
      gap: 10px;
      margin-top: 12px;
      flex-wrap: wrap;
      align-items: center;
    }

    button {
      padding: 9px 20px;
      border: none;
      border-radius: 6px;
      font-size: 0.88rem;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.15s, opacity 0.15s;
    }

    button:disabled { opacity: 0.4; cursor: not-allowed; }

    .btn-primary   { background: #4a90e2; color: #fff; }
    .btn-primary:hover   { background: #357abd; }
    .btn-secondary { background: #f0f0f0; color: #333; }
    .btn-secondary:hover { background: #e0e0e0; }
    .btn-ghost     { background: transparent; color: #4a90e2; border: 1px solid #4a90e2; }
    .btn-ghost:hover     { background: #f0f6ff; }

    .stats {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }

    .stat {
      background: #f5f5f5;
      border-radius: 6px;
      padding: 10px 16px;
      flex: 1;
      min-width: 110px;
      text-align: center;
    }

    .stat-value       { font-size: 1.3rem; font-weight: 700; color: #222; }
    .stat-value.good  { color: #2a9d5c; }
    .stat-value.bad   { color: #e05; }
    .stat-label       { font-size: 0.72rem; color: #888; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.5px; }

    .msg {
      font-size: 0.82rem;
      padding: 8px 12px;
      border-radius: 6px;
      margin-top: 12px;
      display: none;
    }

    .msg.info  { background: #e8f4fd; color: #1a6bb0; display: block; }
    .msg.warn  { background: #fff8e1; color: #a07000; display: block; }
    .msg.error { background: #fdecea; color: #c0392b; display: block; }

    .divider {
      display: flex;
      align-items: center;
      gap: 10px;
      color: #bbb;
      font-size: 0.8rem;
      margin: 4px 0;
    }

    .divider::before, .divider::after {
      content: '';
      flex: 1;
      height: 1px;
      background: #e0e0e0;
    }

    footer {
      text-align: center;
      color: #bbb;
      font-size: 0.78rem;
      margin-top: 24px;
    }

    #spinner { display: none; }
    .loading #spinner { display: inline; }
  </style>
</head>
<body>
<div class="container">
  <header>
    <h1>RLE Compressor</h1>
    <p>Compress text using Run-Length Encoding — server-side Python processes your file.</p>
  </header>

  <!-- Input -->
  <div class="card">
    <div class="card-title">Input</div>

    <div class="drop-zone" id="drop-zone">
      <svg width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round"
          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
      </svg>
      <p>Drag &amp; drop a file here, or <span id="browse-link">browse</span></p>
      <p style="font-size:0.75rem;color:#bbb;margin-top:4px;">Plain-text files (.txt, .csv, .log, .md, etc.)</p>
    </div>
    <input type="file" id="file-input" />

    <div class="divider">or paste text</div>

    <textarea id="input-text" class="input-area" placeholder="Paste or type text here…"></textarea>

    <div class="row">
      <button class="btn-primary" id="compress-btn">
        <span id="spinner">⏳ </span>Compress
      </button>
      <button class="btn-secondary" id="clear-btn">Clear</button>
      <span id="char-count" style="margin-left:auto;color:#aaa;font-size:0.8rem;">0 chars</span>
    </div>
  </div>

  <!-- Stats -->
  <div class="card" id="stats-card" style="display:none;">
    <div class="card-title">Result</div>
    <div class="stats">
      <div class="stat">
        <div class="stat-value" id="stat-original">—</div>
        <div class="stat-label">Original</div>
      </div>
      <div class="stat">
        <div class="stat-value" id="stat-compressed">—</div>
        <div class="stat-label">Compressed</div>
      </div>
      <div class="stat">
        <div class="stat-value" id="stat-ratio">—</div>
        <div class="stat-label">Ratio</div>
      </div>
      <div class="stat">
        <div class="stat-value" id="stat-saving">—</div>
        <div class="stat-label">Saving</div>
      </div>
    </div>
    <div class="msg" id="rle-msg"></div>
  </div>

  <!-- Output -->
  <div class="card" id="output-card" style="display:none;">
    <div class="card-title">Compressed Output</div>
    <textarea id="output-text" class="output-area" readonly></textarea>
    <div class="row">
      <button class="btn-primary"   id="download-btn">Download .rle</button>
      <button class="btn-ghost"     id="copy-btn">Copy</button>
      <button class="btn-ghost"     id="decompress-btn">Decompress &amp; Verify</button>
    </div>
  </div>

  <!-- Verify -->
  <div class="card" id="verify-card" style="display:none;">
    <div class="card-title">Decompressed (Verification)</div>
    <textarea id="verify-text" class="output-area" readonly></textarea>
    <div class="msg" id="verify-msg"></div>
  </div>

  <footer>RLE: consecutive identical characters encoded as count + character &nbsp;|&nbsp; Powered by Python + Flask</footer>
</div>

<script>
  const inputText     = document.getElementById('input-text');
  const outputText    = document.getElementById('output-text');
  const verifyText    = document.getElementById('verify-text');
  const charCount     = document.getElementById('char-count');
  const dropZone      = document.getElementById('drop-zone');
  const fileInput     = document.getElementById('file-input');
  const browseLink    = document.getElementById('browse-link');
  const compressBtn   = document.getElementById('compress-btn');
  const clearBtn      = document.getElementById('clear-btn');
  const downloadBtn   = document.getElementById('download-btn');
  const copyBtn       = document.getElementById('copy-btn');
  const decompressBtn = document.getElementById('decompress-btn');
  const statsCard     = document.getElementById('stats-card');
  const outputCard    = document.getElementById('output-card');
  const verifyCard    = document.getElementById('verify-card');
  const rleMsg        = document.getElementById('rle-msg');
  const verifyMsg     = document.getElementById('verify-msg');

  function fmtBytes(n) {
    return n < 1024 ? n + ' B' : (n / 1024).toFixed(1) + ' KB';
  }

  function showMsg(el, type, text) {
    el.className = 'msg ' + type;
    el.textContent = text;
  }

  function hideResults() {
    statsCard.style.display = 'none';
    outputCard.style.display = 'none';
    verifyCard.style.display = 'none';
  }

  // File loading
  browseLink.addEventListener('click', () => fileInput.click());
  dropZone.addEventListener('click',   () => fileInput.click());

  fileInput.addEventListener('change', () => {
    if (fileInput.files[0]) readFile(fileInput.files[0]);
  });

  dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
  dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
  dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files[0]) readFile(e.dataTransfer.files[0]);
  });

  function readFile(file) {
    const reader = new FileReader();
    reader.onload = e => {
      inputText.value = e.target.result;
      updateCount();
      hideResults();
    };
    reader.readAsText(file);
  }

  inputText.addEventListener('input', () => { updateCount(); hideResults(); });

  function updateCount() {
    const n = inputText.value.length;
    charCount.textContent = n.toLocaleString() + ' char' + (n !== 1 ? 's' : '');
  }

  // Compress (call Python backend)
  compressBtn.addEventListener('click', async () => {
    const text = inputText.value;
    if (!text) return;

    compressBtn.disabled = true;
    document.querySelector('.loading') || compressBtn.classList.add('loading');

    try {
      const res  = await fetch('/compress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });
      const data = await res.json();

      if (data.error) {
        showMsg(rleMsg, 'error', data.error);
        statsCard.style.display = 'block';
        outputCard.style.display = 'none';
        return;
      }

      outputText.value = data.compressed;

      document.getElementById('stat-original').textContent   = fmtBytes(data.original_bytes);
      document.getElementById('stat-compressed').textContent = fmtBytes(data.compressed_bytes);

      const ratioEl  = document.getElementById('stat-ratio');
      const savingEl = document.getElementById('stat-saving');
      ratioEl.textContent  = data.ratio + 'x';
      savingEl.textContent = data.saving_pct;

      const good = data.compressed_bytes < data.original_bytes;
      ratioEl.className  = 'stat-value ' + (good ? 'good' : 'bad');
      savingEl.className = 'stat-value ' + (good ? 'good' : 'bad');

      showMsg(rleMsg, good ? 'info' : 'warn', data.message);

      statsCard.style.display = 'block';
      outputCard.style.display = 'block';
      verifyCard.style.display = 'none';
    } catch (err) {
      alert('Request failed: ' + err.message);
    } finally {
      compressBtn.disabled = false;
    }
  });

  // Clear
  clearBtn.addEventListener('click', () => {
    inputText.value = '';
    fileInput.value = '';
    updateCount();
    hideResults();
  });

  // Copy
  copyBtn.addEventListener('click', () => {
    navigator.clipboard.writeText(outputText.value).then(() => {
      copyBtn.textContent = 'Copied!';
      setTimeout(() => copyBtn.textContent = 'Copy', 1500);
    });
  });

  // Download
  downloadBtn.addEventListener('click', async () => {
    const res  = await fetch('/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ compressed: outputText.value })
    });
    const blob = await res.blob();
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = 'compressed.rle'; a.click();
    URL.revokeObjectURL(url);
  });

  // Decompress & verify
  decompressBtn.addEventListener('click', async () => {
    const res  = await fetch('/decompress', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ compressed: outputText.value })
    });
    const data = await res.json();

    verifyText.value = data.decompressed || '';
    verifyCard.style.display = 'block';

    if (data.error) {
      showMsg(verifyMsg, 'error', data.error);
    } else if (data.decompressed === inputText.value) {
      showMsg(verifyMsg, 'info', 'Verification passed — decompressed output matches the original input exactly.');
    } else {
      showMsg(verifyMsg, 'warn', 'Decompressed output differs from the original input.');
    }
  });

  updateCount();
</script>
</body>
</html>
"""


def rle_encode(text: str) -> str:
    if not text:
        return ""
    result = []
    i = 0
    while i < len(text):
        ch = text[i]
        count = 1
        while i + count < len(text) and text[i + count] == ch:
            count += 1
        # Escape backslashes and digits so the decoder is unambiguous
        if ch == "\\":
            escaped = "\\\\"
        elif ch.isdigit():
            escaped = "\\" + ch
        else:
            escaped = ch
        result.append(f"{count}{escaped}")
        i += count
    return "".join(result)


def rle_decode(encoded: str) -> str:
    result = []
    i = 0
    while i < len(encoded):
        # read count digits
        num_str = ""
        while i < len(encoded) and encoded[i].isdigit():
            num_str += encoded[i]
            i += 1
        if not num_str or i >= len(encoded):
            raise ValueError("Invalid RLE data: missing count or character")
        count = int(num_str)
        # read (possibly escaped) character
        if encoded[i] == "\\":
            if i + 1 >= len(encoded):
                raise ValueError("Trailing escape sequence")
            ch = encoded[i + 1]
            i += 2
        else:
            ch = encoded[i]
            i += 1
        result.append(ch * count)
    return "".join(result)


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/compress", methods=["POST"])
def compress():
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        compressed = rle_encode(text)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    orig_bytes = len(text.encode("utf-8"))
    comp_bytes = len(compressed.encode("utf-8"))
    ratio      = round(comp_bytes / orig_bytes, 2) if orig_bytes else 0
    saving_raw = round((1 - ratio) * 100, 1)
    saving_str = (f"-{saving_raw}%" if saving_raw >= 0 else f"+{abs(saving_raw)}%")

    if comp_bytes < orig_bytes:
        msg = f"RLE reduced the file by {saving_raw}%. Works best on text with many consecutive repeated characters."
    else:
        msg = "The compressed output is larger than the original. RLE is most effective with long runs of repeated characters (e.g. AAAAAABBBB)."

    return jsonify({
        "compressed":      compressed,
        "original_bytes":  orig_bytes,
        "compressed_bytes": comp_bytes,
        "ratio":           ratio,
        "saving_pct":      saving_str,
        "message":         msg,
    })


@app.route("/decompress", methods=["POST"])
def decompress():
    data = request.get_json(force=True)
    encoded = data.get("compressed", "")
    try:
        decoded = rle_decode(encoded)
        return jsonify({"decompressed": decoded})
    except Exception as e:
        return jsonify({"error": str(e), "decompressed": ""}), 400


@app.route("/download", methods=["POST"])
def download():
    data       = request.get_json(force=True)
    compressed = data.get("compressed", "")
    buf        = io.BytesIO(compressed.encode("utf-8"))
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name="compressed.rle",
        mimetype="text/plain",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
