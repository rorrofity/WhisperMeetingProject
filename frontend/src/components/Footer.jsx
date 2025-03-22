import React from 'react';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white py-4">
      <div className="container mx-auto px-4 text-center">
        <p className="text-sm">
          Whisper Meeting Transcriber &copy; {new Date().getFullYear()} | 
          Desarrollado con Whisper AI, React y FastAPI
        </p>
      </div>
    </footer>
  );
};

export default Footer;
