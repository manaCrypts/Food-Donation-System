# Food Donation System

A complete Flask website for managing food donations with a donor form, recipient search, and admin dashboard.

## Features
- Submit a food donation with pickup details
- Search available donations by food type and city
- View current donations in a clean results page
- Admin dashboard to monitor donations and mark items as taken

## Setup
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create the SQLite database:
   ```bash
   python create_db.py
   ```
4. Run the application:
   ```bash
   python app.py
   ```
5. Open the website at `http://127.0.0.1:5000`

## Admin Dashboard
- Visit `/admin-login`
- Default credentials:
  - username: `admin`
  - password: `password123`

To change admin credentials, set environment variables before running the app:
```bash
set ADMIN_USERNAME=admin
set ADMIN_PASSWORD=securepass
set SECRET_KEY=your-secret-key
```
