import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './auth/Login';
import Register from './auth/Register';
import HomePage from './homePage/HomePage';
import PrivateRoute from './component/PrivateRoute';
import Presentation from './presentation/Presentation';

function App() {
  return (
    <Router>
      <div>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/homepage" element={<PrivateRoute element={HomePage} />} />
          <Route path="/presentation" element={<Presentation />} />
          <Route path="/" element={<Presentation />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
