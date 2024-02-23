import React from 'react';
import { useNavigate } from 'react-router-dom';

const Presentation = () => {
  const navigate = useNavigate();

  return (
    <div>
      <h1>Bienvenue sur notre application</h1>
      <button onClick={() => navigate('/login')}>Login</button>
      <button onClick={() => navigate('/register')}>Register</button>
    </div>
  );
};

export default Presentation;
