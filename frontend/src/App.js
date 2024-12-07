import React from 'react';

import './App.css';
import { ThemeProvider } from '@mui/material/styles';
import LobbyPage from './LobbyPage';
import GamePage from './GamePage';
import ResetGamePage from './ResetGamePage';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import theme from './theme';
import { SocketProvider } from './SocketContext';

export default function App() {
  return (
    <SocketProvider>
      <ThemeProvider theme={theme}>
        <Router>
          <Routes>
            <Route exact path="/" element={<LobbyPage />} />
            <Route path="/game/:gameId" element={<GamePage />} />
            <Route path="/reset/" element={<ResetGamePage />} />
          </Routes>
        </Router>
      </ThemeProvider>
    </SocketProvider>
  )
}
