document.addEventListener("DOMContentLoaded", function () {
    const passwordToggles = document.querySelectorAll(".password-toggle");

    passwordToggles.forEach(function (toggle) {
        toggle.addEventListener("click", function () {
            const targetId = toggle.dataset.target;
            const input = document.getElementById(targetId);

            if (!input) {
                return;
            }

            if (input.type === "password") {
                input.type = "text";
                toggle.textContent = "Hide";
            } else {
                input.type = "password";
                toggle.textContent = "Show";
            }

            input.focus();
        });
    });

    const capsFields = [
        {
            input: document.getElementById("login-password"),
            message: document.getElementById("login-password-caps")
        },
        {
            input: document.getElementById("register-password"),
            message: document.getElementById("register-password-caps")
        },
        {
            input: document.getElementById("confirm-password"),
            message: document.getElementById("confirm-password-caps")
        }
    ];

    capsFields.forEach(function (field) {
        if (!field.input || !field.message) {
            return;
        }

        function checkCapsLock(event) {
            const capsLockOn =
                typeof event.getModifierState === "function" &&
                event.getModifierState("CapsLock");

            field.message.classList.toggle("show", capsLockOn);
        }

        field.input.addEventListener("keydown", checkCapsLock);
        field.input.addEventListener("keyup", checkCapsLock);

        field.input.addEventListener("blur", function () {
            field.message.classList.remove("show");
        });
    });

    function showMessage(element, message, type) {
        if (!element) {
            return;
        }

        element.textContent = message;
        element.classList.remove("valid", "invalid");

        if (type) {
            element.classList.add(type);
        }
    }

    function setInputState(input, state) {
        if (!input) {
            return;
        }

        input.classList.remove("input-valid", "input-invalid");

        if (state === "valid") {
            input.classList.add("input-valid");
        }

        if (state === "invalid") {
            input.classList.add("input-invalid");
        }
    }

    function isValidGmail(value) {
        const gmailPattern =
            /^[A-Za-z0-9](?:[A-Za-z0-9.]{0,28}[A-Za-z0-9])?@gmail\.com$/i;

        if (!gmailPattern.test(value)) {
            return false;
        }

        const localPart = value.split("@")[0];

        if (localPart.includes("..")) {
            return false;
        }

        return true;
    }

    const fullName = document.getElementById("full-name");
    const nameMessage = document.getElementById("name-message");

    function validateName() {
        if (!fullName) {
            return true;
        }

        const value = fullName.value.trim();

        if (!value) {
            showMessage(
                nameMessage,
                "Full name is required.",
                "invalid"
            );

            setInputState(fullName, "invalid");
            return false;
        }

        if (!/^[A-Za-z][A-Za-z\s'-]{1,49}$/.test(value)) {
            showMessage(
                nameMessage,
                "Use letters, spaces, apostrophes or hyphens only.",
                "invalid"
            );

            setInputState(fullName, "invalid");
            return false;
        }

        showMessage(nameMessage, "", "");
        setInputState(fullName, "valid");

        return true;
    }

    if (fullName) {
        fullName.addEventListener("input", function () {
            fullName.value =
                fullName.value.replace(/[^A-Za-z\s'-]/g, "");

            if (fullName.value.trim()) {
                validateName();
            } else {
                showMessage(nameMessage, "", "");
                setInputState(fullName, "");
            }
        });

        fullName.addEventListener("blur", validateName);
    }

    const studentId = document.getElementById("student-id");
    const studentIdMessage =
        document.getElementById("student-id-message");

    function validateStudentId() {
        if (!studentId) {
            return true;
        }

        const value = studentId.value.trim();

        if (!value) {
            showMessage(
                studentIdMessage,
                "Student ID is required.",
                "invalid"
            );

            setInputState(studentId, "invalid");
            return false;
        }

        if (value.length < 3) {
            showMessage(
                studentIdMessage,
                "Student ID must contain at least 3 characters.",
                "invalid"
            );

            setInputState(studentId, "invalid");
            return false;
        }

        if (!/^[A-Za-z0-9]+$/.test(value)) {
            showMessage(
                studentIdMessage,
                "Only letters and numbers are allowed.",
                "invalid"
            );

            setInputState(studentId, "invalid");
            return false;
        }

        showMessage(studentIdMessage, "", "");
        setInputState(studentId, "valid");

        return true;
    }

    if (studentId) {
        studentId.addEventListener("input", function () {
            studentId.value = studentId.value
                .replace(/[^A-Za-z0-9]/g, "")
                .toUpperCase();

            if (studentId.value) {
                validateStudentId();
            } else {
                showMessage(studentIdMessage, "", "");
                setInputState(studentId, "");
            }
        });

        studentId.addEventListener(
            "blur",
            validateStudentId
        );
    }

    const email = document.getElementById("email");
    const emailMessage = document.getElementById("email-message");

    function validateEmail() {
        if (!email) {
            return true;
        }

        const value = email.value.trim().toLowerCase();

        if (!value) {
            showMessage(
                emailMessage,
                "Gmail address is required.",
                "invalid"
            );

            setInputState(email, "invalid");
            return false;
        }

        if (!isValidGmail(value)) {
            showMessage(
                emailMessage,
                "Enter a valid Gmail address ending in @gmail.com.",
                "invalid"
            );

            setInputState(email, "invalid");
            return false;
        }

        showMessage(
            emailMessage,
            "Valid Gmail format.",
            "valid"
        );

        setInputState(email, "valid");

        return true;
    }

    if (email) {
        email.addEventListener("input", function () {
            email.value = email.value
                .replace(/\s/g, "")
                .toLowerCase();

            if (email.value) {
                validateEmail();
            } else {
                showMessage(emailMessage, "", "");
                setInputState(email, "");
            }
        });

        email.addEventListener("blur", validateEmail);
    }

    const password =
        document.getElementById("register-password");

    const confirmPassword =
        document.getElementById("confirm-password");

    const passwordMessage =
        document.getElementById("password-message");

    const passwordMatchMessage =
        document.getElementById("password-match-message");

    const ruleLength =
        document.getElementById("rule-length");

    const ruleUppercase =
        document.getElementById("rule-uppercase");

    const ruleLowercase =
        document.getElementById("rule-lowercase");

    const ruleNumber =
        document.getElementById("rule-number");

    const ruleSpecial =
        document.getElementById("rule-special");

    function setRule(element, valid) {
        if (!element) {
            return;
        }

        element.classList.toggle("rule-valid", valid);
    }

    function validatePassword() {
        if (!password) {
            return true;
        }

        const value = password.value;

        const hasLength =
            value.length >= 8 && value.length <= 64;

        const hasUppercase = /[A-Z]/.test(value);
        const hasLowercase = /[a-z]/.test(value);
        const hasNumber = /\d/.test(value);
        const hasSpecial = /[^A-Za-z0-9\s]/.test(value);
        const hasNoSpaces = !/\s/.test(value);

        setRule(ruleLength, hasLength);
        setRule(ruleUppercase, hasUppercase);
        setRule(ruleLowercase, hasLowercase);
        setRule(ruleNumber, hasNumber);
        setRule(ruleSpecial, hasSpecial);

        if (!value) {
            showMessage(passwordMessage, "", "");
            setInputState(password, "");
            return false;
        }

        if (
            !hasLength ||
            !hasUppercase ||
            !hasLowercase ||
            !hasNumber ||
            !hasSpecial ||
            !hasNoSpaces
        ) {
            showMessage(
                passwordMessage,
                hasNoSpaces
                    ? "Complete all password requirements."
                    : "Password cannot contain spaces.",
                "invalid"
            );

            setInputState(password, "invalid");
            return false;
        }

        showMessage(
            passwordMessage,
            "Strong password.",
            "valid"
        );

        setInputState(password, "valid");

        return true;
    }

    function validateConfirmPassword() {
        if (!confirmPassword || !password) {
            return true;
        }

        if (!confirmPassword.value) {
            showMessage(passwordMatchMessage, "", "");
            setInputState(confirmPassword, "");
            return false;
        }

        if (password.value !== confirmPassword.value) {
            showMessage(
                passwordMatchMessage,
                "Passwords do not match.",
                "invalid"
            );

            setInputState(confirmPassword, "invalid");
            return false;
        }

        showMessage(
            passwordMatchMessage,
            "Passwords match.",
            "valid"
        );

        setInputState(confirmPassword, "valid");

        return true;
    }

    if (password) {
        password.addEventListener("input", function () {
            validatePassword();

            if (
                confirmPassword &&
                confirmPassword.value
            ) {
                validateConfirmPassword();
            }
        });

        password.addEventListener(
            "blur",
            validatePassword
        );
    }

    if (confirmPassword) {
        confirmPassword.addEventListener(
            "input",
            validateConfirmPassword
        );

        confirmPassword.addEventListener(
            "blur",
            validateConfirmPassword
        );
    }

    const terms = document.getElementById("terms");
    const termsMessage =
        document.getElementById("terms-message");

    function validateTerms() {
        if (!terms) {
            return true;
        }

        if (!terms.checked) {
            showMessage(
                termsMessage,
                "Please accept the Terms of Use and Privacy Policy.",
                "invalid"
            );

            return false;
        }

        showMessage(termsMessage, "", "");

        return true;
    }

    if (terms) {
        terms.addEventListener(
            "change",
            validateTerms
        );
    }

    const registerForm =
        document.getElementById("register-form");

    if (registerForm) {
        registerForm.addEventListener(
            "submit",
            function (event) {
                const nameValid = validateName();
                const studentIdValid = validateStudentId();
                const emailValid = validateEmail();
                const passwordValid = validatePassword();
                const confirmValid =
                    validateConfirmPassword();
                const termsValid = validateTerms();

                if (
                    !nameValid ||
                    !studentIdValid ||
                    !emailValid ||
                    !passwordValid ||
                    !confirmValid ||
                    !termsValid
                ) {
                    event.preventDefault();

                    const firstInvalid =
                        registerForm.querySelector(
                            ".input-invalid"
                        );

                    if (firstInvalid) {
                        firstInvalid.focus();
                    }
                }
            }
        );
    }

    const loginForm =
        document.getElementById("login-form");

    const identifier =
        document.getElementById("identifier");

    const identifierMessage =
        document.getElementById("identifier-message");

    const loginPassword =
        document.getElementById("login-password");

    const loginPasswordMessage =
        document.getElementById(
            "login-password-message"
        );

    function validateIdentifier() {
        if (!identifier) {
            return true;
        }

        const value = identifier.value.trim();

        if (!value) {
            showMessage(
                identifierMessage,
                "Student ID or Gmail address is required.",
                "invalid"
            );

            setInputState(identifier, "invalid");
            return false;
        }

        if (value.includes("@")) {
            if (!isValidGmail(value)) {
                showMessage(
                    identifierMessage,
                    "Enter a valid Gmail address ending in @gmail.com.",
                    "invalid"
                );

                setInputState(identifier, "invalid");
                return false;
            }
        } else if (!/^[A-Za-z0-9]+$/.test(value)) {
            showMessage(
                identifierMessage,
                "Student ID can contain only letters and numbers.",
                "invalid"
            );

            setInputState(identifier, "invalid");
            return false;
        }

        showMessage(identifierMessage, "", "");
        setInputState(identifier, "valid");

        return true;
    }

    function validateLoginPassword() {
        if (!loginPassword) {
            return true;
        }

        if (!loginPassword.value) {
            showMessage(
                loginPasswordMessage,
                "Password is required.",
                "invalid"
            );

            setInputState(loginPassword, "invalid");
            return false;
        }

        showMessage(loginPasswordMessage, "", "");
        setInputState(loginPassword, "valid");

        return true;
    }

    if (identifier) {
        identifier.addEventListener(
            "input",
            function () {
                identifier.value =
                    identifier.value.replace(/\s/g, "");

                if (identifier.value) {
                    validateIdentifier();
                } else {
                    showMessage(
                        identifierMessage,
                        "",
                        ""
                    );

                    setInputState(identifier, "");
                }
            }
        );

        identifier.addEventListener(
            "blur",
            validateIdentifier
        );
    }

    if (loginPassword) {
        loginPassword.addEventListener(
            "blur",
            validateLoginPassword
        );
    }

    if (loginForm) {
        loginForm.addEventListener(
            "submit",
            function (event) {
                const identifierValid =
                    validateIdentifier();

                const passwordValid =
                    validateLoginPassword();

                if (
                    !identifierValid ||
                    !passwordValid
                ) {
                    event.preventDefault();

                    const firstInvalid =
                        loginForm.querySelector(
                            ".input-invalid"
                        );

                    if (firstInvalid) {
                        firstInvalid.focus();
                    }
                }
            }
        );
    }
});