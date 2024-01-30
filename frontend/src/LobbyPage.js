
import React, { useState, useEffect } from 'react';
import { useSocket } from './SocketContext';
import { Container, Typography, Button, TextField } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { URL } from './settings';


export default function LobbyPage() {
    const [openGames, setOpenGames] = useState([]);
    const [mapSize, setMapSize] = useState(7);
    const [username, setUsername] = useState(localStorage.getItem('username') || ''); // Retrieve from localStorage
    const socket = useSocket();
    const navigate = useNavigate();

    const fetchOpenGames = () => {
        fetch(`${URL}/api/open_games?username=${username}`)
            .then(response => response.json())
            .then(data => setOpenGames(data));
    }

    useEffect(() => {
        // Fetch decks and other initial setup
    
        // Set the userName in localStorage whenever it changes
        localStorage.setItem('username', username);
      }, [username]);

    const handleClickJoinButton = (game) => {
        const data = {
            username: username,
        }

        fetch(`${URL}/api/join_game/${game.id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        })
            .then(response => response.json())
            .then(data => {
                socket.emit('join', { room: data.game.id, username: username });
                navigate(`/game/${data.game.id}?playerNum=${data.player_num}`)
            });
    }

    useEffect(() => {
        socket.emit('join', { room: 'lobby', username: username });
        fetchOpenGames();
        socket.on('updateGames', () => {
          fetchOpenGames();
      })
    }, []);

    const hostGame = () => {
        const data = {
            username: username,
            map_size: mapSize,
        }


        fetch(`${URL}/api/host_game`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data), 
        })
            .then(response => response.json())
            .then(data => {
                socket.emit('join', { room: data.id, username: username });
                navigate(`/game/${data.id}?playerNum=0`)
            });
    }

    return (
        <Container>
            <Typography variant="h1">Lobby</Typography>
            <TextField label="Username" value={username} onChange={e => setUsername(e.target.value)} />
            <Typography variant="h2">Open Games</Typography>
            {openGames.map(game => (
                <>
                    <Button key={game.gameId} variant="contained" color="primary" disabled={!username} onClick={() => handleClickJoinButton(game)}>{username ? game.name : 'Enter username'}</Button>
                    <br />
                    <br />
                </>
            ))}
            <Button variant="contained" color="primary" disabled={!username} onClick={hostGame}>{username ? 'Host Game' : 'Enter username'}</Button>
        </Container>
    )
}