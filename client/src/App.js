import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './auth/Login';
import Register from './auth/Register';
import HomePage from './homePage/HomePage';
import PrivateRoute from './component/route/PrivateRoute';
import PublicRoute from './component/route/PublicRoute';
import Presentation from './presentation/Presentation';

function App() {
  return (
    <Router>
      <div>
        <Routes>
          {/* public routes redirigé vers homePage si utilisateur deja co*/}
          <Route path="/login" element={<PublicRoute element={() => <Login />} />} />
          <Route path="/register" element={<PublicRoute element={() => <Register />} />} />
          <Route path="/presentation" element={<PublicRoute element={() => <Presentation />} />} />
          
          {/* private routes  redirigé vers Login si utilisateur pas co*/}
          <Route path="/homepage" element={<PrivateRoute element={HomePage} />} />
          <Route path="/" element={<Presentation />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
