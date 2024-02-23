import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthAPI from '../auth/AuthAPI';
import Cookies from 'js-cookie';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = Cookies.get('userToken');
    if (token) {
      navigate('/homePage');
    }
  }, [navigate]);

  const handleLogin = (e) => {
    e.preventDefault();
    AuthAPI.login(username, password).then(() => {
      navigate('/home');
      window.location.reload();
    });
  };

  return (
    <div>
      <form onSubmit={handleLogin}>
        <label>
          Username:
          <input type="text" value={username} onChange={(e) => setUsername(e.target.value)} />
        </label>
        <label>
          Password:
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
