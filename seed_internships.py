import sqlite3

from database import get_db_connection, create_database


def seed_internships():
    create_database()

    connection = get_db_connection()

    existing_count = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM internships
        """
    ).fetchone()["total"]

    if existing_count > 0:
        print(
            f"Internships already exist in the database. "
            f"Current count: {existing_count}"
        )
        connection.close()
        return

    internships = [
        {
            "company_name": "TechNova Solutions",
            "role_title": "Python Developer Intern",
            "location": "Bengaluru",
            "work_mode": "Hybrid",
            "duration": "3 Months",
            "stipend": "₹15,000/month",
            "description": "Build and maintain Python web applications, backend services and REST APIs with the development team.",
            "required_skills": "Python, Flask, SQL, Git",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE",
            "eligible_branches": "Computer Science, Information Technology",
            "eligible_years": "2, 3, 4",
            "minimum_score": 60,
            "score_type": "Percentage",
            "openings": 3,
            "application_deadline": "2026-10-31",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "DataVista Labs",
            "role_title": "Data Analyst Intern",
            "location": "Bengaluru",
            "work_mode": "On-site",
            "duration": "4 Months",
            "stipend": "₹18,000/month",
            "description": "Analyze datasets, prepare dashboards and generate useful business insights using reporting and visualization tools.",
            "required_skills": "SQL, Excel, Power BI, Python",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE",
            "eligible_branches": "Computer Science, Information Technology, Data Science",
            "eligible_years": "2, 3, 4",
            "minimum_score": 60,
            "score_type": "Percentage",
            "openings": 2,
            "application_deadline": "2026-11-15",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "CloudSprint Technologies",
            "role_title": "Web Development Intern",
            "location": "Remote",
            "work_mode": "Remote",
            "duration": "3 Months",
            "stipend": "₹12,000/month",
            "description": "Build responsive web interfaces and assist with the development of modern web applications.",
            "required_skills": "HTML, CSS, JavaScript, React, Git",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE",
            "eligible_branches": "Computer Science, Information Technology",
            "eligible_years": "1, 2, 3, 4",
            "minimum_score": 55,
            "score_type": "Percentage",
            "openings": 4,
            "application_deadline": "2026-11-30",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "NexaByte Systems",
            "role_title": "Backend Development Intern",
            "location": "Bengaluru",
            "work_mode": "Hybrid",
            "duration": "6 Months",
            "stipend": "₹20,000/month",
            "description": "Develop backend services, database operations and REST APIs for software applications.",
            "required_skills": "Python, Flask, SQL, REST API, Git",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE",
            "eligible_branches": "Computer Science, Information Technology",
            "eligible_years": "3, 4",
            "minimum_score": 65,
            "score_type": "Percentage",
            "openings": 2,
            "application_deadline": "2026-12-10",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "InsightForge Analytics",
            "role_title": "Business Intelligence Intern",
            "location": "Remote",
            "work_mode": "Remote",
            "duration": "3 Months",
            "stipend": "₹14,000/month",
            "description": "Create interactive dashboards and assist with data cleaning, reporting and business intelligence tasks.",
            "required_skills": "Power BI, Excel, SQL, Data Analysis",
            "eligible_courses": "B.Sc, BCA, B.Com, BBA, B.Tech",
            "eligible_branches": "Computer Science, Information Technology, Data Science, Commerce",
            "eligible_years": "2, 3, 4",
            "minimum_score": 55,
            "score_type": "Percentage",
            "openings": 3,
            "application_deadline": "2026-12-20",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "CodeOrbit Innovations",
            "role_title": "Java Developer Intern",
            "location": "Bengaluru",
            "work_mode": "On-site",
            "duration": "4 Months",
            "stipend": "₹16,000/month",
            "description": "Assist with building Java applications and implementing object-oriented software components.",
            "required_skills": "Java, OOP, SQL, Git",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE",
            "eligible_branches": "Computer Science, Information Technology",
            "eligible_years": "2, 3, 4",
            "minimum_score": 60,
            "score_type": "Percentage",
            "openings": 2,
            "application_deadline": "2026-10-25",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "AetherAI Research",
            "role_title": "Machine Learning Intern",
            "location": "Remote",
            "work_mode": "Remote",
            "duration": "6 Months",
            "stipend": "₹25,000/month",
            "description": "Support machine learning experiments, data preprocessing and model evaluation for applied AI projects.",
            "required_skills": "Python, Machine Learning, Pandas, NumPy, Scikit-learn",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE, M.Sc, MCA",
            "eligible_branches": "Computer Science, Information Technology, Data Science, Artificial Intelligence",
            "eligible_years": "3, 4",
            "minimum_score": 70,
            "score_type": "Percentage",
            "openings": 2,
            "application_deadline": "2026-12-31",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "PixelCraft Digital",
            "role_title": "Frontend Developer Intern",
            "location": "Remote",
            "work_mode": "Remote",
            "duration": "3 Months",
            "stipend": "₹10,000/month",
            "description": "Develop responsive user interfaces and reusable frontend components for web applications.",
            "required_skills": "HTML, CSS, JavaScript, React, Tailwind CSS",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE",
            "eligible_branches": "Computer Science, Information Technology",
            "eligible_years": "1, 2, 3, 4",
            "minimum_score": 50,
            "score_type": "Percentage",
            "openings": 5,
            "application_deadline": "2026-11-20",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "SecureStack Labs",
            "role_title": "Cybersecurity Intern",
            "location": "Bengaluru",
            "work_mode": "Hybrid",
            "duration": "4 Months",
            "stipend": "₹18,000/month",
            "description": "Assist with security monitoring, vulnerability assessment and basic network security activities.",
            "required_skills": "Cybersecurity, Network Security, Networking, Linux",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE",
            "eligible_branches": "Computer Science, Information Technology, Cybersecurity",
            "eligible_years": "2, 3, 4",
            "minimum_score": 65,
            "score_type": "Percentage",
            "openings": 2,
            "application_deadline": "2026-12-05",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "DevFlow Technologies",
            "role_title": "DevOps Intern",
            "location": "Remote",
            "work_mode": "Remote",
            "duration": "5 Months",
            "stipend": "₹22,000/month",
            "description": "Support deployment pipelines, containerized applications and cloud infrastructure tasks.",
            "required_skills": "Git, Docker, Linux, AWS, DevOps",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE",
            "eligible_branches": "Computer Science, Information Technology",
            "eligible_years": "3, 4",
            "minimum_score": 60,
            "score_type": "Percentage",
            "openings": 2,
            "application_deadline": "2026-12-15",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "AppNest Technologies",
            "role_title": "Mobile App Development Intern",
            "location": "Bengaluru",
            "work_mode": "Hybrid",
            "duration": "3 Months",
            "stipend": "₹15,000/month",
            "description": "Build mobile application features and integrate frontend applications with backend APIs.",
            "required_skills": "Flutter, Android, REST API, Git",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE",
            "eligible_branches": "Computer Science, Information Technology",
            "eligible_years": "2, 3, 4",
            "minimum_score": 55,
            "score_type": "Percentage",
            "openings": 3,
            "application_deadline": "2026-11-25",
            "application_link": "",
            "status": "Active"
        },
        {
            "company_name": "QueryWorks Software",
            "role_title": "Database Intern",
            "location": "Bengaluru",
            "work_mode": "On-site",
            "duration": "3 Months",
            "stipend": "₹13,000/month",
            "description": "Assist with database design, SQL queries, data validation and application database support.",
            "required_skills": "SQL, MySQL, PostgreSQL, Python",
            "eligible_courses": "B.Sc, BCA, B.Tech, BE",
            "eligible_branches": "Computer Science, Information Technology",
            "eligible_years": "2, 3, 4",
            "minimum_score": 55,
            "score_type": "Percentage",
            "openings": 3,
            "application_deadline": "2026-12-01",
            "application_link": "",
            "status": "Active"
        }
    ]

    insert_query = """
        INSERT INTO internships (
            company_name,
            role_title,
            location,
            work_mode,
            duration,
            stipend,
            description,
            required_skills,
            eligible_courses,
            eligible_branches,
            eligible_years,
            minimum_score,
            score_type,
            openings,
            application_deadline,
            application_link,
            status
        )
        VALUES (
            :company_name,
            :role_title,
            :location,
            :work_mode,
            :duration,
            :stipend,
            :description,
            :required_skills,
            :eligible_courses,
            :eligible_branches,
            :eligible_years,
            :minimum_score,
            :score_type,
            :openings,
            :application_deadline,
            :application_link,
            :status
        )
    """

    try:
        for internship in internships:
            connection.execute(
                insert_query,
                internship
            )

        connection.commit()

    except sqlite3.Error as error:
        connection.rollback()
        connection.close()
        print(f"Could not seed internships: {error}")
        return

    total = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM internships
        """
    ).fetchone()["total"]

    connection.close()

    print("Sample internships added successfully.")
    print(f"Total internships: {total}")


if __name__ == "__main__":
    seed_internships()