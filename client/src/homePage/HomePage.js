import React from 'react';
import { useNavigate } from 'react-router-dom';
import AuthAPI from '../auth/AuthAPI';

const Home = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    AuthAPI.logout();
    navigate('/login');
  };

  return (
    <div>
      <h2>Home Page</h2>
      <p>Welcome! You are logged in.</p>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
};

export default Home;
