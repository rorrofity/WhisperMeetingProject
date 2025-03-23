import React, { useState } from 'react';
import Login from './Login';
import Register from './Register';

const Auth = () => {
  const [showLogin, setShowLogin] = useState(true);
  
  const toggleForm = () => {
    setShowLogin(!showLogin);
  };
  
  return (
    <div className="w-full max-w-md mx-auto">
      {showLogin ? (
        <Login onToggleForm={toggleForm} />
      ) : (
        <Register onToggleForm={toggleForm} />
      )}
    </div>
  );
};

export default Auth;
