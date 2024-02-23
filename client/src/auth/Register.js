import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthAPI from '../auth/AuthAPI';
import Cookies from 'js-cookie';

const Register = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const token = Cookies.get('userToken');
    if (token) {
      navigate('/homePage');
    }
  }, [navigate]);

  const handleRegister = (e) => {
    e.preventDefault();
    AuthAPI.register(username, password).then(() => {
      navigate('/home');
      window.location.reload();
    });
  };

  return (
    <div>
      <h2>Register</h2>
      <form onSubmit={handleRegister}>
        <div>
          <label>Username:</label>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div>
          <label>Password:</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <div>
          <button type="submit">Register</button>
        </div>
      </form>
    </div>
  );
};

export default Register;
