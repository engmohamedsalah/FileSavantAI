# FileSavantAI: AI-Powered File System Analysis

FileSavantAI is a project that demonstrates how to integrate a C program with a Python script and an AI model to analyze and report on files in a directory. This project fulfills a two-part technical assignment that showcases C programming, Python scripting, and AI integration.

## Features

-   **File Information Tool:** A C program that lists all files in the current directory with details like owner, creation date, and permissions.
-   **AI-Powered Analysis:** A Python script that uses the C program's output to provide AI-driven insights into the directory's contents.
-   **Specific File Lookup:** The script can identify and report on a specific file (`hello_world.txt`) to show its owner and creation date.
-   **Validation:** The script validates its findings using the `ls -l` command.

## Prerequisites

-   A C compiler (like `gcc`)
-   Python 3
-   An OpenAI API key

## Setup and Installation

1.  **Clone the repository:**
    ```sh
    git clone <your-repo-url>
    cd FileSavantAI
    ```

2.  **Compile the C program:**
    ```sh
    gcc -o file_info file_info.c
    ```

3.  **Create and Activate a Virtual Environment:**
    -   This creates an isolated environment for the project's dependencies.
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    -   Your terminal prompt should now show `(.venv)`.
    -   To deactivate it later, simply run `deactivate`.

4.  **Create a `.env` file for your API Key:**
    -   Create a file named `.env` in the root of the project.
    -   Add your OpenAI API key to it like this:
        ```
        OPENAI_API_KEY='your-api-key'
        ```

5.  **Install Python dependencies (inside the virtual environment):**
    ```sh
    pip install -r requirements.txt
    ```

## How to Run

Run the script from your terminal, providing the name of the file you want to inspect. You can also use optional flags to control the search behavior.

**Syntax:**
```sh
python3 ai_integration.py <filename> [--case-sensitive] [--match-type <type>]
```

### Basic Usage

To find an exact match for a file (case-insensitive by default):
```sh
python3 ai_integration.py hello_world.txt
```

### Advanced Searching

You can combine the following flags to create powerful and specific searches.

**`--case-sensitive`**
-   **Purpose:** Makes your search term match the exact letter casing.
-   **Default:** Off (searches are case-insensitive).
-   **Example:** By default, `python3 ai_integration.py readme.md` will find `README.md`. But with this flag, it will not.
    ```sh
    # This will likely fail to find README.md
    python3 ai_integration.py readme.md --case-sensitive
    ```

**`--match-type <type>`**
-   **Purpose:** Changes the search strategy.
-   **Default:** `exact`
-   **Available Types:**
    1.  **`exact` (Default):** Finds the file only if the name is an exact match (respecting `--case-sensitive`).
    2.  **`contains`:** Finds all files whose names contain the search term. This is useful for finding related files.
        ```sh
        # Finds any file with 'info' in the name (e.g., file_info, file_info.c)
        python3 ai_integration.py info --match-type contains
        ```
    3.  **`similar`:** If no exact match is found, this will use a fuzzy-matching algorithm to find and suggest files with similar spellings. This is great for typos.
        ```sh
        # If you misspell 'readme', it will suggest 'README.md'
        python3 ai_integration.py readm --match-type similar
        ```

## Running the Unit Tests

A comprehensive test suite is included to ensure the script's logic is working correctly. The tests cover parsing, all search variations, and use mocks to isolate functions from external dependencies.

To run the tests, execute the following command from the root of the project:
```sh
python3 -m unittest test_ai_integration.py
```

## Running with Docker

You can also build and run this project inside a Docker container.

1.  **Build the Docker image:**
    ```sh
    docker build -t filesavantai .
    ```

2.  **Run the Docker container:**
    -   Make sure you have created the `.env` file as described in the setup section.
    -   Run the container using the `--env-file` flag to securely pass your API key.
    -   Pass the filename and any search flags as a command at the end of the `docker run` line.
    ```sh
    docker run --env-file .env filesavantai info --match-type contains
    ```

## C Program Output Format

The `file_info` C program produces one line of output for each file, with fields separated by spaces. Here is an example and an explanation of the fields:

**Example Output:**
```
644 1 msalah staff 28 Jun 10 18:14 hello_world.txt
```

**Field Breakdown:**
-   `644`: File permissions in octal format.
-   `1`: Number of hard links.
-   `msalah`: The owner of the file.
-   `staff`: The group the file belongs to.
-   `28`: The size of the file in bytes.
-   `Jun 10`: The month and day the file was last modified.
-   `18:14`: The time the file was last modified.
-   `hello_world.txt`: The name of the file.

## Project Structure

-   `file_info.c`: The C program that lists file details.
-   `ai_integration.py`: The main Python script that integrates the C program and the AI model.
-   `docker.Dockerfile`: A Dockerfile for containerizing the application.
-   `AI Engineer Task.pdf`: The original task description.
-   `requirements.txt`: The Python dependencies file.
-   `README.md`: This file. 