import React from 'react';
import Navbar from '../component/navBar/NavBar';
import './presentation.css';

const Presentation = () => {
  return (
    <div className="presentation-container">
      <Navbar />
      <header className="presentation-header">
        <h1>Bienvenue sur CloudStorage</h1>
        <p>Votre espace sécurisé pour stocker et partager vos fichiers.</p>
      </header>
      <section className="features">
        <h2>Fonctionnalités</h2>
        <div className="feature-list">
          <div className="feature-item">
            <h3>Stockage sécurisé</h3>
            <p>Stockez vos fichiers en toute sécurité grâce à notre technologie de chiffrement de pointe.</p>
          </div>
          <div className="feature-item">
            <h3>Partage facile</h3>
            <p>Partagez vos documents avec qui vous voulez, quand vous voulez, en toute simplicité.</p>
          </div>
          <div className="feature-item">
            <h3>Accès de n'importe où</h3>
            <p>Accédez à vos fichiers depuis n'importe quel appareil, à tout moment et en tout lieu.</p>
          </div>
        </div>
      </section>
      <section className="call-to-action">
        <h2>Prêt à commencer ?</h2>
        <p>Rejoignez CloudStorage dès maintenant et profitez de 5GB de stockage gratuit.</p>
      </section>
    </div>
  );
};

export default Presentation;
