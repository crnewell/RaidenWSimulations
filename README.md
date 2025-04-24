
# 🧠 Discrete Structures Visualizer

This repository contains a simulation suite runnable either from source (Python) or via standalone executables for Windows and macOS.

---

## 🔧 Run from Source (Python)

### 1. Clone the Repository
```bash
git clone https://github.com/crnewell/RaidenWSimulations.git
cd RaidenWSimulations
```

### 2. Create a Virtual Environment *(if necessary)*
```bash
python -m venv ./venv
```

### 3. Activate the Virtual Environment
- **Windows:**
  ```bash
  .\venv\Scripts\activate
  ```

- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies *(if necessary)*
```bash
pip install -r requirements.txt
```

### 5. Run the Simulation
```bash
python main.py
```

> 💡 **Note:** Ensure you have Python 3.8+ installed. If dependencies or virtual environments are unfamiliar, consult [Python's official venv guide](https://docs.python.org/3/library/venv.html).

---

## 📦 Run as Executable (Windows & macOS)

### 1. Download the Executable

- **Windows**: [WindowsExecutable.zip](https://drive.google.com/file/d/11UrXTUPlfhqbH0F96XhkheC5FClBddES/view?usp=drive_link)
- **macOS**: [MacExecutable.zip](https://drive.google.com/file/d/13ejw7-fLJ26edtCRjwvHkkHnPCmv6TyN/view?usp=drive_link)

### 2. Extract the Contents

- Unzip the downloaded file for your platform.
- **Do not move** the main executable (`main.exe` or `main.app`) or its accompanying folders/files.

### 3. Run the Simulation

- **Windows**
  - Double-click `main.exe`, **or**
  - Open Command Prompt in the extracted folder:
    ```cmd
    cd path\to\unzipped\folder
    main.exe
    ```

- **macOS**
  - Double-click `main.app`, **or**
  - Use Terminal:
    ```bash
    cd /path/to/unzipped/folder
    open main.app
    ```

> ⚠️ macOS: You may need to approve the app in **System Preferences → Security & Privacy** the first time you run it.

---

## 📁 File Structure Suggestions

To avoid confusion or execution errors:
- Keep all files in their original unzipped structure
- Avoid renaming or moving the `.exe` or `.app` file or its dependencies
