# 🌐 Streamlit CRUD App — Hosting with PlanetScale (MySQL)

This guide explains how to adapt your existing Streamlit CRUD app (originally using SQLite) to work with **PlanetScale**, a free cloud-based MySQL-compatible database.

---

## 🧱 Prerequisites

- A free [PlanetScale account](https://planetscale.com/)
- A GitHub account
- Basic understanding of the current Streamlit app
- Python installed locally

---

## ✅ Step 1: Set Up Your Database on PlanetScale

1. Go to [https://planetscale.com/](https://planetscale.com/) and sign in with GitHub
2. Click **"New Database"**
3. Name your database (e.g., `student_project`)
4. Choose a region and click **"Create Database"**

Once created:
- Go to the **"Branches"** tab
- Select `main`, then click **"Connect"**
- Choose **"Connect with Python"**
- Copy the connection info (host, user, password, etc.)

⚠️ Important: PlanetScale **disables `UPDATE` and `DELETE`** by default.
- Go to your branch (`main`)
- Click **"Settings"**
- Enable **"Safe migrations: OFF"** to allow full CRUD functionality

---

## 🛠️ Step 2: Update `config.py` in Your Project

Replace the SQLite config with this:

```python
DB_CONFIG = {
    "host": "your-planetscale-host",
    "user": "your-username",
    "password": "your-password",
    "database": "your-database-name",
    "port": 3306
}

TABLE_NAME = "your_table_name"

COLUMNS = {
    "name": "VARCHAR(255)",
    "email": "VARCHAR(255)",
    "age": "INT"
}
```

You can get all of these details from the **"Connect with Python"** page in PlanetScale.

---

## 🔄 Step 3: Replace SQLite Code in Your App

Edit `streamlit_app.py`:

- Replace `sqlite3` imports and connection logic with:

```python
import mysql.connector
from config import DB_CONFIG

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)
```

- Everything else (fetch, insert, update, delete) can stay the same if you're using standard SQL syntax.

✅ No need to change your table schema unless your columns differ.

---

## 📤 Step 4: Create Your Table on PlanetScale

You can use any MySQL tool (e.g., MySQL Workbench or DBeaver), or go to the **"Console"** in PlanetScale and run:

```sql
CREATE TABLE your_table_name (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    email VARCHAR(255),
    age INT
);
```

You may also populate it with initial data:

```sql
INSERT INTO your_table_name (name, email, age)
VALUES ('Alice', 'alice@example.com', 30),
       ('Bob', 'bob@example.com', 25);
```

---

## 🚀 Step 5: Run the App Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Verify that:
- Data loads from PlanetScale
- You can add, edit, delete, and transfer age between users

---

## ☁️ Step 6: Deploy to Streamlit Cloud (Optional)

Once working locally:
1. Push your project to GitHub
2. Visit [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Click **New app**, connect your repo, and deploy

✅ The app will connect to PlanetScale in the cloud — no database file needed!

---

## 🧠 Tips

- PlanetScale does **not** allow multiple connections per user by default — for classroom demos, ensure each student has their own DB.
- Do **not** commit your DB credentials to GitHub! Use environment variables or `.streamlit/secrets.toml` for security on Streamlit Cloud.

---

## 🔐 Optional: Using Secrets for Secure Deployment

In `.streamlit/secrets.toml`:

```toml
DB_HOST = "your-host"
DB_USER = "your-user"
DB_PASSWORD = "your-password"
DB_NAME = "your-db"
```

In `config.py`:

```python
import streamlit as st

DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "database": st.secrets["DB_NAME"],
    "port": 3306
}
```

This keeps your credentials secure on Streamlit Cloud.

---

Need help setting it up? Ping your instructor or TA for help with PlanetScale setup or environment configs.
