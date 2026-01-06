# Django Project Setup Guide

Welcome!
Follow these instructions to set up and run the project on your local machine.

---

## Requirements

- Python 3.9 or higher (recommended: 3.10)
- pip (Python package installer)
- virtualenv (recommended)
- PostgreSQL or SQLite (depending on project settings)

---

## 1. Extract the ZIP File

- **Windows**: Right-click the `.zip` → "Extract All" → choose a location.
- **Mac**: Double-click the `.zip` → it will extract into a folder.

---

## 2. Open Terminal or Command Prompt

- **Windows**: Press `Win + R`, type `cmd`, and press Enter.
- **Mac**: Open `Terminal` from `Applications > Utilities > Terminal`.

---

## 3. Navigate to the Project Directory

```bash
cd path/to/your/project

---

🛠️ 4. Create and Activate a Virtual Environment
Windows
 - python -m venv env
 - env\Scripts\activate
Mac/Linux
 - python3 -m venv env
 - source env/bin/activate

⚡ Tip: If venv is not available, install it using:
    pip install virtualenv

📦 5. Install Project Dependencies
    - pip install -r requirements.txt

🗄️ 6. Apply Database Migrations
    - python manage.py migrate

   7. Running in Development Mode
        - To start Django Tailwind in development mode, run the following command in a terminal:

        - python manage.py tailwind start


🚀 8. Run the Development Server
    - python manage.py runserver