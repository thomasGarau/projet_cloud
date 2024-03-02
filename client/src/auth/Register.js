import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthService } from '../auth/AuthAPI';
import { validateEmail, validatePassword } from '../services/regex';
import './register.css';
import Navbar from '../component/navBar/NavBar';

const Register = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState({});
  const navigate = useNavigate();
  const { register } = useAuthService();

  const handleRegister = (e) => {
    e.preventDefault();
    let isValid = true;
    let errors = {};

    if (!validateEmail(email)) {
      errors.email = 'Format d\'email invalide';
      setEmail('');
      isValid = false;
    }

    if (!validatePassword(password)) {
      errors.password = 'Le mot de passe doit contenir au moins 12 caractères, dont une majuscule, une minuscule, un chiffre et un caractère spécial';
      setPassword('');
      setConfirmPassword('');
      isValid = false;
    }

    if (password !== confirmPassword) {
      errors.confirmPassword = 'Les mots de passe ne correspondent pas';
      setConfirmPassword('');
      isValid = false;
    }

    setError(errors);

    if (isValid) {
      register(username, password, email, firstName, lastName).then(() => {
        navigate('/homePage');
      });
    }
  };

  return (
    <div className="register-container">
      <Navbar />
      <div className="register-form-container">
        <h2>Register</h2>
        <form onSubmit={handleRegister} className="register-form">
          <div className="input-group">
            <label>First Name</label>
            <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} />
            {error.firstName && <div className="error-message">{error.firstName}</div>}
          </div>
          <div className="input-group">
            <label>Last Name</label>
            <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} />
            {error.lastName && <div className="error-message">{error.lastName}</div>}
          </div>
          <div className="input-group">
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
            {error.email && <div className="error-message">{error.email}</div>}
          </div>
          <div className="input-group">
            <label>Username</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
            {error.username && <div className="error-message">{error.username}</div>}
          </div>
          <div className="input-group">
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            {error.password && <div className="error-message">{error.password}</div>}
          </div>
          <div className="input-group">
            <label>Confirm Password</label>
            <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} />
            {error.confirmPassword && <div className="error-message">{error.confirmPassword}</div>}
          </div>
          <button type="submit" className="register-button">Register</button>
        </form>
      </div>
    </div>
  );
};

export default Register;
