import React, { useContext } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../../context/AuthProvider';
import { useAuthService } from '../../auth/AuthAPI';
import './navBar.css';

const Navbar = () => {
  const { isAuthenticated } = useContext(AuthContext);
  const navigate = useNavigate();
  const { logout } = useAuthService();
  const location = useLocation();
  const currentPath = location.pathname;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };
  const handleLogin = () => {
    navigate('/login');
  }
  const handleRegister = () => {
    navigate('/register');
  }
  const handleHome = () => {
    navigate('/');
  }

  return (
    <nav className="navbar">
      <button className="navbar-brand" onClick={handleHome}>MonApp</button>
      <div className="nav-items">
        {!isAuthenticated ? (
          <>
            {currentPath === '/login' ? (
              <button onClick={handleRegister}>Inscription</button>
            ) : currentPath === '/register' ? (
              <button onClick={handleLogin}>Connexion</button>
            ) : (
              <>
                <button onClick={handleLogin}>Connexion</button>
                <button onClick={handleRegister}>Inscription</button>
              </>
            )}
          </>
        ) : (
          <button onClick={handleLogout}>Déconnexion</button>
        )}
      </div>
    </nav>
  );
};
export default Navbar;