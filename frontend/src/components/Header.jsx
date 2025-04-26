import React from 'react';
import { FiUser, FiLogOut } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import logo from '../assets/favicon_rocketflow_colorTrans.png';

const Header = ({ onHistoryClick, onLogoutClick, isHistoryView }) => {
  const { currentUser } = useAuth();
  const isLoggedIn = !!currentUser;

  return (
    <div className="w-full bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-2">
            <img src={logo} alt="Rocketflow Logo" className="h-8 w-auto" />
            <span className="text-2xl font-bold text-gray-800">ROCKETFLOW</span>
          </div>

          <div className="flex items-center space-x-4">
            {isLoggedIn && (
              <>
                <button 
                  onClick={onHistoryClick} 
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition duration-150 ease-in-out"
                >
                  {isHistoryView ? 'Nueva Transcripción' : 'Historial'}
                </button>
                <button className="flex items-center px-4 py-2 text-sm font-medium text-blue-800 bg-[#E9F6FE] rounded-md hover:bg-[#d0eefc] transition duration-150 ease-in-out">
                  <FiUser className="h-4 w-4 mr-1" />
                  {currentUser.username}
                </button>
                <button onClick={onLogoutClick} title="Cerrar Sesión" className="p-2 text-gray-500 hover:text-red-600 transition duration-150 ease-in-out">
                  <FiLogOut className="h-5 w-5" />
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Header;
