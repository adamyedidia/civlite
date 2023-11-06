// SocketContext.js
import React, { createContext, useContext } from 'react';
import socket from './Socket'; // Import the socket from your Socket.js module

const SocketContext = createContext();

export const useSocket = () => {
  return useContext(SocketContext);
};

export const SocketProvider = ({ children }) => {
  return (
    <SocketContext.Provider value={socket}>
      {children}
    </SocketContext.Provider>
  );
};
