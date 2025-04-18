
const authHost = 'localhost' //import.meta.env.VITE_AUTH_HOST
const authPort = 4000 //import.meta.env.VITE_AUTH_PORT

async function validateTokenAndLoadApp() {
    const token = localStorage.getItem("token");
    if (!token) return showLogin();
    try {
        const res = await fetch("/auth/protected", {
            method: "GET",
            headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Unauthorized");
        loadReactApp();
    } catch (err) {
        localStorage.removeItem("token");
        showLogin();
    }
}


function loadReactApp() {
    const script = document.createElement("script");
    script.type = "module";
    script.src = "./app/index.jsx";
    document.body.appendChild(script);
}


function showLogin() {
  document.getElementById("root").innerHTML = `
    <div style="padding: 20px;">
      <h2>Login</h2>
      <input id="email" placeholder="Email" value="user@example.com" />
      <input id="password" type="password" placeholder="Password" value="password123" />
      <button onclick="handleLogin()">Login</button>
      <p>or <a href="#" onclick="showRegister()">register</a></p>
      <p id="error" style="color:red;"></p>
    </div>
  `;
}


function showRegister() {
  document.getElementById("root").innerHTML = `
    <div style="padding: 20px;">
      <h2>Register</h2>
      <input id="reg_email" placeholder="Email" />
      <input id="reg_password" type="password" placeholder="Password" />
      <input id="reg_name" placeholder="Full Name" />
      <button onclick="handleRegister()">Register</button>
      <p><a href="#" onclick="showLogin()">Back to login</a></p>
      <p id="reg_error" style="color:red;"></p>
    </div>
  `;
}


async function handleLogin() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const res = await fetch("/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({
                username: email,
                password: password
            })
        });

        if (!res.ok) {
            const text = await res.text();
            throw new Error(`Login failed: ${text}`);
        }

        const data = await res.json();

        console.log("✅ Login success", data);

        if (data.access_token) {
            localStorage.setItem("token", data.access_token);
            validateTokenAndLoadApp();  // 👈 this should now run
        } else {
            throw new Error("Invalid login response");
        }

    } catch (err) {
        console.error("🚨 Login error:", err.message);
        document.getElementById("error").innerText = err.message;
    }
}

async function handleRegister() {
  const email = document.getElementById("reg_email").value;
  const password = document.getElementById("reg_password").value;
  const name = document.getElementById("reg_name").value;
  try {
      const res = await fetch("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: email, password, fullname: name, email: email })
    });
    const data = await res.json();
    alert(data.message);
    showLogin();
  } catch (err) {
    document.getElementById("reg_error").innerText = "Registration failed.";
  }
}

validateTokenAndLoadApp();
