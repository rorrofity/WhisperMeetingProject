import React from 'react';
import { FiHeadphones } from 'react-icons/fi';

const Header = () => {
  return (
    <header className="bg-primary-600 text-white shadow-md">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <FiHeadphones className="text-3xl mr-2" />
            <h1 className="text-xl md:text-2xl font-bold">Whisper Meeting Transcriber</h1>
          </div>
          <div className="text-sm md:text-base">
            Powered by Whisper AI
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
