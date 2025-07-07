# -*- coding: utf-8 -*-


import sqlite3
import os
from datetime import datetime

# --- Database Setup ---
# Define the database file name. SQLite creates a file-based database.
DB_FILE = 'tasks.db'

def connect_db():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row # This allows accessing columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def create_table():
    """Creates the 'tasks' table if it doesn't already exist."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    due_date TEXT, -- Stored as YYYY-MM-DD
                    completed INTEGER DEFAULT 0 -- 0 for false, 1 for true
                );
            """)
            conn.commit()
            print("Database table 'tasks' ensured.")
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")
        finally:
            conn.close()

# --- Task Operations ---

def add_task(description, due_date=None):
    """Adds a new task to the database."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tasks (description, due_date) VALUES (?, ?)",
                           (description, due_date))
            conn.commit()
            print(f"Task '{description}' added successfully!")
        except sqlite3.Error as e:
            print(f"Error adding task: {e}")
        finally:
            conn.close()

def view_tasks(show_completed=False):
    """Retrieves and displays tasks from the database."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            if show_completed:
                cursor.execute("SELECT id, description, due_date, completed FROM tasks ORDER BY completed ASC, due_date ASC, id ASC")
            else:
                cursor.execute("SELECT id, description, due_date, completed FROM tasks WHERE completed = 0 ORDER BY due_date ASC, id ASC")

            tasks = cursor.fetchall()
            if not tasks:
                print("\nNo tasks found.")
                return

            print("\n--- Your Tasks ---")
            for task in tasks:
                status = "[DONE]" if task['completed'] == 1 else "[TODO]"
                due = f"(Due: {task['due_date']})" if task['due_date'] else ""
                print(f"{task['id']}. {status} {task['description']} {due}")
            print("------------------")
        except sqlite3.Error as e:
            print(f"Error viewing tasks: {e}")
        finally:
            conn.close()

def complete_task(task_id):
    """Marks a task as completed."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE tasks SET completed = 1 WHERE id = ?", (task_id,))
            if cursor.rowcount > 0:
                conn.commit()
                print(f"Task {task_id} marked as completed!")
            else:
                print(f"Task {task_id} not found or already completed.")
        except sqlite3.Error as e:
            print(f"Error completing task: {e}")
        finally:
            conn.close()

def delete_task(task_id):
    """Deletes a task from the database."""
    conn = connect_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            if cursor.rowcount > 0:
                conn.commit()
                print(f"Task {task_id} deleted successfully!")
            else:
                print(f"Task {task_id} not found.")
        except sqlite3.Error as e:
            print(f"Error deleting task: {e}")
        finally:
            conn.close()

# --- User Interface / Main Loop ---

def display_menu():
    """Displays the main menu options to the user."""
    print("\n--- Task Manager Menu ---")
    print("1. Add Task")
    print("2. View Tasks (To-Do)")
    print("3. View All Tasks (Including Completed)")
    print("4. Complete Task")
    print("5. Delete Task")
    print("6. Exit")
    print("-------------------------")

def get_valid_date_input(prompt):
    """Prompts the user for a date and validates its format (YYYY-MM-DD)."""
    while True:
        date_str = input(prompt).strip()
        if not date_str: # Allow empty string for no due date
            return None
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD (e.g., 2025-12-31) or leave blank.")

def get_valid_task_id_input(prompt):
    """Prompts the user for a task ID and validates it as an integer."""
    while True:
        try:
            task_id_str = input(prompt).strip()
            task_id = int(task_id_str)
            if task_id <= 0:
                print("Task ID must be a positive number.")
            else:
                return task_id
        except ValueError:
            print("Invalid input. Please enter a number for the Task ID.")

def main():
    """Main function to run the Task Manager application."""
    create_table() # Ensure the database table exists

    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == '1':
            description = input("Enter task description: ").strip()
            if description:
                due_date = get_valid_date_input("Enter due date (YYYY-MM-DD, leave blank for none): ")
                add_task(description, due_date)
            else:
                print("Task description cannot be empty.")
        elif choice == '2':
            view_tasks(show_completed=False)
        elif choice == '3':
            view_tasks(show_completed=True)
        elif choice == '4':
            task_id = get_valid_task_id_input("Enter the ID of the task to complete: ")
            if task_id is not None:
                complete_task(task_id)
        elif choice == '5':
            task_id = get_valid_task_id_input("Enter the ID of the task to delete: ")
            if task_id is not None:
                delete_task(task_id)
        elif choice == '6':
            print("Exiting Task Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
