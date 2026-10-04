import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "intern.db")


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_database():
    connection = get_db_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            student_id TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL UNIQUE,
            course TEXT NOT NULL,
            branch TEXT NOT NULL,
            current_year INTEGER NOT NULL,
            college TEXT NOT NULL,
            graduation_year INTEGER NOT NULL,
            academic_score REAL,
            score_type TEXT,
            interests TEXT,
            career_goal TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS student_skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE,
            UNIQUE(student_id, skill_name)
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS student_resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL UNIQUE,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            extracted_text TEXT NOT NULL,
            detected_skills TEXT,
            detected_education TEXT,
            detected_experience TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id)
                REFERENCES students(id)
                ON DELETE CASCADE
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS internships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            role_title TEXT NOT NULL,
            location TEXT NOT NULL,
            work_mode TEXT NOT NULL,
            duration TEXT NOT NULL,
            stipend TEXT,
            description TEXT NOT NULL,
            required_skills TEXT NOT NULL,
            eligible_courses TEXT,
            eligible_branches TEXT,
            eligible_years TEXT,
            minimum_score REAL,
            score_type TEXT,
            openings INTEGER DEFAULT 1,
            application_deadline TEXT,
            application_link TEXT,
            status TEXT NOT NULL DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_students_email
        ON students(email)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_admins_email
        ON admins(email)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_internships_company
        ON internships(company_name)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_internships_role
        ON internships(role_title)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_internships_location
        ON internships(location)
        """
    )

    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_internships_status
        ON internships(status)
        """
    )

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_database()
    print("INTERN database created successfully.")