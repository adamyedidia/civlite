import React, {useState, useEffect} from 'react';

import { useSocket } from './SocketContext';
import { useParams, useLocation } from 'react-router-dom';
import { URL } from './settings';
import { Typography } from '@mui/material';

export default function GamePage() {

    const { gameId } = useParams();
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const socket = useSocket();

    const [username, setUsername] = useState(localStorage.getItem('username') || ''); // Retrieve from localStorage

    // parse as int if you can, otherwise set it to null
    const { playerNum } = queryParams.get('playerNum') ? { playerNum: parseInt(queryParams.get('playerNum')) } : { playerNum: null };

    const [gameState, setGameState] = useState(null);
    const [playersInGame, setPlayersInGame] = useState(null);
    const [turnNum, setTurnNum] = useState(0);
    const [frameNum, setFrameNum] = useState(0);

    console.log(playersInGame);

    const fetchGameState = () => {
        fetch(`${URL}/api/game_state/${gameId}?player_num=${playerNum}&turn_num=${turnNum}&frame_num=${frameNum}`)
            .then(response => response.json())
            .then(data => {

                if (data.game_state) {
                    setGameState(data.game_state);
                }
                if (data.players) {
                    setPlayersInGame(data.players);
                }
            });
    
    }

    useEffect(() => {
        socket.emit('join', { room: gameId, username: username });
        fetchGameState();
        socket.on('update', () => {
          console.log('update received')
          fetchGameState();
        })
    }, [])

    return (
        <div>
            <h1>Game Page</h1>
            {gameState ? 'Here is the game State!' : playersInGame ? (
                <>
                    <Typography variant="h5">Players in game:</Typography>
                    {playersInGame.map((playerUsername, i) => <Typography key={i}>{playerUsername}</Typography>)}
                </>
            ) : 'Loading...'}
        </div>
    )
}