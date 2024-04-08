import api from '../config/axiosConfig';

const apiController = '/files';

export const useFileService = () => {
    const fetchUserFilesInfo = async () => {
        try {
            const response = await api.get(`${apiController}/user-files-info`);
            return response.data;
        } catch (error) {
            console.error("Erreur lors de la récupération des informations des fichiers : ", error);
            throw new Error('Erreur lors de la récupération des informations des fichiers');
        }
    };

    const fetchRecentUserFilesInfo = async () => {
        try {
            const response = await api.get(`${apiController}/recent-user-files-info`);
            return response.data;
        } catch (error) {
            console.error("Erreur lors de la récupération des informations des fichiers récents : ", error);
            throw new Error('Erreur lors de la récupération des informations des fichiers récents');
        }
    }

    const fetchSharedWithMeFiles = async () => {
       try{
            const response = await api.get(`${apiController}/shared-with-me`);
            return response.data;
        } catch (error) {
            console.error("Erreur lors de la récupération des fichiers partagés : ", error);
            throw new Error('Erreur lors de la récupération des fichiers partagés');
       } 
    }

    const fetchUserFile = async (filename, extension) => {
        const config = {
            responseType: 'blob',
        }
        
        try {
            const response = await api.get(`${apiController}/user-files/${filename}${extension}`, config);
            return response.data;
        } catch (error) {
            console.error("Erreur lors de la récupération du fichier : ", error);
            throw new Error('Erreur lors de la récupération du fichier');
        }
    };

    const uploadFile = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        const config = {
            headers: {
            'Content-Type': 'multipart/form-data',
            },
        };

        try {
            const response = await api.post(`${apiController}/upload-file`, formData, config);
            return response.data;
        } catch (error) {
            console.error("Erreur lors de l'envoi du fichier : ", error);
            throw new Error('Erreur lors de l\'envoi du fichier');
        }
    };

    const renameFile = async (originalName, newName) => {
        try {
            const response = await api.post(`${apiController}/rename-file`, { originalName, newName });
            console.log('Fichier renommé avec succès');
            return response.data;
        } catch (error) {
            console.error("Erreur lors du renommage du fichier : ", error);
            throw new Error('Erreur lors du renommage du fichier');
        }
    };

    const deleteFile = async (filename) => {
        try {
            const response = await api.delete(`${apiController}/delete-file/${filename}`);
            console.log('Fichier supprimé avec succès');
            return response.data;
        } catch (error) {
            console.error("Erreur lors de la suppression du fichier : ", error);
            throw new Error('Erreur lors de la suppression du fichier');
        }
    };    

    const getStorageInfo = async () => { 
        try {
            const response = await api.get(`${apiController}/storage-info`);
            return response.data;
        } catch (error) {
            console.error("Erreur lors de la récupération des informations de stockage : ", error);
            throw new Error('Erreur lors de la récupération des informations de stockage');
        }
    };

    const shareFile = async (filename, shareWithUsername) => {
        try {
            const response = await api.post(`${apiController}/share-file`, { filename, shareWithUsername });
            console.log('Fichier partagé avec succès');
            return response.data;
        } catch (error) {
            console.error("Erreur lors du partage du fichier : ", error);
            throw new Error('Erreur lors du partage du fichier');
        }
    };
    
    const fetchFilesSharedWithMe = async () => {
        try {
            const response = await api.get(`${apiController}/shared-with-me`);
            console.log('Fichiers partagés récupérés avec succès');
            return response.data;
        } catch (error) {
            console.error("Erreur lors de la récupération des fichiers partagés : ", error);
            throw new Error('Erreur lors de la récupération des fichiers partagés');
        }
    };
    
    const stopSharingFile = async (filename) => {
        try {
          const response = await api.delete(`${apiController}/stop-sharing-file`, {
            data: { filename },
            headers: { 'Content-Type': 'application/json' },
          });
          console.log('Arrêt du partage du fichier avec succès');
          return response.data;
        } catch (error) {
          console.error("Erreur lors de l'arrêt du partage du fichier : ", error);
          throw new Error('Erreur lors de l\'arrêt du partage du fichier');
        }
    };

    return {
        fetchUserFilesInfo,
        fetchUserFile,
        fetchRecentUserFilesInfo,
        fetchSharedWithMeFiles,
        uploadFile,
        renameFile,
        deleteFile,
        getStorageInfo,
        shareFile,
        fetchFilesSharedWithMe,
        stopSharingFile,
    };
};
