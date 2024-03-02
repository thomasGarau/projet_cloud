import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../component/navBar/NavBar';
import './homePage.css';

const HomePage = () => {
  const navigate = useNavigate();

  const navigateToSection = (section) => {
    // Logique pour naviguer vers la section sélectionnée
    console.log(`Navigating to ${section}`);
  };

  return (
    <div className="homePage">
      <Navbar />
      <div className="sidebar">
        <ul>
          <li onClick={() => navigateToSection('recent')}>Recent Files</li>
          <li onClick={() => navigateToSection('shared')}>Shared With Me</li>
          <li onClick={() => navigateToSection('storage')}>Storage</li>
          <li onClick={() => navigateToSection('allFiles')}>All Files</li>
        </ul>
      </div>
      <div className="main-content">
        <div className="search-bar">
          <input type="text" placeholder="Search files..." />
        </div>
        <div className="content">
          {/* Contenu dynamique en fonction de la section sélectionnée */}
          <h2>Section Title</h2>
          <p>Content goes here...</p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
