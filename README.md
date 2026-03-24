# Career Path Explorer

A simple Flask web app for students to explore career paths.

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Enter the project folder
cd career_explorer

# 3. Optional: use PostgreSQL instead of SQLite
# Windows PowerShell
$env:DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/career_explorer"

# 4. Run the app
python app.py

# 5. Open your browser
# http://localhost:5000
```

## Pages

| URL | Description |
|-----|-------------|
| `/` | Home page |
| `/careers` | Browse all career cards |
| `/career/<name>` | Detail page for one career |
| `/quiz` | 2-question career quiz |
| `/form` | Save your career interest |
| `/admin` | View all saved student data |
| `/health` | Health check with database status |

## Database

By default the app uses SQLite with `database.db`.

To use PostgreSQL, set `DATABASE_URL` before starting the app:

```powershell
$env:DATABASE_URL="postgresql://USER:PASSWORD@localhost:5432/career_explorer"
python app.py
```

## File Structure

```text
career_explorer/
|-- app.py
|-- database.db
|-- requirements.txt
|-- static/
|   |-- style.css
|   `-- script.js
`-- templates/
    |-- admin.html
    |-- base.html
    |-- career_detail.html
    |-- careers.html
    |-- form.html
    |-- index.html
    `-- quiz.html
```
