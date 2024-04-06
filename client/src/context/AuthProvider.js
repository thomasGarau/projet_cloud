import Cookies from 'js-cookie';
import React, { createContext, useState } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const loginContext = (userData) => {
    setIsAuthenticated(true);
  };

  const logoutContext = () => {
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, loginContext, logoutContext }}>
      {children}
    </AuthContext.Provider>
  );
};
