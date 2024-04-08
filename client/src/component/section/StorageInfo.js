import React, { useState, useEffect } from 'react';
import './storageInfo.css';
import { useFileService } from '../../API/FileServiceAPI';

const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bits';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bits', 'KO', 'MO', 'GO', 'TO'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

const StorageInfo = () => {
    const [storageInfo, setStorageInfo] = useState({});
    const { getStorageInfo } = useFileService();

    useEffect(() => {
        const fetchStorageInfo = async () => {
            const info = await getStorageInfo();
            setStorageInfo(info);
        };

        fetchStorageInfo();
    }, []);

    const usedPercentage = storageInfo.total_compressed_size / (storageInfo.total_space * 1024 * 1024 * 1024) * 100;
    const spaceSaved = storageInfo.total_original_size - storageInfo.total_compressed_size;

    return (
        <div className="storage-info">
            <h2>Storage Info</h2>
            <div className="storage-bar-container">
                <div className="storage-bar" style={{ width: `${usedPercentage}%` }}></div>
            </div>
            <p>Espace disponible: {formatBytes(storageInfo.total_space * 1024 * 1024 * 1024)}</p>
            <p>Espace utilisée: {formatBytes(storageInfo.total_compressed_size)}</p>
            <p>Espace économisé: {formatBytes(spaceSaved)} grâce à la compression</p>
        </div>
    );
}

export default StorageInfo;
