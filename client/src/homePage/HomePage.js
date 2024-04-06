import React, { useState } from 'react';
import Navbar from '../component/navBar/NavBar';
import RecentFiles from '../component/section/RecentFiles';
import SharedWithMe from '../component/section/SharedWithMe';
import StorageInfo from '../component/section/StorageInfo';
import AllFiles from '../component/section/AllFiles';
import './homePage.css';
import AddFileModal from '../component/modal/AddFileModal';
import { useFileService } from '../API/FileServiceAPI';
import { getMimeTypes } from '../services/FileService';

const sectionComponents = {
  recent: RecentFiles,
  shared: SharedWithMe,
  storage: StorageInfo,
  allFiles: AllFiles
};

const HomePage = () => {
  const [selectedSection, setSelectedSection] = useState('allFiles');
  const [isAddFileModalOpen, setIsAddFileModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const SectionComponent = sectionComponents[selectedSection];
  const { fetchUserFile } = useFileService();

  const handleSearchChange = (event) => {
    setSearchQuery(event.target.value);
    setSelectedSection('allFiles');
  };

  const openFile = async (fileName, extension) => {
    try {
      const fileData = await fetchUserFile(fileName, extension);
      const mimeTypes = getMimeTypes();
      const blobType = mimeTypes[extension.split('.')[1]] || '';
  
      if (!blobType) {
        console.error('Format de fichier non pris en charge');
        return;
      }
  
      const blob = new Blob([fileData], { type: blobType });
      const url = window.URL.createObjectURL(blob);
      window.open(url, '_blank');
    } catch (error) {
      console.error("Erreur lors de l'ouverture du fichier :", error);
    }
  };
  

  return (
    <div className="homePage">
      <Navbar />
      {isAddFileModalOpen && (
        <AddFileModal
          onClose={() => setIsAddFileModalOpen(false)}
          onUpload={(file) => { console.log('Uploading', file); }}
        />
      )}
      <div className="sidebar">
        <ul>
          <li
            className={selectedSection === 'allFiles' ? 'selected' : ''}
            onClick={() => setSelectedSection('allFiles')}
          >
            All Files
          </li>
          <li
            className={selectedSection === 'recent' ? 'selected' : ''}
            onClick={() => setSelectedSection('recent')}
          >
            Recent Files
          </li>
          <li
            className={selectedSection === 'shared' ? 'selected' : ''}
            onClick={() => setSelectedSection('shared')}
          >
            Shared With Me
          </li>
          <li
            className={selectedSection === 'storage' ? 'selected' : ''}
            onClick={() => setSelectedSection('storage')}
          >
            Storage
          </li>
          <li onClick={() => setIsAddFileModalOpen(true)}>Add Files</li>
        </ul>
      </div>
      <div className="main-content">
        <div className="search-bar">
          <input type="text" placeholder="Search files..." value={searchQuery} onChange={handleSearchChange} />
        </div>
        <div className="content">
          <SectionComponent searchQuery={searchQuery} openFile={openFile} />
        </div>
      </div>
    </div>
  );
};

export default HomePage;
