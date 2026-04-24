#!/usr/bin/env python3
"""
cleanup.py — Reset your Django project safely.

Removes:
- All SQLite database data (or drops all tables if using PostgreSQL/MySQL)
- All migration files (except __init__.py)
- Recreates empty migrations

⚠️ Use for development only! DO NOT run in production.
"""

import os
import shutil
import django
from django.conf import settings
from django.core.management import call_command

# --- Setup Django ---
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mpaeureview")
django.setup()


def delete_migrations():
    """Delete all migration files except __init__.py."""
    print("🧩 Cleaning migration files...")
    for app in settings.INSTALLED_APPS:
        # Skip built-in Django/system apps
        if not app.startswith("django.") and not app.startswith("import_export"):
            app_path = app.replace(".", "/")
            migrations_dir = os.path.join(settings.BASE_DIR, app_path, "migrations")
            if os.path.exists(migrations_dir):
                for filename in os.listdir(migrations_dir):
                    if filename != "__init__.py" and filename.endswith(".py"):
                        os.remove(os.path.join(migrations_dir, filename))
                for filename in os.listdir(migrations_dir):
                    if filename.endswith(".pyc"):
                        os.remove(os.path.join(migrations_dir, filename))
                print(f"  ✅ Cleaned {migrations_dir}")


def reset_database():
    """Drop and recreate the database."""
    #db_settings = settings.DATABASES["default"]
    #engine = db_settings["ENGINE"]
    engine = "sqlite3"  # Simplified for this example

    if "sqlite3" in engine:
        #db_path = db_settings["NAME"]
        db_path = "db.sqlite3"
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"💾 Removed SQLite database: {db_path}")
    else:
        print("⚠️ Non-SQLite database detected. Using Django flush.")
        call_command("flush", "--no-input")

    print("✅ Database cleaned.")


def recreate_migrations():
    """Recreate fresh migrations for all local apps."""
    print("🛠️  Creating fresh migrations...")
    call_command("makemigrations")
    print("✅ Migrations recreated.")


def migrate():
    """Run migrations."""
    print("🚀 Applying migrations...")
    call_command("migrate")
    print("✅ Database ready.")


def main():
    print("\n=== 🧹 Django Project Cleanup Tool ===\n")
    confirm = input("This will DELETE ALL DATA and MIGRATIONS. Are you sure? (yes/no): ").lower()
    if confirm != "yes":
        print("❌ Aborted.")
        return

    delete_migrations()
    reset_database()
    recreate_migrations()
    migrate()
    print("\n✨ Done! Your project is completely clean.\n")


if __name__ == "__main__":
    main()
