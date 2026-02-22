# DRICE Backend Setup Guide

This guide will walk you through cloning the backend repository, configuring your local PostgreSQL database, and seeding it with the necessary dummy data to match the frontend Dashboard expectations.

## Prerequisites

Before starting, ensure you have the following installed on your machine:
*   [Python 3.10+](https://www.python.org/downloads/)
*   [PostgreSQL](https://www.postgresql.org/download/)
*   [Git](https://git-scm.com/downloads)

## 1. Clone the Repository

Clone the backend repository and navigate into it:

```bash
git clone https://github.com/Cathy-matu/research-backend.git
cd research-backend
```

## 2. Create the Virtual Environment

It is highly recommended to isolate your Python dependencies using a virtual environment.

```bash
python3 -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

Next, install all project dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 3. Database Configuration (PostgreSQL)

The Django backend strictly expects a PostgreSQL connection to function, especially because it uses specific JSON fields.

### Create a Local Database
Open your psql terminal (or use a GUI tool like pgAdmin) and create a local database:
```sql
CREATE DATABASE research_db;
CREATE USER research_user WITH PASSWORD 'secure_password';
ALTER ROLE research_user SET client_encoding TO 'utf8';
ALTER ROLE research_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE research_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE research_db TO research_user;
```

### Environment Variables (.env)
Create a `.env` file at the root of your `research-backend/` project. This isolates your sensitive credentials from version control.

```bash
touch .env
```

Add your PostgreSQL configuration. **You only need to supply `DATABASE_URL` (preferred) OR the individual `DB_*` keys:**

```env
DEBUG=True
SECRET_KEY=generate_a_secure_random_key_here

# METHOD 1: Database URL (Preferred for Vercel/Supabase)
# DATABASE_URL=postgres://research_user:secure_password@localhost:5432/research_db

# METHOD 2: Strict Variables
DB_NAME=research_db
DB_USER=research_user
DB_PASSWORD=secure_password
DB_HOST=localhost
DB_PORT=5432

CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_HOSTS=localhost,127.0.0.1
```

## 4. Run Migrations

Now that the `.env` file is loaded with your database credentials, instruct Django to build the required tables (Users, Projects, Events, Tasks, etc.).

```bash
python manage.py migrate
```

## 5. Seed the Database

The frontend dashboards require an initial populated state to display correctly. We provide a `seed_db.py` script that automatically generates ~10 Users (with roles) and ties them to dummy Projects, Tasks, and Events. 

If you do not run this script, your local dashboard will be completely empty.

```bash
python seed_db.py
```

*Note: The script outputs the generated email credentials and the default password (usually `password123`) to the terminal. Use these to log in to the frontend.*

## 6. Run the Server

Finally, start the Django development server:

```bash
python manage.py runserver
```

The backend is now running at `http://127.0.0.1:8000`. You can now start the React frontend in a separate terminal.
