import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import { useAuthService } from '../../auth/AuthAPI';

const PrivateRoute = ({  element: Element }) => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const { verifyToken } = useAuthService();

    useEffect(() => {
        const checkAuth = async () => {
            try {
                const {token} = Cookies.get();
                const valide = await verifyToken(token);
                setIsAuthenticated(valide);
            } catch (error) {
                console.error('Erreur lors de la vérification du token :', error);
            } finally {
                setIsLoading(false);
            }
        };

        checkAuth();
    }, []);

    if (isLoading) {
        return <div>Chargement...</div>;
    }

    return isAuthenticated ? <Element /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;