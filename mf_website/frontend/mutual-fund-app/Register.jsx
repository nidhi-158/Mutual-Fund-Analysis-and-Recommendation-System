import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const Register = () => {
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await axios.post("http://localhost:8000/register", form);
      localStorage.setItem("token", res.data.access_token);
      navigate("/main");
    } catch (err) {
      if (err.response?.status === 400) {
        setError("⚠️ Email already registered. Please log in.");
      } else {
        setError(err.response?.data?.detail || "❌ Registration failed.");
      }
    }
  };

  return (
    <div className="container auth-box">
      <h2>📝 Register</h2>
      <form onSubmit={handleSubmit}>
        <label>Email:</label>
        <input type="email" name="email" value={form.email} onChange={handleChange} required />
        <label>Password:</label>
        <input type="password" name="password" value={form.password} onChange={handleChange} required />
        <button type="submit">Register</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <p style={{ marginTop: "10px" }}>
        Already registered? <Link to="/">Login here</Link>
      </p>
    </div>
  );
};

export default Register;
