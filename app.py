import os
import re
import sqlite3
import uuid

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.exceptions import RequestEntityTooLarge
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from database import get_db_connection, create_database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads", "resumes")
MAX_RESUME_SIZE = 5 * 1024 * 1024

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

app.config["SECRET_KEY"] = "intern-development-secret-key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_RESUME_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

create_database()


def valid_full_name(name):
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z\s'-]{1,49}", name))


def valid_student_id(student_id):
    return bool(re.fullmatch(r"[A-Za-z0-9]+", student_id))


def valid_gmail(email):
    pattern = r"^[A-Za-z0-9](?:[A-Za-z0-9.]{0,28}[A-Za-z0-9])?@gmail\.com$"

    if not re.fullmatch(pattern, email, re.IGNORECASE):
        return False

    local_part = email.split("@")[0]

    if ".." in local_part:
        return False

    return True


def allowed_resume_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() == "pdf"
    )


def has_pdf_signature(file_storage):
    current_position = file_storage.stream.tell()

    file_storage.stream.seek(0)
    signature = file_storage.stream.read(5)
    file_storage.stream.seek(current_position)

    return signature == b"%PDF-"


def get_uploaded_file_size(file_storage):
    current_position = file_storage.stream.tell()

    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(current_position)

    return size


def extract_pdf_text(file_path):
    reader = PdfReader(file_path)

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            raise ValueError("Encrypted PDF")

    pages = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            pages.append(page_text)

    return "\n".join(pages).strip()


def detect_resume_skills(text):
    skill_patterns = {
        "Python": [r"\bpython\b"],
        "Java": [r"\bjava\b"],
        "C": [r"(?<!\+)(?<!#)\bc\b(?!\+\+|#)"],
        "C++": [r"\bc\+\+\b"],
        "C#": [r"\bc#\b"],
        "JavaScript": [r"\bjavascript\b", r"\bjava\s+script\b"],
        "TypeScript": [r"\btypescript\b", r"\btype\s+script\b"],
        "HTML": [r"\bhtml5?\b"],
        "CSS": [r"\bcss3?\b"],
        "React": [r"\breact(?:\.js|js)?\b"],
        "Angular": [r"\bangular(?:\.js|js)?\b"],
        "Vue.js": [r"\bvue(?:\.js|js)?\b"],
        "Node.js": [r"\bnode(?:\.js|js)?\b"],
        "Express.js": [r"\bexpress(?:\.js|js)?\b"],
        "Flask": [r"\bflask\b"],
        "Django": [r"\bdjango\b"],
        "Spring Boot": [r"\bspring\s*boot\b"],
        "PHP": [r"\bphp\b"],
        "Bootstrap": [r"\bbootstrap\b"],
        "Tailwind CSS": [r"\btailwind(?:\s*css)?\b"],
        "SQL": [r"\bsql\b"],
        "MySQL": [r"\bmysql\b"],
        "PostgreSQL": [r"\bpostgresql\b", r"\bpostgres\b"],
        "SQLite": [r"\bsqlite\b"],
        "MongoDB": [r"\bmongodb\b", r"\bmongo\s*db\b"],
        "Oracle": [r"\boracle\b"],
        "Firebase": [r"\bfirebase\b"],
        "Power BI": [r"\bpower\s*bi\b"],
        "Tableau": [r"\btableau\b"],
        "Excel": [r"\bmicrosoft\s*excel\b", r"\bms\s*excel\b", r"\bexcel\b"],
        "Pandas": [r"\bpandas\b"],
        "NumPy": [r"\bnumpy\b"],
        "Matplotlib": [r"\bmatplotlib\b"],
        "Scikit-learn": [
            r"\bscikit[\s-]*learn\b",
            r"\bsklearn\b"
        ],
        "TensorFlow": [r"\btensorflow\b"],
        "Keras": [r"\bkeras\b"],
        "PyTorch": [r"\bpytorch\b"],
        "Machine Learning": [r"\bmachine\s+learning\b"],
        "Deep Learning": [r"\bdeep\s+learning\b"],
        "Artificial Intelligence": [
            r"\bartificial\s+intelligence\b"
        ],
        "Data Science": [r"\bdata\s+science\b"],
        "Data Analysis": [
            r"\bdata\s+analysis\b",
            r"\bdata\s+analytics\b"
        ],
        "Natural Language Processing": [
            r"\bnatural\s+language\s+processing\b",
            r"\bnlp\b"
        ],
        "Computer Vision": [r"\bcomputer\s+vision\b"],
        "Git": [r"\bgit\b"],
        "GitHub": [r"\bgithub\b"],
        "Docker": [r"\bdocker\b"],
        "Kubernetes": [r"\bkubernetes\b"],
        "AWS": [
            r"\baws\b",
            r"\bamazon\s+web\s+services\b"
        ],
        "Microsoft Azure": [
            r"\bmicrosoft\s+azure\b",
            r"\bazure\b"
        ],
        "Google Cloud": [
            r"\bgoogle\s+cloud\b",
            r"\bgcp\b"
        ],
        "Linux": [r"\blinux\b"],
        "REST API": [
            r"\brest\s*api\b",
            r"\brestful\s+api\b",
            r"\brestful\s+apis\b"
        ],
        "API Development": [r"\bapi\s+development\b"],
        "Cybersecurity": [
            r"\bcybersecurity\b",
            r"\bcyber\s+security\b"
        ],
        "Network Security": [r"\bnetwork\s+security\b"],
        "Networking": [r"\bnetworking\b"],
        "Cloud Computing": [r"\bcloud\s+computing\b"],
        "DevOps": [r"\bdevops\b"],
        "Android": [r"\bandroid\b"],
        "Kotlin": [r"\bkotlin\b"],
        "Flutter": [r"\bflutter\b"],
        "React Native": [r"\breact\s+native\b"],
        "Figma": [r"\bfigma\b"],
        "UI/UX Design": [
            r"\bui\s*/\s*ux\b",
            r"\bui\s+ux\b",
            r"\buser\s+interface\s+design\b",
            r"\buser\s+experience\s+design\b"
        ],
        "Data Structures": [
            r"\bdata\s+structures\b"
        ],
        "Algorithms": [r"\balgorithms?\b"],
        "OOP": [
            r"\boop\b",
            r"\bobject[\s-]+oriented\s+programming\b"
        ]
    }

    detected_skills = []

    for skill_name, patterns in skill_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected_skills.append(skill_name)
                break

    return detected_skills


def detect_resume_education(text):
    education_patterns = [
        (
            "Bachelor of Science",
            [
                r"\bbachelor\s+of\s+science\b",
                r"\bb\.?\s*sc\.?\b"
            ]
        ),
        (
            "Bachelor of Computer Applications",
            [
                r"\bbachelor\s+of\s+computer\s+applications\b",
                r"\bb\.?\s*c\.?\s*a\.?\b"
            ]
        ),
        (
            "Bachelor of Technology",
            [
                r"\bbachelor\s+of\s+technology\b",
                r"\bb\.?\s*tech\.?\b"
            ]
        ),
        (
            "Bachelor of Engineering",
            [
                r"\bbachelor\s+of\s+engineering\b",
                r"\bb\.?\s*e\.?\b"
            ]
        ),
        (
            "Bachelor of Commerce",
            [
                r"\bbachelor\s+of\s+commerce\b",
                r"\bb\.?\s*com\.?\b"
            ]
        ),
        (
            "Bachelor of Business Administration",
            [
                r"\bbachelor\s+of\s+business\s+administration\b",
                r"\bb\.?\s*b\.?\s*a\.?\b"
            ]
        ),
        (
            "Master of Science",
            [
                r"\bmaster\s+of\s+science\b",
                r"\bm\.?\s*sc\.?\b"
            ]
        ),
        (
            "Master of Computer Applications",
            [
                r"\bmaster\s+of\s+computer\s+applications\b",
                r"\bm\.?\s*c\.?\s*a\.?\b"
            ]
        ),
        (
            "Master of Technology",
            [
                r"\bmaster\s+of\s+technology\b",
                r"\bm\.?\s*tech\.?\b"
            ]
        ),
        (
            "Computer Science",
            [
                r"\bcomputer\s+science\b"
            ]
        ),
        (
            "Information Technology",
            [
                r"\binformation\s+technology\b"
            ]
        )
    ]

    detected = []

    for label, patterns in education_patterns:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(label)
                break

    year_matches = re.findall(
        r"\b(?:19|20)\d{2}\b",
        text
    )

    years = []

    for year in year_matches:
        if year not in years:
            years.append(year)

    if years:
        detected.append(
            "Years mentioned: " + ", ".join(years[:6])
        )

    if not detected:
        return "No clear education details were automatically detected."

    return " • ".join(detected)


