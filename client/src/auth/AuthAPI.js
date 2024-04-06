import axios from 'axios';
import Cookies from 'js-cookie';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthProvider';

const API_URL = 'http://localhost:5000/users';

export const useAuthService = () => {
  const { loginContext, logoutContext } = useContext(AuthContext);

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API_URL}/login`, { username, password });
      if (response.data.token) {
        Cookies.set('userToken', response.data.token);
        loginContext();
      }
      return response.data;
    } catch (error) {
      console.error("Une erreur est survenue lors de la tentative de connexion : ", error);
    }
  };

  const register = async (username, password, email, firstName, lastName) => {
    try {
      const response = await axios.post(`${API_URL}/register`, {
        username,
        password,
        email,
        firstName,
        lastName
      });
      if (response.data.token) {
        Cookies.set('userToken', response.data.token);
        loginContext();
      }
      return response.data;
    } catch (error) {
      console.error("Une erreur est survenue lors de l'inscription : ", error);
    }
  };

  const logout = () => {
    Cookies.remove('userToken');
    logoutContext();
  };

  const verifyToken = async () => {
    const token = Cookies.get('userToken');
    try {
      const response = await axios.get(`${API_URL}/verify-token`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.data.status === 'success') {
        return true;
      }
      throw new Error('Token invalide');
    } catch (error) {
      console.error("Une erreur est survenue lors de la vérification du token : ", error);
    }
  };

  return { login, register, logout, verifyToken };
};
