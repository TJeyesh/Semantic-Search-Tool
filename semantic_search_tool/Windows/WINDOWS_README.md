# How to Run Finder on Windows

Follow these steps to transfer and run this AI Search Tool on a Windows PC.

## 1. Transfer Files
Copy the entire `semantic_search_tool` folder to your Windows PC.
*Note: You do NOT need to copy the `venv` folder or `.DS_Store` files. You will recreate the environment on Windows.*

## 2. Install Python
Make sure you have Python installed on your Windows machine.
-   Download from [python.org](https://www.python.org/).
-   **Important**: Check the box "Add Python to PATH" during installation.

## 3. Setup Environment (First Time Only)
Open a command prompt (cmd) inside the `semantic_search_tool` folder and run these commands:

1.  **Create Virtual Environment**:
    ```cmd
    python -m venv venv
    ```

2.  **Activate Environment**:
    ```cmd
    venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```cmd
    pip install -r requirements.txt
    ```
    *Note: This might take a few minutes to download the AI models/libraries.*

## 4. Run the App
Once set up, you can simply **double-click** the `run_finder.bat` file!

-   It will start the server.
-   It will open your browser to `http://localhost:8000`.
-   You can now use it exactly like on Mac.

## 5. Troubleshooting
-   If you get an error about "Execution Policy", you might need to run PowerShell as Admin.
-   If `pip` fails, try upgrading it: `python -m pip install --upgrade pip`.
