import axios from 'axios';
import Cookies from 'js-cookie';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthProvider';


const API_URL = 'http://localhost:5000/files';

export const useFileService = () => {
    const fetchUserFilesInfo = async () => {
        const token = Cookies.get('userToken');
        const config = {
            headers: {
                'Authorization': `Bearer ${token}`
            },
        };

        try {
            const response = await axios.get(`${API_URL}/user-files-info`, config);
            return response.data;
        } catch (error) {
            console.error("Erreur lors de la récupération des informations des fichiers : ", error);
            throw error;
        }
    };

    const fetchUserFile = async (filename, extension) => {
        const token = Cookies.get('userToken');
        const config = {
            headers: {
            'Authorization': `Bearer ${token}`,
            },
            responseType: 'blob',
        };

        try {
            const response = await axios.get(`${API_URL}/user-files/${filename}${extension}`, config);
            return response.data;
        } catch (error) {
            console.error("Erreur lors de la récupération du fichier : ", error);
            throw error;
        }
    };

    const uploadFile = async (file) => {
        const token = Cookies.get('userToken');
        const formData = new FormData();
        formData.append('file', file);

        const config = {
            headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data',
            },
        };

        try {
            const response = await axios.post(`${API_URL}/upload-file`, formData, config);
            return response.data;
        } catch (error) {
            console.error("Erreur lors de l'envoi du fichier : ", error);
            throw error;
        }
    };

    const renameFile = async (originalName, newName) => {
        console.log('Renommage du fichier:', originalName, newName)
        const token = Cookies.get('userToken');
        const config = {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        };
    
        try {
            const response = await axios.post(`${API_URL}/rename-file`, { originalName, newName }, config);
            console.log('Fichier renommé avec succès');
            return response.data;
        } catch (error) {
            console.error("Erreur lors du renommage du fichier : ", error);
            throw error;
        }
    };

    const deleteFile = async (filename) => {
        const token = Cookies.get('userToken');
        const config = {
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        };
    
        try {
            const response = await axios.delete(`${API_URL}/delete-file/${filename}`, config);
            console.log('Fichier supprimé avec succès');
            return response.data;
        } catch (error) {
            console.error("Erreur lors de la suppression du fichier : ", error);
            throw error;
        }
    };    

    return {
        fetchUserFilesInfo,
        fetchUserFile,
        uploadFile,
        renameFile,
        deleteFile
    };
};
