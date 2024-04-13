import React from 'react';
import './loadingIndicator.css';

const LoadingIndicator = ({ files }) => {
    return (
        <div className="loading-indicator">
            {files.map((file, index) => (
                <div key={index} className="loading-item">
                    <div className="spinner"></div>
                    Chargement de {file}...
                </div>
            ))}
        </div>
    );
}

export default LoadingIndicator;
