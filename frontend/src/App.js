import React from 'react';

import './App.css';
import LobbyPage from './LobbyPage';
import GamePage from './GamePage';
import ResetGamePage from './ResetGamePage';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import { SocketProvider } from './SocketContext';

export default function App() {
  return (
    <SocketProvider>
      <Router>
        <Routes>
          <Route exact path="/" element={<LobbyPage />} />
          <Route path="/game/:gameId" element={<GamePage />} />
          <Route path="/reset/" element={<ResetGamePage />} />
        </Routes>
      </Router>
    </SocketProvider>
  )
}
