# Huffman & LZW File Compression Web App

![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.1-hotpink.svg)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow.svg)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A web-based file compression and decompression tool that implements the classic Huffman and LZW lossless algorithms from scratch. This project, developed for a Data Structures and Algorithms course at Southwest University, focuses on the meticulous implementation of core data structures and algorithms, wrapped in a user-friendly interface powered by Python Flask and modern web technologies.

---

## ✨ Key Features

-   **Dual Algorithm Support**: Choose between Huffman coding (statistical) and LZW (dictionary-based) for compression and decompression.
-   **File & Directory Handling**: Process single files or entire directories with ease. Directory handling is supported via client-side ZIP archiving and server-side processing.
-   **Intuitive User Interface**: A clean, responsive UI built with Bootstrap 5, featuring:
    -   Drag-and-drop file/directory uploads.
    -   Light and Dark mode themes.
    -   Multilingual support (English/Chinese).
    -   User preferences saved to local storage.
-   **Real-time Performance Metrics**: Instantly view processing time, original/final file sizes, and compression ratio after each operation.
-   **Batch Operations**: For decompressed directories, select multiple files to download as a single ZIP archive.
-   **Custom Data Structures**: Core algorithms are built upon custom-implemented data structures (`PriorityQueue` for Huffman, `CustomDict` for LZW) to demonstrate a deep understanding of the underlying principles.
-   **Robust Error Handling**: Provides clear feedback for common errors, such as format mismatches, negative compression, and invalid files.

## 📸 Screenshots & Demo

A quick look at the application's interface and capabilities.

| Main Interface (Light/Dark Mode)                                | Compression Results Display                                 |
| --------------------------------------------------------------- | ----------------------------------------------------------- |
| ![Main UI](docs/images/main-ui.png)                             | ![Results UI](docs/images/results-ui.png)                   |
| **Directory Decompression & Batch Download** | **Error & Warning Feedback** |
| ![Directory Decompression](docs/images/directory-download.png) | ![Error Handling](docs/images/error-handling.png)         |

*(**Note**: Please replace the image paths above with your actual screenshots.)*

## ⚙️ Technology Stack

-   **Backend**: Python 3.10, Flask 3.1.0
-   **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3
-   **Core Algorithms**:
    -   **Huffman Coding**: Implemented from scratch, including frequency analysis, tree building, and encoding/decoding logic.
    -   **LZW Algorithm**: Implemented from scratch, including dynamic dictionary management and KwKwK edge case handling.
-   **Key Libraries**:
    -   `unittest` for comprehensive testing.
    -   `JSZip` for client-side directory archiving.
    -   `chardet` for rudimentary file encoding detection.
-   **Development Environment**: PyCharm, macOS Sequoia

## 📂 Project Structure

The project is organized into distinct modules for maintainability and clarity.

```

Huff\_LZW\_compress/
├── core\_logic/
│   ├── **init**.py
│   ├── custom\_dict.py        \# Custom dictionary for LZW
│   ├── data\_structures.py    \# HuffmanNode & PriorityQueue
│   ├── directory\_handler.py  \# Logic for directory processing
│   ├── huffman\_coder.py      \# Huffman algorithm implementation
│   └── lzw\_coder.py          \# LZW algorithm implementation
├── downloads/                  \# Default location for processed files
├── tests/                      \# Unit tests for the core logic
│   ├── test\_custom\_dict.py
│   ├── test\_data\_structures.py
│   ├── test\_huffman\_coder.py
│   └── test\_lzw\_coder.py
├── web\_app/
│   ├── **init**.py             \# Flask application factory
│   ├── routes.py               \# Application routes (/process, /download)
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── example/            \# Sample files for testing
│   └── templates/
│       └── index.html          \# Main HTML template
├── requirements.txt            \# Project dependencies
├── run.py                      \# Application entry point
└── README.md

````

## 📚 Core Concepts & Implementation Details

A key objective of this project was to implement the compression algorithms and their supporting data structures from the ground up.

### Huffman Algorithm

The Huffman implementation is based on statistical data redundancy.
1.  **Frequency Analysis**: Scans the input file to build a frequency map of each byte using `collections.Counter`.
2.  **Tree Construction**: A custom `PriorityQueue` class, implemented as a min-heap using a Python list, is used to efficiently build the Huffman tree. It repeatedly extracts the two nodes with the lowest frequencies and merges them.
3.  **Code Generation**: A recursive traversal of the Huffman tree generates the variable-length prefix codes for each byte.
4.  **Header Metadata**: To ensure self-contained decompression, a custom file header is prepended to the compressed data. It contains:
    -   The original file extension.
    -   The pickled frequency map, essential for rebuilding the exact Huffman tree.
    -   Padding information to align the final byte.

### LZW Algorithm

The LZW implementation is an adaptive, dictionary-based method.
1.  **Custom Dictionary**: A `CustomDict` class was built from scratch to serve as the LZW dictionary. It's a hash table that uses chaining for collision resolution and features dynamic resizing to maintain performance as the dictionary grows. It is specifically optimized to handle `bytes` objects as keys.
2.  **Adaptive Compression**: The algorithm reads the input stream and progressively builds the dictionary. Sequences of bytes are replaced with codes from the dictionary. When a new, previously unseen sequence is encountered, it is added to the dictionary.
3.  **KwKwK Edge Case**: The implementation correctly handles the "KwKwK" edge case, which occurs when the encoder encounters a sequence of the form `(string) + (first char of string)`.

## 🚀 Getting Started

Follow these steps to run the application locally.

### Prerequisites

-   Python 3.10 or higher
-   `pip` and `venv`

### Installation & Launch

1.  **Clone the repository:**
    ```sh
    git clone [https://github.com/DokiforU/Huff_LZW_compress.git](https://github.com/DokiforU/Huff_LZW_compress.git)
    cd Huff_LZW_compress
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```sh
    python run.py
    ```

5.  Open your web browser and navigate to `http://127.0.0.1:5000`.

## 🧪 Running Tests

To verify the correctness of the core algorithms and data structures, you can run the built-in unit tests.

```sh
python -m unittest discover -s tests
````

## 🛣️ Future Improvements

This project serves as a solid foundation, and several areas could be explored for future enhancement:

  - **Advanced Algorithms**: Integrate more powerful algorithms like Arithmetic Coding or Deflate (LZ77 + Huffman).
  - **Algorithm Optimization**: Implement adaptive Huffman coding or add a dictionary reset policy (e.g., LFU/LRU) to the LZW algorithm for better performance on large, non-uniform files.
  - **Large File Support**: Implement file chunking for uploads and processing, using a task queue like Celery and WebSockets for real-time progress updates.
  - **User Authentication**: Add user accounts to manage and secure personal files.

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
