import React, { useContext, useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../../context/AuthProvider';
import Loader from '../loader/Loader';

const PrivateRouteContext = ({ element: Element }) => {
  const { isAuthenticated } = useContext(AuthContext);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  if (isLoading) {
    return <Loader />;
  }

  return isAuthenticated ? <Element /> : <Navigate to="/login" replace />;
};

export default PrivateRouteContext;