def detect_resume_experience(text):
    experience_keywords = [
        "internship",
        "intern",
        "experience",
        "work experience",
        "employment",
        "project",
        "projects",
        "freelance",
        "volunteer"
    ]

    lines = [
        re.sub(r"\s+", " ", line).strip()
        for line in text.splitlines()
        if line.strip()
    ]

    matched_lines = []

    for line in lines:
        lower_line = line.lower()

        if any(
            keyword in lower_line
            for keyword in experience_keywords
        ):
            if len(line) >= 4 and line not in matched_lines:
                matched_lines.append(line)

        if len(matched_lines) >= 8:
            break

    if not matched_lines:
        return "No clear experience or project details were automatically detected."

    return " • ".join(matched_lines)


def validate_resume_content(text):
    normalized_text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    if len(normalized_text) < 150:
        return False, (
            "This PDF does not contain enough readable text to verify "
            "that it is a resume. Please upload a complete text-based resume."
        )

    categories = {
        "contact": [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            r"(?:\+?\d[\d\s().-]{7,}\d)",
            r"\blinkedin(?:\.com)?\b",
            r"\bgithub(?:\.com)?\b"
        ],
        "education": [
            r"\beducation\b",
            r"\bacademic\b",
            r"\bcollege\b",
            r"\buniversity\b",
            r"\bdegree\b",
            r"\bbachelor\b",
            r"\bmaster\b",
            r"\bb\.?\s*sc\.?\b",
            r"\bb\.?\s*tech\.?\b",
            r"\bb\.?\s*c\.?\s*a\.?\b",
            r"\bm\.?\s*sc\.?\b",
            r"\bm\.?\s*c\.?\s*a\.?\b",
            r"\bcgpa\b",
            r"\bgpa\b"
        ],
        "skills": [
            r"\bskills?\b",
            r"\btechnical\s+skills?\b",
            r"\btechnologies\b",
            r"\bprogramming\b",
            r"\bpython\b",
            r"\bjava\b",
            r"\bjavascript\b",
            r"\bhtml\b",
            r"\bcss\b",
            r"\bsql\b",
            r"\bflask\b",
            r"\breact\b",
            r"\bpower\s*bi\b"
        ],
        "experience": [
            r"\bexperience\b",
            r"\bwork\s+experience\b",
            r"\bemployment\b",
            r"\binternship\b",
            r"\bintern\b",
            r"\bworked\b",
            r"\bresponsibilities\b"
        ],
        "projects": [
            r"\bprojects?\b",
            r"\bproject\s+experience\b",
            r"\bdeveloped\b",
            r"\bbuilt\b",
            r"\bimplemented\b",
            r"\bcreated\b"
        ],
        "certifications": [
            r"\bcertifications?\b",
            r"\bcertificates?\b",
            r"\bcourses?\b",
            r"\btraining\b"
        ],
        "profile": [
            r"\bsummary\b",
            r"\bprofile\b",
            r"\bobjective\b",
            r"\bcareer\s+objective\b",
            r"\babout\s+me\b"
        ],
        "achievements": [
            r"\bachievements?\b",
            r"\bawards?\b",
            r"\bhonou?rs?\b",
            r"\bactivities\b",
            r"\bextracurricular\b"
        ]
    }

    matched_categories = []

    for category, patterns in categories.items():
        if any(
            re.search(pattern, normalized_text, re.IGNORECASE)
            for pattern in patterns
        ):
            matched_categories.append(category)

    detected_skills = detect_resume_skills(normalized_text)

    has_contact = "contact" in matched_categories
    has_education = "education" in matched_categories
    has_skills = (
        "skills" in matched_categories
        or len(detected_skills) >= 2
    )
    has_experience_or_projects = (
        "experience" in matched_categories
        or "projects" in matched_categories
    )

    strong_core_count = sum(
        [
            has_contact,
            has_education,
            has_skills,
            has_experience_or_projects
        ]
    )

    total_category_count = len(matched_categories)

    if (
        strong_core_count >= 3
        and total_category_count >= 3
    ):
        return True, None

    if (
        has_contact
        and has_education
        and total_category_count >= 4
    ):
        return True, None

    if (
        has_education
        and has_skills
        and has_experience_or_projects
        and total_category_count >= 3
    ):
        return True, None

    return False, (
        "This PDF does not appear to be a resume. Please upload a resume "
        "containing information such as contact details, education, skills, "
        "projects or work experience."
    )


