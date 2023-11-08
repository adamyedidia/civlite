import React, {useState, useEffect} from 'react';

import { HexGrid, Layout, Hexagon, Text, Pattern, Path, Hex, GridGenerator } from 'react-hexgrid';
import './GamePage.css';
import { Typography } from '@mui/material';
import { css } from '@emotion/react';
import { useSocket } from './SocketContext';
import { useParams, useLocation } from 'react-router-dom';
import { URL } from './settings';
import { Button } from '@mui/material';
import foodImg from './images/food.png';
import woodImg from './images/wood.png';
import metalImg from './images/metal.png';
import scienceImg from './images/science.png';

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
    const [turnNum, setTurnNum] = useState(1);
    const [frameNum, setFrameNum] = useState(0);

    console.log(playersInGame);

    console.log(gameState);

    const YieldImages = ({ yields }) => {
        let imageCounter = 0; // Counter to track the total number of images

        let totalCount = yields.food + yields.wood + yields.metal + yields.science;
    
        const renderImages = (img, count) => {
            let images = [];
            for (let i = 0; i < count; i++) {
                images.push(
                    <image 
                        key={`${img}-${imageCounter}`} 
                        href={img} 
                        x={(1.5 * (imageCounter * (totalCount / (totalCount - 1)) + 0.1) - totalCount * 1.5) / (totalCount * 0.7)} 
                        y={-1} 
                        height={2} 
                        width={2}
                    />
                );
                imageCounter++; // Increment counter for each image
            }
            return images;
        };
    
        return (
            <g>
                {renderImages(foodImg, yields.food)}
                {renderImages(woodImg, yields.wood)}
                {renderImages(metalImg, yields.metal)}
                {renderImages(scienceImg, yields.science)}
            </g>
        );
    };
    const hexStyle = (terrain) => {
        switch (terrain) {
            case 'forest':
                return { fill: '#228B22', fillOpacity: '0.8' }; // example color for forest
            case 'desert':
                return { fill: '#FFFFAA', fillOpacity: '0.8' }; // example color for desert
            case 'plains': 
                return { fill: '#CBC553', fillOpacity: '0.8' }; // example color for plains CB9553
            case 'hills': 
                return { fill: '#9B9553', fillOpacity: '0.8' }; // example color for plains                
            case 'mountain':
                return { fill: '#8B4513', fillOpacity: '0.8' }; // example color for mountain
            case 'grassland':
                return { fill: '#AAFF77', fillOpacity: '0.8' }; // example color for grassland
            case 'tundra':
                return { fill: '#BBAABB', fillOpacity: '0.8' }; // example color for tundra
            case 'jungle': 
                return { fill: '#00BB00', fillOpacity: '0.8' }; // example color for jungle
            case 'marsh':
                return { fill: '#00FFFF', fillOpacity: '0.8' }; // example color for marsh
            // Add more cases for different terrains
            default:
                return { fill: '#f0f0f0', fillOpacity: '0.6' }; // default color
        }
    };

    const displayGameState = (gameState) => {
        // return <Typography>{JSON.stringify(gameState)}</Typography>
        const hexagons = Object.values(gameState.hexes)
        return (
            <div className="basic-example">
                <h1>Basic example of HexGrid usage.</h1>
                <HexGrid width={5000} height={5000}>
                <Layout size={{ x: 3, y: 3 }}>
                    {hexagons.map((hex, i) => (
                        <Hexagon key={i} q={hex.q} r={hex.r} s={hex.s} 
                                 cellStyle={hexStyle(hex.terrain)} 
                                 onClick={() => console.log('hello')}>
                            <YieldImages yields={hex.yields} />
                        </Hexagon>
                    ))}
                </Layout>
                <Pattern id="pat-1" link="http://cat-picture" />
                <Pattern id="pat-2" link="http://cat-picture2" />                
                </HexGrid>
            </div>
        )
    }

    const launchGame = () => {
        const data = {
            username: username,
        }

        fetch(`${URL}/api/launch_game/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        })
    }

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
            {gameState ? displayGameState(gameState) : (
                <Button onClick={launchGame}>Launch Game</Button>
            )}
        </div>
    )
}