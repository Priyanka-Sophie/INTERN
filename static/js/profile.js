document.addEventListener("DOMContentLoaded", function () {
    const branches = [
        "Computer Science",
        "Computer Science and Engineering",
        "Information Technology",
        "Artificial Intelligence",
        "Artificial Intelligence and Machine Learning",
        "Data Science",
        "Cyber Security",
        "Computer Applications",
        "Software Engineering",
        "Electronics and Communication Engineering",
        "Electrical and Electronics Engineering",
        "Electronics and Computer Science",
        "Information Science and Engineering",
        "Mathematics and Computer Science",
        "Statistics and Computer Science",
        "Cloud Computing",
        "Internet of Things",
        "Robotics and Automation",
        "Mechanical Engineering",
        "Civil Engineering",
        "Other"
    ];

    const colleges = [
        {
            name: "Indian Institute of Science",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "CHRIST (Deemed to be University)",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Bangalore University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Bengaluru City University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Bengaluru North University",
            location: "Karnataka"
        },
        {
            name: "Jain (Deemed-to-be University)",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "PES University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "RV University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "REVA University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Dayananda Sagar University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "CMR University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Presidency University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Alliance University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Azim Premji University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "St. Joseph's University",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Mount Carmel College, Autonomous",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Kristu Jayanti College, Autonomous",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Jyoti Nivas College Autonomous",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "M.S. Ramaiah University of Applied Sciences",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "University Visvesvaraya College of Engineering",
            location: "Bengaluru, Karnataka"
        },
        {
            name: "Visvesvaraya Technological University",
            location: "Belagavi, Karnataka"
        },
        {
            name: "University of Mysore",
            location: "Mysuru, Karnataka"
        },
        {
            name: "Manipal Academy of Higher Education",
            location: "Manipal, Karnataka"
        },
        {
            name: "National Institute of Technology Karnataka",
            location: "Surathkal, Karnataka"
        },
        {
            name: "University of Delhi",
            location: "Delhi"
        },
        {
            name: "Jawaharlal Nehru University",
            location: "New Delhi"
        },
        {
            name: "Jamia Millia Islamia",
            location: "New Delhi"
        },
        {
            name: "University of Mumbai",
            location: "Mumbai, Maharashtra"
        },
        {
            name: "Savitribai Phule Pune University",
            location: "Pune, Maharashtra"
        },
        {
            name: "University of Calcutta",
            location: "Kolkata, West Bengal"
        },
        {
            name: "University of Madras",
            location: "Chennai, Tamil Nadu"
        },
        {
            name: "Anna University",
            location: "Chennai, Tamil Nadu"
        },
        {
            name: "Vellore Institute of Technology",
            location: "Vellore, Tamil Nadu"
        },
        {
            name: "SRM Institute of Science and Technology",
            location: "Chennai, Tamil Nadu"
        },
        {
            name: "Amrita Vishwa Vidyapeetham",
            location: "Coimbatore, Tamil Nadu"
        },
        {
            name: "University of Hyderabad",
            location: "Hyderabad, Telangana"
        },
        {
            name: "Osmania University",
            location: "Hyderabad, Telangana"
        },
        {
            name: "BITS Pilani",
            location: "Pilani, Rajasthan"
        },
        {
            name: "Chandigarh University",
            location: "Mohali, Punjab"
        },
        {
            name: "Lovely Professional University",
            location: "Phagwara, Punjab"
        },
        {
            name: "Amity University",
            location: "Noida, Uttar Pradesh"
        }
    ];

    const branchInput = document.getElementById("branch");
    const branchSuggestions = document.getElementById("branch-suggestions");

    const collegeInput = document.getElementById("college");
    const collegeSuggestions = document.getElementById("college-suggestions");

    const interestInput = document.getElementById("interests");
    const interestButtons = document.querySelectorAll(".interest-chip");
    const selectedInterestsText = document.getElementById("selected-interests");

    const careerInput = document.getElementById("career_goal");
    const careerButtons = document.querySelectorAll(".career-card");

    const scoreType = document.getElementById("score_type");
    const academicScore = document.getElementById("academic_score");
    const scoreHelp = document.getElementById("score-help");
    const scoreSuffix = document.getElementById("score-suffix");

    const form = document.getElementById("profile-form");

    function hideSuggestions(container) {
        container.classList.remove("show");
        container.innerHTML = "";
    }

    function showBranchSuggestions() {
        const query = branchInput.value.trim().toLowerCase();

        const matches = branches
            .filter(function (branch) {
                return branch.toLowerCase().includes(query);
            })
            .slice(0, 8);

        branchSuggestions.innerHTML = "";

        if (matches.length === 0) {
            hideSuggestions(branchSuggestions);
            return;
        }

        matches.forEach(function (branch) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "suggestion-item";

            const icon = document.createElement("span");
            icon.className = "suggestion-icon";
            icon.textContent = "◫";

            const content = document.createElement("span");

            const title = document.createElement("strong");
            title.textContent = branch;

            const subtitle = document.createElement("small");
            subtitle.textContent = "Branch / Specialization";

            content.appendChild(title);
            content.appendChild(subtitle);

            button.appendChild(icon);
            button.appendChild(content);

            button.addEventListener("click", function () {
                branchInput.value = branch;
                hideSuggestions(branchSuggestions);
            });

            branchSuggestions.appendChild(button);
        });

        branchSuggestions.classList.add("show");
    }

    function showCollegeSuggestions() {
        const query = collegeInput.value.trim().toLowerCase();

        if (query.length < 1) {
            hideSuggestions(collegeSuggestions);
            return;
        }

        const matches = colleges
            .filter(function (college) {
                return (
                    college.name.toLowerCase().includes(query) ||
                    college.location.toLowerCase().includes(query)
                );
            })
            .slice(0, 8);

        collegeSuggestions.innerHTML = "";

        if (matches.length === 0) {
            hideSuggestions(collegeSuggestions);
            return;
        }

        matches.forEach(function (college) {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "suggestion-item";

            const icon = document.createElement("span");
            icon.className = "suggestion-icon";
            icon.textContent = "U";

            const content = document.createElement("span");

            const title = document.createElement("strong");
            title.textContent = college.name;

            const subtitle = document.createElement("small");
            subtitle.textContent = college.location;

            content.appendChild(title);
            content.appendChild(subtitle);

            button.appendChild(icon);
            button.appendChild(content);

            button.addEventListener("click", function () {
                collegeInput.value = college.name;
                hideSuggestions(collegeSuggestions);
            });

            collegeSuggestions.appendChild(button);
        });

        collegeSuggestions.classList.add("show");
    }

    branchInput.addEventListener("focus", showBranchSuggestions);
    branchInput.addEventListener("input", showBranchSuggestions);

    collegeInput.addEventListener("input", showCollegeSuggestions);

    document.addEventListener("click", function (event) {
        if (!branchInput.contains(event.target) &&
            !branchSuggestions.contains(event.target)) {
            hideSuggestions(branchSuggestions);
        }

        if (!collegeInput.contains(event.target) &&
            !collegeSuggestions.contains(event.target)) {
            hideSuggestions(collegeSuggestions);
        }
    });

    let selectedInterests = [];

    if (interestInput.value.trim() !== "") {
        selectedInterests = interestInput.value
            .split(",")
            .map(function (item) {
                return item.trim();
            })
            .filter(function (item) {
                return item !== "";
            });
    }

    function updateInterestDisplay() {
        interestButtons.forEach(function (button) {
            const value = button.dataset.value;

            if (selectedInterests.includes(value)) {
                button.classList.add("selected");
            } else {
                button.classList.remove("selected");
            }
        });

        interestInput.value = selectedInterests.join(", ");

        if (selectedInterests.length === 0) {
            selectedInterestsText.textContent =
                "Choose at least one interest above.";
        } else {
            selectedInterestsText.textContent =
                selectedInterests.join(" · ");
        }
    }

    interestButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const value = button.dataset.value;

            if (selectedInterests.includes(value)) {
                selectedInterests = selectedInterests.filter(
                    function (item) {
                        return item !== value;
                    }
                );
            } else {
                selectedInterests.push(value);
            }

            updateInterestDisplay();
        });
    });

    updateInterestDisplay();

    function updateCareerDisplay() {
        const currentCareer = careerInput.value.trim();

        careerButtons.forEach(function (button) {
            if (button.dataset.value === currentCareer) {
                button.classList.add("selected");
            } else {
                button.classList.remove("selected");
            }
        });
    }

    careerButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            careerInput.value = button.dataset.value;
            updateCareerDisplay();
        });
    });

    updateCareerDisplay();

    function updateScoreField() {
        if (scoreType.value === "CGPA") {
            academicScore.max = "10";
            academicScore.min = "0";
            academicScore.step = "0.01";
            academicScore.placeholder = "e.g. 8.5";
            scoreSuffix.textContent = "/ 10";
            scoreHelp.textContent = "Enter your CGPA between 0 and 10.";
        } else if (scoreType.value === "Percentage") {
            academicScore.max = "100";
            academicScore.min = "0";
            academicScore.step = "0.01";
            academicScore.placeholder = "e.g. 82.5";
            scoreSuffix.textContent = "%";
            scoreHelp.textContent = "Enter your percentage between 0 and 100.";
        } else {
            academicScore.max = "100";
            academicScore.placeholder = "Select score type first";
            scoreSuffix.textContent = "";
            scoreHelp.textContent =
                "Select CGPA or Percentage first.";
        }
    }

    scoreType.addEventListener("change", function () {
        academicScore.value = "";
        updateScoreField();
    });

    updateScoreField();

    form.addEventListener("submit", function (event) {
        if (selectedInterests.length === 0) {
            event.preventDefault();
            alert("Please select at least one area of interest.");
            document.getElementById("interest-options").scrollIntoView({
                behavior: "smooth",
                block: "center"
            });
            return;
        }

        if (careerInput.value.trim() === "") {
            event.preventDefault();
            alert("Please select your career goal.");
            document.getElementById("career-options").scrollIntoView({
                behavior: "smooth",
                block: "center"
            });
        }
    });
});