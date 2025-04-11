# Text Line Merger (for GB18030 Files)

This Python script processes a text file encoded in **GB18030**, merging consecutive lines unless a line ends with specific punctuation marks ('。' or '"') or is an empty line. It's useful for cleaning up text where paragraphs or sentences have been unnecessarily split across multiple lines.

## Overview

The script reads an input text file (`.txt`), processes its content line by line, and creates a new output file in the **same directory** as the input file. The output file will have the same name as the input file, but with `_processed.txt` appended before the original extension. The original input file remains unchanged.

**Important:** This script is specifically designed to work with files encoded using the **GB18030** standard. Using it on files with other encodings (like UTF-8, GBK, Big5) will likely result in errors or incorrect output.

## Features

* Merges consecutive lines of text.
* Preserves line breaks for lines ending in '。' (full stop period used in Chinese) or '"' (quotation mark).
* Preserves empty lines as separate paragraphs/lines.
* Reads and writes files using **GB18030** encoding.
* Creates a new output file, leaving the original file untouched.
* Basic error handling for cases where the input file is not found.

## Prerequisites

* **Python 3:** You need to have Python 3 installed on your computer. You can download it from [python.org](https://www.python.org/).
* **The Script File:** You need this Python script file (let's assume you save it as `process_text.py`).

## Setup

1.  **Save the Script:** Download or save the Python script code to a file on your computer. For example, save it as `process_text.py`.
2.  **!!! IMPORTANT: Modify the Input File Path !!!**
    * Open the script file (`process_text.py`) in a text editor (like Notepad, TextEdit, VS Code, etc.).
    * Locate the **last section** of the script, which looks like this:
        ```python
        # 使用指定的文件路径
        if __name__ == '__main__':
            # vvvvv MODIFY THIS LINE vvvvv
            input_file = '/Users/yuli_xia/Desktop/.txt' # <--- CHANGE THIS PATH
            # ^^^^^ MODIFY THIS LINE ^^^^^
            process_text_file(input_file, None)
        ```
    * **You MUST change** the path `/Users/yuli_xia/Desktop/.txt` to the **exact, full path** of the `.txt` file you want to process on your computer.
        * **Example (macOS/Linux):** `input_file = '/Users/your_username/Documents/my_document.txt'`
        * **Example (Windows):** `input_file = 'C:/Users/your_username/Documents/my_document.txt'` (Use forward slashes `/` even on Windows, or escape backslashes: `'C:\\Users\\your_username\\Documents\\my_document.txt'`)
    * **Save** the changes you made to the script file.

## How to Use / Running the Script

1.  **Open Terminal or Command Prompt:**
    * **macOS:** Open the "Terminal" application (usually in Applications > Utilities).
    * **Windows:** Search for "Command Prompt" or "PowerShell" and open it.
2.  **Navigate to the Script's Directory:** Use the `cd` command to change the current directory to where you saved the `process_text.py` file.
    * **Example (macOS/Linux):** `cd /path/to/where/you/saved/the/script`
    * **Example (Windows):** `cd C:\path\to\where\you\saved\the\script`
3.  **Run the Script:** Execute the script using the `python` command:
    ```bash
    python process_text.py
    ```
4.  **Check Output:**
    * The script will print a message to the terminal when it finishes (e.g., "处理完成！输出文件保存为：...").
    * Look in the **same directory where your original input file is located**. You should find a new file with the original name plus `_processed.txt` at the end (e.g., if your input was `my_document.txt`, the output will be `my_document_processed.txt`).
    * Open the `_processed.txt` file to view the results.

**Note:** Every time you want to process a *different* input file, you need to repeat the **Setup Step 2** (modify the `input_file` path inside the script) before running it again.

## Important Notes & Limitations

* **Encoding is Critical:** This script **only** works correctly with **GB18030** encoded text files. Do not use it on UTF-8 or other encoded files.
* **Input Path Modification:** You **must** edit the script code directly to change the input file path before each run for different files.
* **Line Break Rules:** Line breaks are preserved *only* if a line ends precisely with '。' or '"' (after stripping trailing whitespace), or if the line was originally empty. Other punctuation marks (like '.', '?', '!') will *not* prevent lines from being merged.
* **Output File Overwriting:** If a file with the `_processed.txt` name already exists in the input file's directory (perhaps from a previous run), it will be **overwritten without warning**.