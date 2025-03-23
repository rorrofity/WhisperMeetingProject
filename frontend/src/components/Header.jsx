import React from 'react';
import { FiHeadphones } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';

const Header = () => {
  const { currentUser } = useAuth();

  return (
    <header className="bg-primary-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <FiHeadphones className="text-3xl mr-2" />
            <h1 className="text-xl md:text-2xl font-bold">Whisper Meeting Transcriber</h1>
          </div>
          <div className="text-sm md:text-base flex items-center">
            <span className="mr-2">Powered by Deepgram AI</span>
            {currentUser && (
              <span className="bg-primary-700 px-2 py-1 rounded-md text-xs md:text-sm hidden sm:inline-block">
                {currentUser.username}
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
