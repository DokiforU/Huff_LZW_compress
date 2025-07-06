# Huffman & LZW Web Compression Tool

This project is a Flask-based web application supporting **Huffman** and **LZW** algorithms for compressing and decompressing any type of file or folder. It features a modern UI, supports both English and Chinese, and is suitable for text, images, audio, video, binary files, and more.

## Features

- Supports **Huffman** and **LZW** classic lossless compression algorithms
- Compress and decompress **single files** or **folders/directories**
- Supports various file types (.txt, .bin, .dat, .jpg, .png, .mp3, .mp4, .zip, .huff, .lzw, etc.)
- Maximum supported size: 20MB per file or folder
- Output is a zip archive, with each file inside compressed by the selected algorithm
- Decompression supports .huff, .lzw files and zip folder packages (restores original structure)
- Batch upload, directory upload, drag-and-drop, and paste supported
- Automatic file encoding detection, with warnings for non-UTF-8 text
- **Bilingual UI** (English/Chinese) and dark mode
- Download results directly, with compression ratio and speed metrics

## Project Structure

```
Huff_lzw_webapp/
├── core_logic/           # Core algorithm implementations (Huffman/LZW/directory handling)
├── downloads/            # Downloaded result files
├── uploads/              # Temporary upload files
├── web_app/
│   ├── static/           # Frontend static resources (js/css/example files)
│   ├── templates/        # Frontend templates (index.html, etc.)
│   ├── routes.py         # Flask routes and business logic
│   └── __init__.py       # Flask app initialization
├── tests/                # Unit tests
├── run.py                # App entry point
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies, mainly:
  - Flask
  - Jinja2
  - Werkzeug
  - chardet

Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Run

1. **Development mode**
   ```bash
   python run.py
   ```
   By default, the app runs at `0.0.0.0:5001`. Open your browser and visit `http://127.0.0.1:5001/`

2. **Production deployment**
   Recommended: use gunicorn, uwsgi, or Nginx as a reverse proxy for deployment.

## Usage

1. Open the web page, select the compression algorithm (Huffman/LZW) and mode (compress/decompress)
2. Select a file or folder, or drag-and-drop/paste into the upload area
3. Click "Start" and wait for the progress bar to complete
4. Results, compression ratio, time, etc. will be displayed on the right; download the result file directly
5. Switch between English/Chinese UI and dark mode as needed

## FAQ

- **Q: Why is the decompressed file garbled or incorrect?**  
  A: The original file may not be UTF-8 encoded. Please save as UTF-8 or download as binary.

- **Q: What file types and folders are supported?**  
  A: All file types (text, images, audio, video, binary, etc.) and folders are supported. Folders are zipped automatically.

- **Q: What formats are supported for decompression?**  
  A: .huff, .lzw compressed files and zip folder packages (restores original structure).

- **Q: Why is the compressed file sometimes larger?**  
  A: Random data, already compressed files, or formats like images/audio may become larger with general-purpose algorithms.

## Testing

Unit tests are provided in the `tests/` directory. To run all tests:
```bash
python -m unittest discover tests
```

## Additional Notes

- Frontend dependencies (Bootstrap, JSZip) are loaded via CDN, no local installation needed
- Modern browsers only
- For further development, familiarity with Flask, frontend basics, and compression algorithms is recommended

---

For questions or suggestions, please open an issue or contact the developer.

---

**中文界面支持：**
This project supports both English and Chinese UI. Switch the language at the top-right corner of the web page.