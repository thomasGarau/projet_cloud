import Cookies from 'js-cookie';
import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    const isAuth = Cookies.get('isAuthenticated');
    return isAuth === 'true';
  });

  useEffect(() => {
    Cookies.set('isAuthenticated', isAuthenticated, { secure: true, sameSite: 'strict' });
  }, [isAuthenticated]);

  const loginContext = () => {
    setIsAuthenticated(true);
  };

  const logoutContext = () => {
    setIsAuthenticated(false);
    Cookies.remove('userToken');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, loginContext, logoutContext }}>
      {children}
    </AuthContext.Provider>
  );
};
