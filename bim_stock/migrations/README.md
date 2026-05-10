# BIM Stock Migrations

This folder stores Django migration files for the `bim_stock` app.

Migrations describe database changes over time:
- creating tables
- adding fields
- renaming fields or models
- changing constraints

Run migrations with:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

Create new migrations after model changes with:

```powershell
.\.venv\Scripts\python.exe manage.py makemigrations
```

Do not manually edit old migration files unless there is a specific database
repair reason. They are the history Django uses to build the database.
