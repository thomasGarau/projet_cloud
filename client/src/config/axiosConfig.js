import axios from 'axios';
import Cookies from 'js-cookie';
import  history from './history';

const API_URL = 'http://localhost:5000';

const api = axios.create({
  baseURL: API_URL,
});

api.interceptors.request.use((config) => {
  const token = Cookies.get('userToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

api.interceptors.response.use(async (response) => {
  return response;
}, async (error) => {
  if (error.response && error.response.status === 401) {
    const logoutEvent = new Event('logoutRequired');
    window.dispatchEvent(logoutEvent);
    history.push('/login');
    console.log('Déconnexion due à un token invalide ou expiré.');
    return new Promise((resolve) => {
      resolve({ data: 'Session expired, user logged out.' });
    });
  }
  return Promise.reject(error);
});

export default api;
