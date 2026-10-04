document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("skills-form");
    const hiddenInput = document.getElementById("skills-input");
    const selectedContainer = document.getElementById("selected-skills");
    const selectedCount = document.getElementById("selected-count");
    const customInput = document.getElementById("custom-skill");
    const addCustomButton = document.getElementById("add-custom-skill");
    const customMessage = document.getElementById("custom-message");
    const skillChips = document.querySelectorAll(".skill-chip");

    let selectedSkills = [];

    if (hiddenInput.value.trim() !== "") {
        selectedSkills = hiddenInput.value
            .split(",")
            .map(function (skill) {
                return skill.trim();
            })
            .filter(function (skill) {
                return skill !== "";
            });
    }

    function skillExists(skill) {
        return selectedSkills.some(function (existingSkill) {
            return existingSkill.toLowerCase() === skill.toLowerCase();
        });
    }

    function updateHiddenInput() {
        hiddenInput.value = selectedSkills.join(",");
    }

    function updateChipStates() {
        skillChips.forEach(function (chip) {
            const skill = chip.dataset.skill;

            if (skillExists(skill)) {
                chip.classList.add("selected");
                chip.setAttribute("aria-pressed", "true");
            } else {
                chip.classList.remove("selected");
                chip.setAttribute("aria-pressed", "false");
            }
        });
    }

    function renderSelectedSkills() {
        selectedContainer.innerHTML = "";

        if (selectedSkills.length === 0) {
            const empty = document.createElement("div");

            empty.className = "empty-selection";
            empty.textContent =
                "No skills selected yet. Choose skills below.";

            selectedContainer.appendChild(empty);
        } else {
            selectedSkills.forEach(function (skill) {
                const button = document.createElement("button");

                button.type = "button";
                button.className = "selected-skill";
                button.dataset.skill = skill;
                button.setAttribute(
                    "aria-label",
                    "Remove " + skill
                );

                const name = document.createElement("strong");
                name.textContent = skill;

                const remove = document.createElement("span");
                remove.textContent = "×";

                button.appendChild(name);
                button.appendChild(remove);

                button.addEventListener("click", function () {
                    removeSkill(skill);
                });

                selectedContainer.appendChild(button);
            });
        }

        selectedCount.textContent = selectedSkills.length;

        updateHiddenInput();
        updateChipStates();
    }

    function addSkill(skill) {
        const cleanedSkill = skill
            .trim()
            .replace(/\s+/g, " ");

        if (cleanedSkill === "") {
            customMessage.textContent =
                "Enter a skill before adding it.";
            return;
        }

        if (cleanedSkill.length > 40) {
            customMessage.textContent =
                "Skill names cannot contain more than 40 characters.";
            return;
        }

        if (selectedSkills.length >= 30) {
            customMessage.textContent =
                "You can add up to 30 skills.";
            return;
        }

        if (skillExists(cleanedSkill)) {
            customMessage.textContent =
                "That skill is already selected.";
            return;
        }

        selectedSkills.push(cleanedSkill);

        customMessage.textContent = "";
        customInput.value = "";

        renderSelectedSkills();
    }

    function removeSkill(skill) {
        selectedSkills = selectedSkills.filter(function (existingSkill) {
            return existingSkill.toLowerCase() !== skill.toLowerCase();
        });

        customMessage.textContent = "";

        renderSelectedSkills();
    }

    skillChips.forEach(function (chip) {
        chip.setAttribute("aria-pressed", "false");

        chip.addEventListener("click", function () {
            const skill = chip.dataset.skill;

            if (skillExists(skill)) {
                removeSkill(skill);
            } else {
                addSkill(skill);
            }
        });
    });

    addCustomButton.addEventListener("click", function () {
        addSkill(customInput.value);
    });

    customInput.addEventListener("keydown", function (event) {
        if (event.key === "Enter") {
            event.preventDefault();
            addSkill(customInput.value);
        }
    });

    customInput.addEventListener("input", function () {
        customMessage.textContent = "";
    });

    form.addEventListener("submit", function (event) {
        if (selectedSkills.length === 0) {
            event.preventDefault();

            customMessage.textContent =
                "Please select or add at least one skill.";

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

            return;
        }

        updateHiddenInput();
    });

    renderSelectedSkills();
});