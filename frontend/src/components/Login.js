import React, { useState } from "react";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:5000";

const LoginPage = ({ onLogin }) => {
  const [mode, setMode] = useState("login"); // login | signup | reset
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const isRegister = mode === "signup";
  const isReset = mode === "reset";

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!email || (!isReset && !password) || (isRegister && !username) || (isReset && !password)) {
      setError("Please fill out all required fields.");
      return;
    }

    setLoading(true);
    try {
      let endpoint = "/login";
      let payload = { email, password };

      if (isRegister) {
        endpoint = "/signup";
        payload = { username, email, password };
      } else if (isReset) {
        endpoint = "/reset-password";
        payload = { email, new_password: password };
      }

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();

      if (res.ok) {
        if (isReset) {
          setSuccess(data.message || "Password updated. You can now log in.");
          setMode("login");
          setPassword("");
        } else if (data.user) {
          onLogin(data.user);
        } else {
          setError(data.message || "Unable to process request.");
        }
      } else {
        setError(data.message || "Unable to process request.");
      }
    } catch (err) {
      setError("Error connecting to server.");
    } finally {
      setLoading(false);
    }
  };

  const toggleMode = () => {
    setMode(isRegister ? "login" : "signup");
    setError("");
    setSuccess("");
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center bg-cover bg-center relative"
      style={{
        backgroundImage:
          "url('https://www.sacredheart.edu/media/shu-media/homepage/20250821-Campus-Visit-Opps-UG-1220x686-740x416.jpg')",
      }}
    >
      <div className="absolute inset-0 bg-black/50"></div>

      <div className="relative z-10 bg-white/90 backdrop-blur-md shadow-2xl rounded-2xl p-10 w-full max-w-md animate-fadeIn">
        <h1 className="text-3xl font-bold text-center text-red-700 mb-4">
          Sacred Heart University
        </h1>
        <p className="text-center text-gray-700 mb-6">
          {isRegister
            ? "Create a new eLearning account"
            : isReset
              ? "Reset your password"
              : "eLearning Module Login"}
        </p>

        <form onSubmit={handleSubmit} className="space-y-5">
          {isRegister && (
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-semibold text-gray-700 mb-1"
              >
                Username
              </label>
              <input
                id="username"
                type="text"
                placeholder="Choose a username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-red-500 focus:outline-none"
              />
            </div>
          )}

          <div>
            <label
              htmlFor="email"
              className="block text-sm font-semibold text-gray-700 mb-1"
            >
              Email Address
            </label>
            <input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-red-500 focus:outline-none"
            />
          </div>

          {!isReset && (
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-semibold text-gray-700 mb-1"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                placeholder={isRegister ? "Create a password" : "Enter your password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-red-500 focus:outline-none"
              />
            </div>
          )}

          {isReset && (
            <div>
              <label
                htmlFor="new-password"
                className="block text-sm font-semibold text-gray-700 mb-1"
              >
                New Password
              </label>
              <input
                id="new-password"
                type="password"
                placeholder="Enter a new password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-red-500 focus:outline-none"
              />
            </div>
          )}

          {error && (
            <p className="text-sm text-red-600 text-center">
              {error}
            </p>
          )}
          {success && (
            <p className="text-sm text-green-600 text-center">
              {success}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-red-700 text-white font-semibold py-3 rounded-lg hover:bg-red-800 transition disabled:opacity-70"
          >
            {loading ? "Please wait..." : isRegister ? "Sign Up" : isReset ? "Reset Password" : "Login"}
          </button>
        </form>

        <button
          type="button"
          onClick={toggleMode}
          className="w-full mt-4 text-sm text-red-700 hover:underline"
        >
          {isRegister
            ? "Already have an account? Log in"
            : isReset
              ? "Return to login"
              : "Need an account? Sign up"}
        </button>

        {!isRegister && !isReset && (
          <button
            type="button"
            onClick={() => { setMode('reset'); setError(''); setSuccess(''); }}
            className="w-full mt-2 text-sm text-red-700 hover:underline"
          >
            Forgot password?
          </button>
        )}

        <p className="text-center text-sm text-gray-600 mt-6">
          Ac {new Date().getFullYear()} Sacred Heart University | eLearning Portal
        </p>
      </div>
    </div>
  );
};

export default LoginPage;
