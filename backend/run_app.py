import os
import sys

def runmigration():
    try:
        # Running migrations
        os.system("python manage.py makemigrations")
        os.system("python manage.py migrate")
        print("Migrations applied successfully.")
    except Exception as e:
        print(f"Error while applying migrations: {e}")
        sys.exit(1)

def runserver():
    try:
        # Running the server
        os.system("python manage.py runserver")
    except Exception as e:
        print(f"Error while running the server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        runmigration()
        runserver()
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)