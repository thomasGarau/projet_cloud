import React, { useState, useContext } from 'react';
import Navbar from '../component/navBar/NavBar';
import RecentFiles from '../component/section/RecentFiles';
import SharedWithMe from '../component/section/SharedWithMe';
import StorageInfo from '../component/section/StorageInfo';
import AllFiles from '../component/section/AllFiles';
import './homePage.css';
import AddFileModal from '../component/modal/AddFileModal';
import { useFileService } from '../API/FileServiceAPI';
import { AuthContext } from '../context/AuthProvider';

const sectionComponents = {
  recent: RecentFiles,
  shared: SharedWithMe,
  storage: StorageInfo,
  allFiles: AllFiles
};

const HomePage = () => {
  const { uploadFile } = useFileService();
  const [selectedSection, setSelectedSection] = useState('allFiles');
  const [isAddFileModalOpen, setIsAddFileModalOpen] = useState(false);
  const SectionComponent = sectionComponents[selectedSection];

  const handleUpload = async (file) => {
    console.log('Fichier à télécharger:', file);
    try {
      const response = await uploadFile(file);
      console.log('Réponse du serveur:', response);
    } catch (error) {
      console.error('Erreur lors de l\'envoi du fichier:', error);
    }
  };

  return (
    <div className="homePage">
      <Navbar />
      {isAddFileModalOpen && (
        <AddFileModal
          onClose={() => setIsAddFileModalOpen(false)}
          onUpload={(file) => {handleUpload(file)}}
        />
      )}
      <div className="sidebar">
        <ul>
          <li onClick={() => setIsAddFileModalOpen(true)}>Add Files</li>
          <li onClick={() => setSelectedSection('allFiles')}>All Files</li>
          <li onClick={() => setSelectedSection('recent')}>Recent Files</li>
          <li onClick={() => setSelectedSection('shared')}>Shared With Me</li>
          <li onClick={() => setSelectedSection('storage')}>Storage</li>
        </ul>
      </div>
      <div className="main-content">
        <div className="search-bar">
          <input type="text" placeholder="Search files..." />
        </div>
        <div className="content">
          <SectionComponent />
        </div>
      </div>
    </div>
  );
};

export default HomePage;
