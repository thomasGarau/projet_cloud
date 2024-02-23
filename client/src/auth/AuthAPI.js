import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = 'http://localhost:5000';

class AuthService {
  async login(username, password) {
    try {
      const response = await axios.post(`${API_URL}/login`, { username, password });
      if (response.data.token) {
        Cookies.set('userToken', response.data.token);
      }
      return response.data;
    } catch (error) {
      console.error("Une erreur est survenue lors de la tentative de connexion : ", error);
      throw error;
    }
  }

  async register(username, password) {
    try {
      const response = await axios.post(`${API_URL}/register`, { username, password });
      if (response.data.token) {
        Cookies.set('userToken', response.data.token);
      }
      return response.data;
    } catch (error) {
      console.error("Une erreur est survenue lors de l'inscription : ", error);
      throw error;
    }
  }

  logout() {
    Cookies.remove('userToken');
  }

  async verifyToken() {
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
      throw error;
    }
  }
}

export default new AuthService();