@app.errorhandler(RequestEntityTooLarge)
def handle_large_resume(error):
    if "student_id" in session:
        flash(
            "Resume file is too large. Please upload a PDF smaller than 5 MB.",
            "error"
        )
        return redirect(url_for("resume"))

    flash(
        "The uploaded file is too large.",
        "error"
    )
    return redirect(url_for("login"))


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        student_id = request.form.get("student_id", "").strip().upper()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        terms = request.form.get("terms")

        errors = []

        if not full_name:
            errors.append("Please enter your full name.")
        elif not valid_full_name(full_name):
            errors.append(
                "Full name can contain only letters, spaces, apostrophes and hyphens."
            )

        if not student_id:
            errors.append("Please enter your Student ID.")
        elif len(student_id) < 3:
            errors.append(
                "Student ID must contain at least 3 characters."
            )
        elif len(student_id) > 20:
            errors.append(
                "Student ID cannot contain more than 20 characters."
            )
        elif not valid_student_id(student_id):
            errors.append(
                "Student ID can contain only letters and numbers."
            )

        if not email:
            errors.append("Please enter your Gmail address.")
        elif not valid_gmail(email):
            errors.append(
                "Please enter a valid Gmail address ending in @gmail.com."
            )

        if not password:
            errors.append("Please create a password.")
        else:
            if len(password) < 8:
                errors.append(
                    "Password must contain at least 8 characters."
                )

            if len(password) > 64:
                errors.append(
                    "Password cannot contain more than 64 characters."
                )

            if not re.search(r"[A-Z]", password):
                errors.append(
                    "Password must contain at least one uppercase letter."
                )

            if not re.search(r"[a-z]", password):
                errors.append(
                    "Password must contain at least one lowercase letter."
                )

            if not re.search(r"\d", password):
                errors.append(
                    "Password must contain at least one number."
                )

            if not re.search(r"[^A-Za-z0-9\s]", password):
                errors.append(
                    "Password must contain at least one special character."
                )

            if re.search(r"\s", password):
                errors.append(
                    "Password cannot contain spaces."
                )

        if not confirm_password:
            errors.append("Please confirm your password.")
        elif password != confirm_password:
            errors.append("Passwords do not match.")

        if not terms:
            errors.append(
                "Please accept the Terms of Use and Privacy Policy."
            )

        if errors:
            for error in errors:
                flash(error, "error")

            return render_template(
                "register.html",
                full_name=full_name,
                student_id=student_id,
                email=email
            )

        connection = get_db_connection()

        existing_student_id = connection.execute(
            "SELECT id FROM students WHERE student_id = ?",
            (student_id,)
        ).fetchone()

        existing_email = connection.execute(
            "SELECT id FROM students WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_student_id:
            connection.close()

            flash(
                "An account with this Student ID already exists.",
                "error"
            )

            return render_template(
                "register.html",
                full_name=full_name,
                student_id=student_id,
                email=email
            )

        if existing_email:
            connection.close()

            flash(
                "An account with this Gmail address already exists.",
                "error"
            )

            return render_template(
                "register.html",
                full_name=full_name,
                student_id=student_id,
                email=email
            )

        password_hash = generate_password_hash(password)

        try:
            connection.execute(
                """
                INSERT INTO students (
                    full_name,
                    student_id,
                    email,
                    password_hash
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    full_name,
                    student_id,
                    email,
                    password_hash
                )
            )

            connection.commit()

        except sqlite3.IntegrityError:
            connection.close()

            flash(
                "An account with these details already exists.",
                "error"
            )

            return render_template(
                "register.html",
                full_name=full_name,
                student_id=student_id,
                email=email
            )

        connection.close()

        flash(
            "Account created successfully. You can now log in.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")

        if not identifier:
            flash(
                "Please enter your Student ID or Gmail address.",
                "error"
            )

            return render_template(
                "login.html",
                identifier=identifier
            )

        if not password:
            flash(
                "Please enter your password.",
                "error"
            )

            return render_template(
                "login.html",
                identifier=identifier
            )

        connection = get_db_connection()

        if "@" in identifier:
            identifier = identifier.lower()

            if not valid_gmail(identifier):
                connection.close()

                flash(
                    "Please enter a valid Gmail address ending in @gmail.com.",
                    "error"
                )

                return render_template(
                    "login.html",
                    identifier=identifier
                )

            student = connection.execute(
                "SELECT * FROM students WHERE email = ?",
                (identifier,)
            ).fetchone()

        else:
            identifier = identifier.upper()

            if not valid_student_id(identifier):
                connection.close()

                flash(
                    "Please enter a valid Student ID.",
                    "error"
                )

                return render_template(
                    "login.html",
                    identifier=identifier
                )

            student = connection.execute(
                "SELECT * FROM students WHERE student_id = ?",
                (identifier,)
            ).fetchone()

        connection.close()

        if student is None:
            flash(
                "No account was found with those login details.",
                "error"
            )

            return render_template(
                "login.html",
                identifier=identifier
            )

        if not check_password_hash(
            student["password_hash"],
            password
        ):
            flash(
                "Incorrect password. Please try again.",
                "error"
            )

            return render_template(
                "login.html",
                identifier=identifier
            )

        session.clear()
        session["student_id"] = student["id"]
        session["student_name"] = student["full_name"]

        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "student_id" not in session:
        flash(
            "Please log in to access your dashboard.",
            "error"
        )
        return redirect(url_for("login"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT id, full_name, student_id, email, created_at
        FROM students
        WHERE id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    profile = connection.execute(
        """
        SELECT *
        FROM student_profiles
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    skills = connection.execute(
        """
        SELECT skill_name
        FROM student_skills
        WHERE student_id = ?
        ORDER BY skill_name COLLATE NOCASE
        """,
        (session["student_id"],)
    ).fetchall()

    resume = connection.execute(
        """
        SELECT *
        FROM student_resumes
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    connection.close()

    if student is None:
        session.clear()

        flash(
            "Your account could not be found. Please log in again.",
            "error"
        )

        return redirect(url_for("login"))

    profile_completion = 20

    if profile:
        profile_completion = 60

    if skills:
        profile_completion = 80

    if resume and resume["extracted_text"].strip():
        profile_completion = 100

    return render_template(
        "dashboard.html",
        student=student,
        profile=profile,
        skills=skills,
        resume=resume,
        profile_completion=profile_completion
    )


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "student_id" not in session:
        flash(
            "Please log in to access your profile.",
            "error"
        )
        return redirect(url_for("login"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT id, full_name, student_id, email
        FROM students
        WHERE id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    if student is None:
        connection.close()
        session.clear()

        flash(
            "Your account could not be found. Please log in again.",
            "error"
        )

        return redirect(url_for("login"))

    existing_profile = connection.execute(
        """
        SELECT *
        FROM student_profiles
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    if request.method == "POST":
        course = request.form.get("course", "").strip()
        branch = request.form.get("branch", "").strip()
        current_year = request.form.get("current_year", "").strip()
        college = request.form.get("college", "").strip()
        graduation_year = request.form.get("graduation_year", "").strip()
        academic_score = request.form.get("academic_score", "").strip()
        score_type = request.form.get("score_type", "").strip()
        interests = request.form.get("interests", "").strip()
        career_goal = request.form.get("career_goal", "").strip()

        errors = []

        if not course:
            errors.append("Please select your course.")

        if not branch:
            errors.append(
                "Please enter your branch or specialization."
            )

        if not current_year:
            errors.append("Please select your current year.")
        else:
            try:
                current_year_value = int(current_year)

                if current_year_value < 1 or current_year_value > 6:
                    errors.append(
                        "Please select a valid current year."
                    )

            except ValueError:
                errors.append(
                    "Please select a valid current year."
                )

        if not college:
            errors.append("Please enter your college name.")

        if not graduation_year:
            errors.append(
                "Please enter your expected graduation year."
            )
        else:
            try:
                graduation_year_value = int(graduation_year)

                if (
                    graduation_year_value < 2020
                    or graduation_year_value > 2040
                ):
                    errors.append(
                        "Please enter a valid graduation year."
                    )

            except ValueError:
                errors.append(
                    "Please enter a valid graduation year."
                )

        if not score_type:
            errors.append(
                "Please select CGPA or Percentage."
            )

        if academic_score:
            try:
                score_value = float(academic_score)

                if score_type == "CGPA":
                    if score_value < 0 or score_value > 10:
                        errors.append(
                            "CGPA must be between 0 and 10."
                        )

                elif score_type == "Percentage":
                    if score_value < 0 or score_value > 100:
                        errors.append(
                            "Percentage must be between 0 and 100."
                        )

            except ValueError:
                errors.append(
                    "Please enter a valid academic score."
                )

        else:
            errors.append(
                "Please enter your academic score."
            )

        if not interests:
            errors.append(
                "Please enter at least one area of interest."
            )

        if not career_goal:
            errors.append(
                "Please enter your career goal."
            )

        form_data = {
            "course": course,
            "branch": branch,
            "current_year": current_year,
            "college": college,
            "graduation_year": graduation_year,
            "academic_score": academic_score,
            "score_type": score_type,
            "interests": interests,
            "career_goal": career_goal
        }

        if errors:
            connection.close()

            for error in errors:
                flash(error, "error")

            return render_template(
                "profile.html",
                student=student,
                profile=form_data
            )

        if existing_profile:
            connection.execute(
                """
                UPDATE student_profiles
                SET
                    course = ?,
                    branch = ?,
                    current_year = ?,
                    college = ?,
                    graduation_year = ?,
                    academic_score = ?,
                    score_type = ?,
                    interests = ?,
                    career_goal = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE student_id = ?
                """,
                (
                    course,
                    branch,
                    int(current_year),
                    college,
                    int(graduation_year),
                    float(academic_score),
                    score_type,
                    interests,
                    career_goal,
                    session["student_id"]
                )
            )

        else:
            connection.execute(
                """
                INSERT INTO student_profiles (
                    student_id,
                    course,
                    branch,
                    current_year,
                    college,
                    graduation_year,
                    academic_score,
                    score_type,
                    interests,
                    career_goal
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["student_id"],
                    course,
                    branch,
                    int(current_year),
                    college,
                    int(graduation_year),
                    float(academic_score),
                    score_type,
                    interests,
                    career_goal
                )
            )

        connection.commit()
        connection.close()

        flash(
            "Your student profile has been saved successfully.",
            "success"
        )

        return redirect(url_for("profile"))

    connection.close()

    return render_template(
        "profile.html",
        student=student,
        profile=existing_profile
    )


@app.route("/skills", methods=["GET", "POST"])
def skills():
    if "student_id" not in session:
        flash(
            "Please log in to manage your skills.",
            "error"
        )
        return redirect(url_for("login"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT id, full_name, student_id, email
        FROM students
        WHERE id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    if student is None:
        connection.close()
        session.clear()

        flash(
            "Your account could not be found. Please log in again.",
            "error"
        )

        return redirect(url_for("login"))

    if request.method == "POST":
        skills_value = request.form.get("skills", "").strip()

        submitted_skills = []
        seen_skills = set()

        for skill in skills_value.split(","):
            cleaned_skill = re.sub(r"\s+", " ", skill).strip()

            if not cleaned_skill:
                continue

            skill_key = cleaned_skill.casefold()

            if skill_key not in seen_skills:
                seen_skills.add(skill_key)
                submitted_skills.append(cleaned_skill)

        errors = []

        if not submitted_skills:
            errors.append(
                "Please select or add at least one skill."
            )

        if len(submitted_skills) > 30:
            errors.append(
                "You can save up to 30 skills."
            )

        if any(len(skill) > 40 for skill in submitted_skills):
            errors.append(
                "Each skill name must contain 40 characters or fewer."
            )

        if errors:
            connection.close()

            for error in errors:
                flash(error, "error")

            return render_template(
                "skills.html",
                student=student,
                saved_skills=submitted_skills
            )

        try:
            connection.execute(
                """
                DELETE FROM student_skills
                WHERE student_id = ?
                """,
                (session["student_id"],)
            )

            connection.executemany(
                """
                INSERT INTO student_skills (
                    student_id,
                    skill_name
                )
                VALUES (?, ?)
                """,
                [
                    (session["student_id"], skill)
                    for skill in submitted_skills
                ]
            )

            connection.commit()

        except sqlite3.IntegrityError:
            connection.rollback()
            connection.close()

            flash(
                "Your skills could not be saved. Please try again.",
                "error"
            )

            return render_template(
                "skills.html",
                student=student,
                saved_skills=submitted_skills
            )

        connection.close()

        flash(
            "Your skills have been saved successfully.",
            "success"
        )

        return redirect(url_for("skills"))

    saved_skill_rows = connection.execute(
        """
        SELECT skill_name
        FROM student_skills
        WHERE student_id = ?
        ORDER BY skill_name COLLATE NOCASE
        """,
        (session["student_id"],)
    ).fetchall()

    connection.close()

    saved_skills = [
        row["skill_name"]
        for row in saved_skill_rows
    ]

    return render_template(
        "skills.html",
        student=student,
        saved_skills=saved_skills
    )


@app.route("/resume", methods=["GET", "POST"])
def resume():
    if "student_id" not in session:
        flash(
            "Please log in to manage your resume.",
            "error"
        )
        return redirect(url_for("login"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT id, full_name, student_id, email
        FROM students
        WHERE id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    if student is None:
        connection.close()
        session.clear()

        flash(
            "Your account could not be found. Please log in again.",
            "error"
        )

        return redirect(url_for("login"))

    existing_resume = connection.execute(
        """
        SELECT *
        FROM student_resumes
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    if request.method == "POST":
        if "resume" not in request.files:
            connection.close()

            flash(
                "Please choose a PDF resume to upload.",
                "error"
            )

            return redirect(url_for("resume"))

        resume_file = request.files["resume"]

        if not resume_file or not resume_file.filename:
            connection.close()

            flash(
                "Please choose a PDF resume to upload.",
                "error"
            )

            return redirect(url_for("resume"))

        original_filename = secure_filename(
            resume_file.filename
        )

        if not original_filename:
            connection.close()

            flash(
                "The selected file name is not valid.",
                "error"
            )

            return redirect(url_for("resume"))

        if not allowed_resume_file(original_filename):
            connection.close()

            flash(
                "Only PDF resume files are supported. Please upload a file ending in .pdf.",
                "error"
            )

            return redirect(url_for("resume"))

        file_size = get_uploaded_file_size(
            resume_file
        )

        if file_size <= 0:
            connection.close()

            flash(
                "The selected PDF is empty. Please choose a valid resume.",
                "error"
            )

            return redirect(url_for("resume"))

        if file_size > MAX_RESUME_SIZE:
            connection.close()

            flash(
                "Resume file is too large. Please upload a PDF smaller than 5 MB.",
                "error"
            )

            return redirect(url_for("resume"))

        if not has_pdf_signature(resume_file):
            connection.close()

            flash(
                "The selected file is not a valid PDF. Renamed or unsupported files cannot be uploaded.",
                "error"
            )

            return redirect(url_for("resume"))

        stored_filename = (
            f"{session['student_id']}_"
            f"{uuid.uuid4().hex}.pdf"
        )

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            stored_filename
        )

        try:
            resume_file.stream.seek(0)
            resume_file.save(file_path)

            extracted_text = extract_pdf_text(
                file_path
            )

        except Exception:
            if os.path.exists(file_path):
                os.remove(file_path)

            connection.close()

            flash(
                "INTERN could not read this PDF. Please upload a valid, non-encrypted, text-based resume PDF.",
                "error"
            )

            return redirect(url_for("resume"))

        if not extracted_text:
            if os.path.exists(file_path):
                os.remove(file_path)

            connection.close()

            flash(
                "No readable text was found in this PDF. Scanned or image-only resumes are not supported yet.",
                "error"
            )

            return redirect(url_for("resume"))

        is_resume, validation_error = validate_resume_content(
            extracted_text
        )

        if not is_resume:
            if os.path.exists(file_path):
                os.remove(file_path)

            connection.close()

            flash(
                validation_error,
                "error"
            )

            return redirect(url_for("resume"))

        detected_skills_list = detect_resume_skills(
            extracted_text
        )

        detected_skills = ", ".join(
            detected_skills_list
        )

        detected_education = detect_resume_education(
            extracted_text
        )

        detected_experience = detect_resume_experience(
            extracted_text
        )

        old_stored_filename = None

        if existing_resume:
            old_stored_filename = existing_resume[
                "stored_filename"
            ]

        try:
            if existing_resume:
                connection.execute(
                    """
                    UPDATE student_resumes
                    SET
                        original_filename = ?,
                        stored_filename = ?,
                        extracted_text = ?,
                        detected_skills = ?,
                        detected_education = ?,
                        detected_experience = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE student_id = ?
                    """,
                    (
                        original_filename,
                        stored_filename,
                        extracted_text,
                        detected_skills,
                        detected_education,
                        detected_experience,
                        session["student_id"]
                    )
                )

            else:
                connection.execute(
                    """
                    INSERT INTO student_resumes (
                        student_id,
                        original_filename,
                        stored_filename,
                        extracted_text,
                        detected_skills,
                        detected_education,
                        detected_experience
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session["student_id"],
                        original_filename,
                        stored_filename,
                        extracted_text,
                        detected_skills,
                        detected_education,
                        detected_experience
                    )
                )

            connection.commit()

        except sqlite3.Error:
            connection.rollback()

            if os.path.exists(file_path):
                os.remove(file_path)

            connection.close()

            flash(
                "Your resume analysis could not be saved. Please try again.",
                "error"
            )

            return redirect(url_for("resume"))

        connection.close()

        if (
            old_stored_filename
            and old_stored_filename != stored_filename
        ):
            old_file_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                old_stored_filename
            )

            if os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                except OSError:
                    pass

        flash(
            "Your resume was verified, uploaded and analyzed successfully.",
            "success"
        )

        return redirect(url_for("resume"))

    connection.close()

    detected_skills = []

    if existing_resume and existing_resume["detected_skills"]:
        detected_skills = [
            skill.strip()
            for skill in existing_resume[
                "detected_skills"
            ].split(",")
            if skill.strip()
        ]

    return render_template(
        "resume.html",
        student=student,
        resume=existing_resume,
        detected_skills=detected_skills
    )


def normalize_list_value(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def normalize_eligibility_value(value):
    key = re.sub(r"[^a-z0-9]", "", str(value).casefold())

    aliases = {
        "bsc": "bsc",
        "bachelorofscience": "bsc",
        "bca": "bca",
        "bachelorofcomputerapplications": "bca",
        "btech": "btech",
        "bacheloroftechnology": "btech",
        "be": "be",
        "bachelorofengineering": "be",
        "bcom": "bcom",
        "bachelorofcommerce": "bcom",
        "bba": "bba",
        "bachelorofbusinessadministration": "bba",
        "msc": "msc",
        "masterofscience": "msc",
        "mca": "mca",
        "masterofcomputerapplications": "mca",
        "mtech": "mtech",
        "masteroftechnology": "mtech",
        "cs": "computerscience",
        "cse": "computerscience",
        "computerscience": "computerscience",
        "computerscienceengineering": "computerscience",
        "it": "informationtechnology",
        "informationtechnology": "informationtechnology",
        "datascience": "datascience",
        "ds": "datascience",
        "ai": "artificialintelligence",
        "artificialintelligence": "artificialintelligence",
        "cybersecurity": "cybersecurity",
        "cybersecurityengineering": "cybersecurity",
        "commerce": "commerce"
    }

    return aliases.get(key, key)


def internship_value_matches(student_value, allowed_values):
    if not allowed_values:
        return True

    student_key = normalize_eligibility_value(student_value)

    if not student_key:
        return False

    for allowed_value in allowed_values:
        allowed_key = normalize_eligibility_value(allowed_value)

        if not allowed_key:
            continue

        if student_key == allowed_key:
            return True

    return False


def evaluate_internship_eligibility(internship, profile):
    if not profile:
        return {
            "eligible": False,
            "status": "Profile required",
            "reasons": ["Complete your profile to check eligibility."]
        }

    reasons = []

    eligible_courses = normalize_list_value(internship["eligible_courses"])
    eligible_branches = normalize_list_value(internship["eligible_branches"])
    eligible_years = normalize_list_value(internship["eligible_years"])

    if not internship_value_matches(profile["course"], eligible_courses):
        reasons.append("Course requirement does not match your profile.")

    if not internship_value_matches(profile["branch"], eligible_branches):
        reasons.append("Branch requirement does not match your profile.")

    if eligible_years and str(profile["current_year"]) not in eligible_years:
        reasons.append("Current year is outside the eligible year range.")

    minimum_score = internship["minimum_score"]
    internship_score_type = internship["score_type"]
    student_score = profile["academic_score"]
    student_score_type = profile["score_type"]

    if minimum_score is not None:
        if student_score is None:
            reasons.append("Academic score is required to confirm eligibility.")
        elif internship_score_type and student_score_type:
            if internship_score_type.casefold() != student_score_type.casefold():
                reasons.append(
                    f"This internship uses {internship_score_type} for its academic requirement."
                )
            elif float(student_score) < float(minimum_score):
                reasons.append(
                    f"Minimum academic requirement is {minimum_score:g} {internship_score_type}."
                )
        elif float(student_score) < float(minimum_score):
            reasons.append(
                f"Minimum academic requirement is {minimum_score:g}."
            )

    if reasons:
        return {
            "eligible": False,
            "status": "Not eligible",
            "reasons": reasons
        }

    return {
        "eligible": True,
        "status": "Eligible",
        "reasons": ["Your saved profile meets the listed eligibility requirements."]
    }


def build_internship_skill_result(internship, student_skills):
    required_skills = normalize_list_value(internship["required_skills"])
    student_skill_map = {
        skill.casefold(): skill
        for skill in student_skills
    }

    matched_skills = []
    missing_skills = []

    for required_skill in required_skills:
        if required_skill.casefold() in student_skill_map:
            matched_skills.append(required_skill)
        else:
            missing_skills.append(required_skill)

    return {
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills
    }


def normalize_match_text(value):
    return re.sub(r"[^a-z0-9+#. ]", " ", str(value or "").casefold())


def calculate_tfidf_similarity(student_text, internship_text):
    student_text = re.sub(r"\s+", " ", str(student_text or "")).strip()
    internship_text = re.sub(r"\s+", " ", str(internship_text or "")).strip()

    if not student_text or not internship_text:
        return 0

    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z0-9+#.]*\b"
        )
        matrix = vectorizer.fit_transform([student_text, internship_text])
        similarity = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return round(float(similarity) * 100)
    except ValueError:
        return 0


def calculate_internship_match(internship, profile, student_skills, eligibility):
    required_skills = normalize_list_value(internship["required_skills"])

    if not profile or not student_skills or not required_skills:
        return {
            "score": None,
            "skill_score": None,
            "nlp_score": None,
            "matched_count": 0,
            "required_count": len(required_skills),
            "explanation": "Complete your profile and add skills or upload a resume to calculate a match score."
        }

    student_skill_keys = {
        re.sub(r"[^a-z0-9+#]", "", skill.casefold())
        for skill in student_skills
        if skill.strip()
    }

    matched_skills = []
    missing_skills = []

    for required_skill in required_skills:
        required_key = re.sub(r"[^a-z0-9+#]", "", required_skill.casefold())

        if required_key in student_skill_keys:
            matched_skills.append(required_skill)
        else:
            missing_skills.append(required_skill)

    matched_count = len(matched_skills)
    skill_score = round((matched_count / len(required_skills)) * 100)

    student_text = " ".join(
        [
            str(profile["course"] or ""),
            str(profile["branch"] or ""),
            str(profile["interests"] or ""),
            str(profile["career_goal"] or ""),
            " ".join(student_skills)
        ]
    )

    internship_text = " ".join(
        [
            str(internship["role_title"] or ""),
            str(internship["description"] or ""),
            str(internship["required_skills"] or ""),
            str(internship["eligible_courses"] or ""),
            str(internship["eligible_branches"] or "")
        ]
    )

    nlp_score = calculate_tfidf_similarity(student_text, internship_text)
    eligibility_score = 100 if eligibility["eligible"] else 0

    final_score = round(
        (skill_score * 0.65)
        + (nlp_score * 0.25)
        + (eligibility_score * 0.10)
    )

    if not eligibility["eligible"]:
        final_score = min(final_score, 69)

    explanation_parts = []

    if matched_skills:
        if len(matched_skills) == 1:
            matched_text = matched_skills[0]
        elif len(matched_skills) == 2:
            matched_text = " and ".join(matched_skills)
        else:
            matched_text = ", ".join(matched_skills[:-1]) + ", and " + matched_skills[-1]

        explanation_parts.append(
            f"Your profile matches this internship because you have {matched_text}, "
            f"covering {len(matched_skills)} of {len(required_skills)} listed required skills."
        )
    else:
        explanation_parts.append(
            "None of the listed required skills currently match your saved or resume-detected skills."
        )

    if nlp_score >= 60:
        explanation_parts.append(
            "TF-IDF text analysis shows strong similarity between your profile, interests, career goal and skills and the internship role description."
        )
    elif nlp_score >= 30:
        explanation_parts.append(
            "TF-IDF text analysis shows moderate similarity between your profile information and the internship role description."
        )
    elif nlp_score > 0:
        explanation_parts.append(
            "TF-IDF text analysis found some relevance between your profile information and the internship role description."
        )
    else:
        explanation_parts.append(
            "TF-IDF text analysis found little direct textual similarity between your profile information and this internship description."
        )

    if eligibility["eligible"]:
        explanation_parts.append(
            "Your academic profile also meets the listed eligibility requirements."
        )
    else:
        explanation_parts.append(
            "Your profile has one or more eligibility requirements that should be reviewed before applying."
        )

    if missing_skills:
        if len(missing_skills) == 1:
            missing_text = missing_skills[0]
        elif len(missing_skills) == 2:
            missing_text = " and ".join(missing_skills)
        else:
            missing_text = ", ".join(missing_skills[:-1]) + ", and " + missing_skills[-1]

        explanation_parts.append(
            f"Developing {missing_text} would improve your alignment with this internship."
        )
    else:
        explanation_parts.append(
            "Your current skills cover every listed required skill for this internship."
        )

    explanation = " ".join(explanation_parts)

    return {
        "score": final_score,
        "skill_score": skill_score,
        "nlp_score": nlp_score,
        "matched_count": matched_count,
        "required_count": len(required_skills),
        "explanation": explanation
    }


@app.route("/internships")
def internships():
    if "student_id" not in session:
        flash(
            "Please log in to find internships.",
            "error"
        )
        return redirect(url_for("login"))

    search_query = request.args.get("search", request.args.get("q", "")).strip()
    location_filter = request.args.get("location", "").strip()
    work_mode_filter = request.args.get("work_mode", "").strip()

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT id, full_name, student_id, email
        FROM students
        WHERE id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    if student is None:
        connection.close()
        session.clear()

        flash(
            "Your account could not be found. Please log in again.",
            "error"
        )
        return redirect(url_for("login"))

    profile = connection.execute(
        """
        SELECT *
        FROM student_profiles
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    saved_skill_rows = connection.execute(
        """
        SELECT skill_name
        FROM student_skills
        WHERE student_id = ?
        ORDER BY skill_name COLLATE NOCASE
        """,
        (session["student_id"],)
    ).fetchall()

    resume = connection.execute(
        """
        SELECT detected_skills
        FROM student_resumes
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    resume_skills = []

    if resume and resume["detected_skills"]:
        resume_skills = [
            skill.strip()
            for skill in resume["detected_skills"].split(",")
            if skill.strip()
        ]

    query = """
        SELECT *
        FROM internships
        WHERE status = 'Active'
    """
    parameters = []

    if search_query:
        search_value = f"%{search_query}%"
        query += """
            AND (
                company_name LIKE ? COLLATE NOCASE
                OR role_title LIKE ? COLLATE NOCASE
                OR required_skills LIKE ? COLLATE NOCASE
                OR description LIKE ? COLLATE NOCASE
            )
        """
        parameters.extend(
            [search_value, search_value, search_value, search_value]
        )

    if location_filter:
        query += " AND location = ? COLLATE NOCASE"
        parameters.append(location_filter)

    if work_mode_filter:
        query += " AND work_mode = ? COLLATE NOCASE"
        parameters.append(work_mode_filter)

    query += """
        ORDER BY
            application_deadline ASC,
            company_name COLLATE NOCASE ASC,
            role_title COLLATE NOCASE ASC
    """

    internship_rows = connection.execute(
        query,
        parameters
    ).fetchall()

    location_rows = connection.execute(
        """
        SELECT DISTINCT location
        FROM internships
        WHERE status = 'Active'
        ORDER BY location COLLATE NOCASE
        """
    ).fetchall()

    work_mode_rows = connection.execute(
        """
        SELECT DISTINCT work_mode
        FROM internships
        WHERE status = 'Active'
        ORDER BY work_mode COLLATE NOCASE
        """
    ).fetchall()

    connection.close()

    combined_skills = []
    seen_skills = set()

    for row in saved_skill_rows:
        skill = row["skill_name"].strip()
        skill_key = skill.casefold()

        if skill and skill_key not in seen_skills:
            seen_skills.add(skill_key)
            combined_skills.append(skill)

    if resume and resume["detected_skills"]:
        for skill in resume["detected_skills"].split(","):
            cleaned_skill = skill.strip()
            skill_key = cleaned_skill.casefold()

            if cleaned_skill and skill_key not in seen_skills:
                seen_skills.add(skill_key)
                combined_skills.append(cleaned_skill)

    internship_results = []

    for row in internship_rows:
        internship = dict(row)
        eligibility = evaluate_internship_eligibility(
            internship,
            profile
        )
        skill_result = build_internship_skill_result(
            internship,
            combined_skills
        )

        match_result = calculate_internship_match(
            internship,
            profile,
            combined_skills,
            eligibility
        )

        internship["eligibility"] = eligibility
        internship["eligible"] = eligibility["eligible"]
        internship["eligibility_status"] = eligibility["status"]
        internship["eligibility_reasons"] = eligibility["reasons"]
        internship["required_skills_list"] = skill_result["required_skills"]
        internship["matched_skills"] = skill_result["matched_skills"]
        internship["missing_skills"] = skill_result["missing_skills"]
        internship["match_score"] = match_result["score"]
        internship["skill_match_score"] = match_result["skill_score"]
        internship["match_explanation"] = match_result["explanation"]

        internship_results.append(internship)

    locations = [row["location"] for row in location_rows]
    work_modes = [row["work_mode"] for row in work_mode_rows]

    return render_template(
        "internships.html",
        student=student,
        profile=profile,
        internships=internship_results,
        locations=locations,
        work_modes=work_modes,
        search_query=search_query,
        location_filter=location_filter,
        work_mode_filter=work_mode_filter,
        combined_skills=combined_skills,
        search=search_query,
        location=location_filter,
        work_mode=work_mode_filter,
        student_skills=[row["skill_name"] for row in saved_skill_rows],
        resume_skills=resume_skills
    )


@app.route("/recommendations")
def recommendations():
    if "student_id" not in session:
        flash("Please log in to view your recommendations.", "error")
        return redirect(url_for("login"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT id, full_name, student_id, email
        FROM students
        WHERE id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    if student is None:
        connection.close()
        session.clear()
        flash("Your account could not be found. Please log in again.", "error")
        return redirect(url_for("login"))

    profile = connection.execute(
        """
        SELECT *
        FROM student_profiles
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    saved_skill_rows = connection.execute(
        """
        SELECT skill_name
        FROM student_skills
        WHERE student_id = ?
        ORDER BY skill_name COLLATE NOCASE
        """,
        (session["student_id"],)
    ).fetchall()

    resume = connection.execute(
        """
        SELECT detected_skills
        FROM student_resumes
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    internship_rows = connection.execute(
        """
        SELECT *
        FROM internships
        WHERE status = 'Active'
        ORDER BY application_deadline ASC, company_name COLLATE NOCASE ASC
        """
    ).fetchall()

    connection.close()

    saved_skills = [row["skill_name"] for row in saved_skill_rows]
    resume_skills = []

    if resume and resume["detected_skills"]:
        resume_skills = [
            skill.strip()
            for skill in resume["detected_skills"].split(",")
            if skill.strip()
        ]

    combined_skills = []
    seen_skills = set()

    for skill in saved_skills + resume_skills:
        cleaned_skill = skill.strip()
        skill_key = cleaned_skill.casefold()

        if cleaned_skill and skill_key not in seen_skills:
            seen_skills.add(skill_key)
            combined_skills.append(cleaned_skill)

    recommendation_ready = bool(profile and combined_skills)
    recommendation_results = []

    if recommendation_ready:
        for row in internship_rows:
            internship = dict(row)
            eligibility = evaluate_internship_eligibility(internship, profile)
            skill_result = build_internship_skill_result(internship, combined_skills)
            match_result = calculate_internship_match(
                internship,
                profile,
                combined_skills,
                eligibility
            )

            internship["eligible"] = eligibility["eligible"]
            internship["eligibility_status"] = eligibility["status"]
            internship["eligibility_reasons"] = eligibility["reasons"]
            internship["required_skills_list"] = skill_result["required_skills"]
            internship["matched_skills"] = skill_result["matched_skills"]
            internship["missing_skills"] = skill_result["missing_skills"]
            internship["match_score"] = match_result["score"]
            internship["skill_match_score"] = match_result["skill_score"]
            internship["match_explanation"] = match_result["explanation"]

            recommendation_results.append(internship)

        recommendation_results.sort(
            key=lambda item: (
                item["eligible"],
                item["match_score"] if item["match_score"] is not None else -1
            ),
            reverse=True
        )

    eligible_count = sum(
        1 for internship in recommendation_results if internship["eligible"]
    )

    strong_match_count = sum(
        1
        for internship in recommendation_results
        if internship["match_score"] is not None
        and internship["match_score"] >= 70
    )

    top_match_score = (
        recommendation_results[0]["match_score"]
        if recommendation_results
        else None
    )

    return render_template(
        "recommendations.html",
        student=student,
        profile=profile,
        recommendations=recommendation_results,
        recommendation_ready=recommendation_ready,
        student_skills=saved_skills,
        resume_skills=resume_skills,
        combined_skills=combined_skills,
        eligible_count=eligible_count,
        strong_match_count=strong_match_count,
        top_match_score=top_match_score
    )


@app.route("/skill-gap")
def skill_gap():
    if "student_id" not in session:
        flash("Please log in to view your skill gap analysis.", "error")
        return redirect(url_for("login"))

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT id, full_name, student_id, email
        FROM students
        WHERE id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    if student is None:
        connection.close()
        session.clear()
        flash("Your account could not be found. Please log in again.", "error")
        return redirect(url_for("login"))

    profile = connection.execute(
        """
        SELECT *
        FROM student_profiles
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    saved_skill_rows = connection.execute(
        """
        SELECT skill_name
        FROM student_skills
        WHERE student_id = ?
        ORDER BY skill_name COLLATE NOCASE
        """,
        (session["student_id"],)
    ).fetchall()

    resume = connection.execute(
        """
        SELECT detected_skills
        FROM student_resumes
        WHERE student_id = ?
        """,
        (session["student_id"],)
    ).fetchone()

    internship_rows = connection.execute(
        """
        SELECT *
        FROM internships
        WHERE status = 'Active'
        ORDER BY application_deadline ASC, company_name COLLATE NOCASE ASC
        """
    ).fetchall()

    connection.close()

    saved_skills = [row["skill_name"] for row in saved_skill_rows]
    resume_skills = []

    if resume and resume["detected_skills"]:
        resume_skills = [
            skill.strip()
            for skill in resume["detected_skills"].split(",")
            if skill.strip()
        ]

    combined_skills = []
    seen_skills = set()

    for skill in saved_skills + resume_skills:
        cleaned_skill = skill.strip()
        skill_key = cleaned_skill.casefold()

        if cleaned_skill and skill_key not in seen_skills:
            seen_skills.add(skill_key)
            combined_skills.append(cleaned_skill)

    analysis_ready = bool(profile and combined_skills)
    internship_gaps = []
    skill_frequency = {}

    if analysis_ready:
        for row in internship_rows:
            internship = dict(row)
            eligibility = evaluate_internship_eligibility(internship, profile)
            skill_result = build_internship_skill_result(internship, combined_skills)
            match_result = calculate_internship_match(
                internship,
                profile,
                combined_skills,
                eligibility
            )

            internship["eligible"] = eligibility["eligible"]
            internship["matched_skills"] = skill_result["matched_skills"]
            internship["missing_skills"] = skill_result["missing_skills"]
            internship["required_skills_list"] = skill_result["required_skills"]
            internship["match_score"] = match_result["score"]
            internship["skill_match_score"] = match_result["skill_score"]

            if eligibility["eligible"]:
                for missing_skill in skill_result["missing_skills"]:
                    key = missing_skill.casefold()

                    if key not in skill_frequency:
                        skill_frequency[key] = {
                            "skill": missing_skill,
                            "count": 0
                        }

                    skill_frequency[key]["count"] += 1

            internship_gaps.append(internship)

        internship_gaps.sort(
            key=lambda item: (
                item["eligible"],
                item["match_score"] if item["match_score"] is not None else -1
            ),
            reverse=True
        )

    priority_skills = sorted(
        skill_frequency.values(),
        key=lambda item: (-item["count"], item["skill"].casefold())
    )

    eligible_internships = [
        internship
        for internship in internship_gaps
        if internship["eligible"]
    ]

    total_missing_skills = len(priority_skills)
    top_priority_skill = priority_skills[0]["skill"] if priority_skills else None
    best_target = eligible_internships[0] if eligible_internships else None

    return render_template(
        "skill_gap.html",
        student=student,
        profile=profile,
        analysis_ready=analysis_ready,
        student_skills=saved_skills,
        resume_skills=resume_skills,
        combined_skills=combined_skills,
        internship_gaps=internship_gaps,
        eligible_internships=eligible_internships,
        priority_skills=priority_skills,
        total_missing_skills=total_missing_skills,
        top_priority_skill=top_priority_skill,
        best_target=best_target
    )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if "admin_id" in session:
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email:
            flash("Please enter your admin email address.", "error")
            return render_template(
                "admin_login.html",
                email=email
            )

        if not password:
            flash("Please enter your password.", "error")
            return render_template(
                "admin_login.html",
                email=email
            )

        connection = get_db_connection()

        admin = connection.execute(
            """
            SELECT *
            FROM admins
            WHERE email = ?
            """,
            (email,)
        ).fetchone()

        connection.close()

        if admin is None:
            flash(
                "No administrator account was found with that email address.",
                "error"
            )

            return render_template(
                "admin_login.html",
                email=email
            )

        if admin["status"] != "Active":
            flash(
                "This administrator account is currently inactive.",
                "error"
            )

            return render_template(
                "admin_login.html",
                email=email
            )

        if not check_password_hash(
            admin["password_hash"],
            password
        ):
            flash(
                "Incorrect password. Please try again.",
                "error"
            )

            return render_template(
                "admin_login.html",
                email=email
            )

        session.clear()
        session["admin_id"] = admin["id"]
        session["admin_name"] = admin["full_name"]
        session["admin_email"] = admin["email"]

        return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")


@app.route("/admin")
@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin_id" not in session:
        flash(
            "Please sign in to access the admin portal.",
            "error"
        )

        return redirect(url_for("admin_login"))

    connection = get_db_connection()

    admin = connection.execute(
        """
        SELECT id, full_name, email, status, created_at
        FROM admins
        WHERE id = ?
        """,
        (session["admin_id"],)
    ).fetchone()

    if admin is None or admin["status"] != "Active":
        connection.close()
        session.clear()

        flash(
            "Your administrator session is no longer valid.",
            "error"
        )

        return redirect(url_for("admin_login"))

    total_internships = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM internships
        """
    ).fetchone()["count"]

    active_internships = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM internships
        WHERE status = 'Active'
        """
    ).fetchone()["count"]

    inactive_internships = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM internships
        WHERE status != 'Active'
        """
    ).fetchone()["count"]

    total_students = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM students
        """
    ).fetchone()["count"]

    completed_profiles = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM student_profiles
        """
    ).fetchone()["count"]

    recent_internships = connection.execute(
        """
        SELECT
            id,
            company_name,
            role_title,
            location,
            work_mode,
            status,
            created_at
        FROM internships
        ORDER BY created_at DESC, id DESC
        LIMIT 5
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin_dashboard.html",
        admin=admin,
        total_internships=total_internships,
        active_internships=active_internships,
        inactive_internships=inactive_internships,
        total_students=total_students,
        completed_profiles=completed_profiles,
        recent_internships=recent_internships
    )


@app.route("/admin/internships")
def admin_internships():
    if "admin_id" not in session:
        flash("Please sign in to manage internships.", "error")
        return redirect(url_for("admin_login"))
    connection = get_db_connection()
    admin = connection.execute("SELECT id, full_name, email, status FROM admins WHERE id = ?", (session["admin_id"],)).fetchone()
    if admin is None or admin["status"] != "Active":
        connection.close()
        session.clear()
        flash("Your administrator session is no longer valid.", "error")
        return redirect(url_for("admin_login"))
    internship_rows = connection.execute("SELECT * FROM internships ORDER BY created_at DESC, id DESC").fetchall()
    connection.close()
    internships = [dict(row) for row in internship_rows]
    total_internships = len(internships)
    active_internships = sum(1 for internship in internships if internship["status"] == "Active")
    inactive_internships = total_internships - active_internships
    return render_template("admin_internships.html", admin=admin, internships=internships, total_internships=total_internships, active_internships=active_internships, inactive_internships=inactive_internships)


def get_admin_or_redirect():
    if "admin_id" not in session:
        return None
    connection = get_db_connection()
    admin = connection.execute("SELECT id, full_name, email, status FROM admins WHERE id = ?", (session["admin_id"],)).fetchone()
    connection.close()
    if admin is None or admin["status"] != "Active":
        session.clear()
        return None
    return admin


def get_internship_form_data():
    return {
        "company_name": request.form.get("company_name", "").strip(),
        "role_title": request.form.get("role_title", "").strip(),
        "location": request.form.get("location", "").strip(),
        "work_mode": request.form.get("work_mode", "").strip(),
        "duration": request.form.get("duration", "").strip(),
        "stipend": request.form.get("stipend", "").strip(),
        "description": request.form.get("description", "").strip(),
        "required_skills": request.form.get("required_skills", "").strip(),
        "eligible_courses": request.form.get("eligible_courses", "").strip(),
        "eligible_branches": request.form.get("eligible_branches", "").strip(),
        "eligible_years": request.form.get("eligible_years", "").strip(),
        "minimum_score": request.form.get("minimum_score", "").strip(),
        "score_type": request.form.get("score_type", "").strip(),
        "openings": request.form.get("openings", "").strip(),
        "application_deadline": request.form.get("application_deadline", "").strip(),
        "application_link": request.form.get("application_link", "").strip(),
        "status": request.form.get("status", "Active").strip()
    }


def validate_internship_form(data):
    errors = []
    for key, message in [
        ("company_name", "Please enter the company name."),
        ("role_title", "Please enter the internship role."),
        ("location", "Please enter the internship location."),
        ("work_mode", "Please select the work mode."),
        ("duration", "Please enter the internship duration."),
        ("description", "Please enter the internship description."),
        ("required_skills", "Please enter at least one required skill.")
    ]:
        if not data[key]:
            errors.append(message)
    minimum_score = None
    if data["minimum_score"]:
        try:
            minimum_score = float(data["minimum_score"])
            if minimum_score < 0:
                errors.append("Minimum academic score cannot be negative.")
            if data["score_type"] == "Percentage" and minimum_score > 100:
                errors.append("Percentage requirement cannot exceed 100.")
            if data["score_type"] == "CGPA" and minimum_score > 10:
                errors.append("CGPA requirement cannot exceed 10.")
        except ValueError:
            errors.append("Please enter a valid minimum academic score.")
    try:
        openings = int(data["openings"] or 1)
        if openings < 1:
            errors.append("Number of openings must be at least 1.")
    except ValueError:
        openings = 1
        errors.append("Please enter a valid number of openings.")
    if data["status"] not in ["Active", "Inactive"]:
        data["status"] = "Active"
    return errors, minimum_score, openings


@app.route("/admin/internships/add", methods=["GET", "POST"])
def admin_add_internship():
    admin = get_admin_or_redirect()
    if admin is None:
        flash("Please sign in to manage internships.", "error")
        return redirect(url_for("admin_login"))
    if request.method == "POST":
        data = get_internship_form_data()
        errors, minimum_score, openings = validate_internship_form(data)
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("admin_internship_form.html", admin=admin, internship=data, form_mode="add")
        connection = get_db_connection()
        try:
            connection.execute("""
                INSERT INTO internships (
                    company_name, role_title, location, work_mode, duration, stipend,
                    description, required_skills, eligible_courses, eligible_branches,
                    eligible_years, minimum_score, score_type, openings,
                    application_deadline, application_link, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["company_name"], data["role_title"], data["location"], data["work_mode"],
                data["duration"], data["stipend"], data["description"], data["required_skills"],
                data["eligible_courses"], data["eligible_branches"], data["eligible_years"],
                minimum_score, data["score_type"], openings, data["application_deadline"],
                data["application_link"], data["status"]
            ))
            connection.commit()
        except sqlite3.Error:
            connection.rollback()
            connection.close()
            flash("The internship could not be added. Please try again.", "error")
            return render_template("admin_internship_form.html", admin=admin, internship=data, form_mode="add")
        connection.close()
        flash("Internship added successfully.", "success")
        return redirect(url_for("admin_internships"))
    return render_template("admin_internship_form.html", admin=admin, internship=None, form_mode="add")


@app.route("/admin/internships/<int:internship_id>/edit", methods=["GET", "POST"])
def admin_edit_internship(internship_id):
    admin = get_admin_or_redirect()
    if admin is None:
        flash("Please sign in to manage internships.", "error")
        return redirect(url_for("admin_login"))
    connection = get_db_connection()
    internship = connection.execute("SELECT * FROM internships WHERE id = ?", (internship_id,)).fetchone()
    if internship is None:
        connection.close()
        flash("The selected internship could not be found.", "error")
        return redirect(url_for("admin_internships"))
    if request.method == "POST":
        data = get_internship_form_data()
        data["id"] = internship_id
        errors, minimum_score, openings = validate_internship_form(data)
        if errors:
            connection.close()
            for error in errors:
                flash(error, "error")
            return render_template("admin_internship_form.html", admin=admin, internship=data, form_mode="edit")
        try:
            connection.execute("""
                UPDATE internships SET
                    company_name = ?, role_title = ?, location = ?, work_mode = ?, duration = ?,
                    stipend = ?, description = ?, required_skills = ?, eligible_courses = ?,
                    eligible_branches = ?, eligible_years = ?, minimum_score = ?, score_type = ?,
                    openings = ?, application_deadline = ?, application_link = ?, status = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                data["company_name"], data["role_title"], data["location"], data["work_mode"],
                data["duration"], data["stipend"], data["description"], data["required_skills"],
                data["eligible_courses"], data["eligible_branches"], data["eligible_years"],
                minimum_score, data["score_type"], openings, data["application_deadline"],
                data["application_link"], data["status"], internship_id
            ))
            connection.commit()
        except sqlite3.Error:
            connection.rollback()
            connection.close()
            flash("The internship could not be updated. Please try again.", "error")
            return render_template("admin_internship_form.html", admin=admin, internship=data, form_mode="edit")
        connection.close()
        flash("Internship updated successfully.", "success")
        return redirect(url_for("admin_internships"))
    connection.close()
    return render_template("admin_internship_form.html", admin=admin, internship=internship, form_mode="edit")


@app.route("/admin/internships/<int:internship_id>/toggle", methods=["POST"])
def admin_toggle_internship(internship_id):
    admin = get_admin_or_redirect()
    if admin is None:
        flash("Please sign in to manage internships.", "error")
        return redirect(url_for("admin_login"))
    connection = get_db_connection()
    internship = connection.execute("SELECT id, status FROM internships WHERE id = ?", (internship_id,)).fetchone()
    if internship is None:
        connection.close()
        flash("The selected internship could not be found.", "error")
        return redirect(url_for("admin_internships"))
    new_status = "Inactive" if internship["status"] == "Active" else "Active"
    connection.execute("UPDATE internships SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, internship_id))
    connection.commit()
    connection.close()
    flash(f"Internship changed to {new_status}.", "success")
    return redirect(url_for("admin_internships"))


@app.route("/admin/internships/<int:internship_id>/delete", methods=["POST"])
def admin_delete_internship(internship_id):
    admin = get_admin_or_redirect()
    if admin is None:
        flash("Please sign in to manage internships.", "error")
        return redirect(url_for("admin_login"))
    connection = get_db_connection()
    internship = connection.execute("SELECT id FROM internships WHERE id = ?", (internship_id,)).fetchone()
    if internship is None:
        connection.close()
        flash("The selected internship could not be found.", "error")
        return redirect(url_for("admin_internships"))
    try:
        connection.execute("DELETE FROM internships WHERE id = ?", (internship_id,))
        connection.commit()
    except sqlite3.Error:
        connection.rollback()
        connection.close()
        flash("The internship could not be deleted.", "error")
        return redirect(url_for("admin_internships"))
    connection.close()
    flash("Internship deleted successfully.", "success")
    return redirect(url_for("admin_internships"))


@app.route("/admin/students")
def admin_students():
    admin = get_admin_or_redirect()
    if admin is None:
        flash("Please sign in to view students.", "error")
        return redirect(url_for("admin_login"))
    connection = get_db_connection()
    rows = connection.execute("""
        SELECT s.id, s.full_name, s.student_id, s.email, s.created_at,
               p.course, p.branch, p.current_year, p.college, p.graduation_year,
               p.academic_score, p.score_type,
               (SELECT COUNT(*) FROM student_skills ss WHERE ss.student_id = s.id) AS skill_count,
               CASE WHEN p.id IS NULL THEN 0 ELSE 1 END AS profile_complete,
               CASE WHEN r.id IS NULL THEN 0 ELSE 1 END AS resume_uploaded
        FROM students s
        LEFT JOIN student_profiles p ON p.student_id = s.id
        LEFT JOIN student_resumes r ON r.student_id = s.id
        ORDER BY s.created_at DESC, s.id DESC
    """).fetchall()
    connection.close()
    students = [dict(row) for row in rows]
    return render_template(
        "admin_students.html", admin=admin, students=students,
        total_students=len(students),
        completed_profiles=sum(1 for student in students if student["profile_complete"]),
        resume_students=sum(1 for student in students if student["resume_uploaded"])
    )


@app.route("/admin/reports")
def admin_reports():
    admin = get_admin_or_redirect()
    if admin is None:
        flash("Please sign in to view reports.", "error")
        return redirect(url_for("admin_login"))
    connection = get_db_connection()
    total_students = connection.execute("SELECT COUNT(*) AS count FROM students").fetchone()["count"]
    completed_profiles = connection.execute("SELECT COUNT(*) AS count FROM student_profiles").fetchone()["count"]
    resume_uploads = connection.execute("SELECT COUNT(*) AS count FROM student_resumes").fetchone()["count"]
    total_internships = connection.execute("SELECT COUNT(*) AS count FROM internships").fetchone()["count"]
    active_internships = connection.execute("SELECT COUNT(*) AS count FROM internships WHERE status = 'Active'").fetchone()["count"]
    inactive_internships = total_internships - active_internships
    mode_rows = connection.execute("SELECT work_mode, COUNT(*) AS count FROM internships GROUP BY work_mode").fetchall()
    company_rows = connection.execute("SELECT company_name, COUNT(*) AS internship_count FROM internships GROUP BY company_name ORDER BY internship_count DESC, company_name COLLATE NOCASE LIMIT 8").fetchall()
    skill_rows = connection.execute("SELECT required_skills FROM internships WHERE required_skills IS NOT NULL AND TRIM(required_skills) != ''").fetchall()
    connection.close()
    modes = {str(row["work_mode"] or "").casefold().replace("-", "").replace(" ", ""): row["count"] for row in mode_rows}
    remote_internships = modes.get("remote", 0)
    hybrid_internships = modes.get("hybrid", 0)
    onsite_internships = modes.get("onsite", 0)
    skill_frequency = {}
    for row in skill_rows:
        for skill in normalize_list_value(row["required_skills"]):
            key = skill.casefold()
            if key not in skill_frequency:
                skill_frequency[key] = {"skill": skill, "count": 0}
            skill_frequency[key]["count"] += 1
    popular_skills = sorted(skill_frequency.values(), key=lambda item: (-item["count"], item["skill"].casefold()))[:8]
    profile_completion_rate = round((completed_profiles / total_students) * 100) if total_students else 0
    resume_upload_rate = round((resume_uploads / total_students) * 100) if total_students else 0
    active_rate = round((active_internships / total_internships) * 100) if total_internships else 0
    return render_template(
        "admin_reports.html", admin=admin, total_students=total_students,
        completed_profiles=completed_profiles, resume_uploads=resume_uploads,
        total_internships=total_internships, active_internships=active_internships,
        inactive_internships=inactive_internships, remote_internships=remote_internships,
        hybrid_internships=hybrid_internships, onsite_internships=onsite_internships,
        top_companies=[dict(row) for row in company_rows], popular_skills=popular_skills,
        profile_completion_rate=profile_completion_rate, resume_upload_rate=resume_upload_rate,
        active_rate=active_rate
    )


@app.route("/admin/logout")
def admin_logout():
    session.clear()

    flash(
        "You have been logged out of the admin portal.",
        "success"
    )

    return redirect(url_for("admin_login"))


@app.route("/logout")
def logout():
    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)