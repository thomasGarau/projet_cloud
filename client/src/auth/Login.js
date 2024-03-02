import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {useAuthService} from '../auth/AuthAPI';
import './login.css';
import Navbar from '../component/navBar/NavBar';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { login } = useAuthService();

  const handleLogin = (e) => {
    e.preventDefault();
    login(username, password).then(() => {
      navigate('/homePage');
    });
  };

  return (
    <div className="login-container">
      <Navbar />
      <div className="login-form-container">
        <h2>Login</h2>
        <form onSubmit={handleLogin} className="login-form">
          <div className="input-group">
            <label>Username</label>
            <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <button type="submit" className="login-button">Login</button>
        </form>
      </div>
    </div>
  );
};

export default Login;
