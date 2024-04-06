import { React, useEffect, useContext } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Login from './auth/Login';
import Register from './auth/Register';
import HomePage from './homePage/HomePage';
import PublicRoute from './component/route/PublicRoute';
import Presentation from './presentation/Presentation';
import PrivateRouteContext from './component/route/PrivateRouteContext';
import { AuthContext } from './context/AuthProvider';
import history from './config/history';

function App() {

  const { logoutContext } = useContext(AuthContext);

  useEffect(() => {
    const handleLogout = () => {
      logoutContext();
    };

    window.addEventListener('logoutRequired', handleLogout);

    return () => {
      window.removeEventListener('logoutRequired', handleLogout);
    };
  }, [logoutContext]);

  return (
    <Router history={history}>
      <div>
        <Routes>
          {/* public routes redirigé vers homePage si utilisateur deja co*/}
          <Route path="/login" element={<PublicRoute element={() => <Login />} />} />
          <Route path="/register" element={<PublicRoute element={() => <Register />} />} />
          <Route path="/presentation" element={<PublicRoute element={() => <Presentation />} />} />
          
          {/* private routes  redirigé vers Login si utilisateur pas co*/}
          <Route path="/homepage" element={<PrivateRouteContext element={HomePage} />} />
          <Route path="/" element={<Presentation />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
