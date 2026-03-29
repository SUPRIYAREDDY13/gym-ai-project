document.addEventListener("DOMContentLoaded", function () {
    console.log("Gym AI System loaded successfully!");

    const forms = document.querySelectorAll("form");

    forms.forEach(function(form) {
        form.addEventListener("submit", function(event) {
            event.preventDefault();

            const pageName = window.location.pathname.split("/").pop();

            // ================= REGISTER =================
            if (pageName === "register.html") {
                const inputs = document.querySelectorAll("input");

                const name = inputs[0].value;
                const email = inputs[1].value;
                const phone = inputs[2].value;
                const role = document.querySelector("select").value;
                const password = inputs[3].value;
                const confirmPassword = inputs[4].value;

                if (password !== confirmPassword) {
                    alert("Passwords do not match!");
                    return;
                }

                fetch("http://127.0.0.1:5000/register", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        name,
                        email,
                        phone,
                        role,
                        password
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        alert("Registration successful!");
                        window.location.href = "login.html";
                    }
                })
                .catch(() => alert("Server error!"));
            }

            // ================= LOGIN =================
            else if (pageName === "login.html") {
                const email = document.querySelector('input[type="email"]').value;
                const password = document.querySelector('input[type="password"]').value;

                fetch("http://127.0.0.1:5000/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email,
                        password
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.message === "Login successful") {
                        localStorage.setItem("loggedInUser", email);

                        alert("Login successful!");

                        // ✅ FIXED ROLE CHECK (case matches backend)
                        if (data.role === "Admin") {
                            window.location.href = "admin_dashboard.html";
                        } else if (data.role === "Trainer") {
                            window.location.href = "trainer_dashboard.html";
                        } else {
                            window.location.href = "member_dashboard.html";
                        }

                    } else {
                        alert("Invalid login details!");
                    }
                })
                .catch(() => alert("Server error!"));
            }

            // ================= OTHER FORMS =================
            else {
                alert("Form submitted!");
            }
        });
    });

    // ================= WELCOME TEXT =================
    const welcomeText = document.getElementById("welcomeUser");
    if (welcomeText) {
        const user = localStorage.getItem("loggedInUser");
        if (user) {
            welcomeText.innerText = "Welcome, " + user;
        }
    }
});

// ================= LOGOUT =================
function logoutUser() {
    localStorage.removeItem("loggedInUser");
    alert("Logged out successfully!");
    window.location.href = "login.html";
}