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

    const uploadFile = async (file, file_id, onStart, onComplete, onError) => {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('file_id', file_id);
    
        const config = {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        };
    
        onStart(); // Callback pour démarrer l'indicateur de chargement
    
        try {
            const response = await api.post(`${apiController}/upload-file`, formData, config);
            onComplete(); // Callback pour arrêter l'indicateur de chargement en cas de succès
        } catch (error) {
            console.error("Erreur lors de l'envoi du fichier : ", error);
            onError(error); // Callback pour gérer l'erreur
        }
    };    

    const checkUploadStatus = async (file_id, checkInterval, onCompletion) => {
        console.log('Checking upload status for file_id:', file_id);
        try {
            const response = await api.get(`${apiController}/check-status/${file_id}`);
            if (response.data.status === 'completed' || response.data.status === 'failed') {
                console.log('Upload status:', response.data.status);
                clearInterval(checkInterval);
                onCompletion();
            } else {
                console.log(response.data.status);

            }
        } catch (error) {
            console.error('Error checking status:', error);
            clearInterval(checkInterval);
            onCompletion();
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
        checkUploadStatus,
    };
};
