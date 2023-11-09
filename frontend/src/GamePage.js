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
import CityIcon from './images/city.svg';

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
    const [civTemplates, setCivTemplates] = useState({});

    console.log(civTemplates);

    useEffect(() => {
        fetch(`${URL}/api/civ_templates`)
            .then(response => response.json())
            .then(data => setCivTemplates(data));
    }, [])

    console.log(playersInGame);

    console.log(gameState);

    // const City = ({ primaryColor, secondaryColor }) => {
    //     return (
    //         <CityIcon fill={primaryColor} stroke={secondaryColor} strokeWidth="5" />
    //     );
    // };

    const City = ({ city }) => {
        const primaryColor = civTemplates[city.civ.name].primary_color
        const secondaryColor = civTemplates[city.civ.name].secondary_color
        const population = city.population

        return (
            // <svg version="1.0" xmlns="http://www.w3.org/2000/svg"
            //      width="4" height="4" viewBox="0 0 4 4"
            //      preserveAspectRatio="xMidYMid meet">
            //     <g transform="translate(0.000000,0.000000) scale(0.100000,-0.100000)"
            //        fill={primaryColor} stroke={secondaryColor}>
            //         <path d="M5893 12222 c-135 -474 -800 -2789 -849 -2959 -12 -40 -20 -53 -35
            //         -53 -10 0 -19 -7 -19 -15 0 -8 7 -15 15 -15 13 0 15 -153 15 -1320 0 -726 -4
            //         -1320 -8 -1320 -5 0 -276 246 -603 546 l-594 547 -3 78 -3 79 -50 0 -49 0 6
            //         43 c29 201 70 322 150 442 75 113 84 139 84 242 0 73 -39 315 -53 329 -2 2 -9
            //         -37 -15 -86 -23 -169 -66 -244 -138 -238 -35 3 -39 6 -36 28 2 14 10 44 19 67
            //         14 39 14 45 -1 68 -21 32 -76 35 -107 4 -23 -23 -22 -46 2 -127 16 -51 4 -66
            //         -46 -57 -62 11 -95 78 -138 285 l-13 65 -22 -92 c-57 -238 -52 -313 29 -456
            //         71 -123 103 -217 123 -366 23 -163 27 -151 -49 -151 l-65 0 0 -74 0 -74 -645
            //         -516 c-355 -284 -647 -516 -650 -516 -3 0 -5 601 -5 1335 l0 1335 -1050 0
            //         -1050 0 0 -1370 c0 -907 -3 -1370 -10 -1370 -6 0 -10 -136 -10 -389 0 -302 -3
            //         -391 -12 -395 -10 -5 -10 -7 0 -12 10 -5 12 -331 12 -1612 0 -884 0 -2171 0
            //         -2859 l0 -1253 3540 0 3540 0 2 1253 3 1252 40 6 40 5 -40 5 -40 4 -3 3314
            //         c-1 2314 1 3318 9 3327 7 9 6 15 -6 22 -16 8 -106 316 -800 2737 -131 457
            //         -241 833 -244 837 -3 4 -79 -248 -168 -560z"/>
            //     </g>
            // </svg>

            <svg width="2" height="2" viewBox="0 0 2 2" x={-1} y={-1}>
                <rect width="2" height="2" fill={primaryColor} stroke={secondaryColor} strokeWidth={0.5} />
                <text x="50%" y="56%" dominantBaseline="middle" textAnchor="middle" fontSize="0.1" fill="black">
                    {population}
                </text>                
            </svg>
        );
    };

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

    function greyOutHexColor(hexColor, targetGrey = '#777777') {
        // Convert hex to RGB
        function hexToRgb(hex) {
            var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
            return result ? {
                r: parseInt(result[1], 16),
                g: parseInt(result[2], 16),
                b: parseInt(result[3], 16)
            } : null;
        }
    
        // Convert RGB to hex
        function rgbToHex(r, g, b) {
            return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
        }
    
        // Blend two colors
        function blendColors(color1, color2, bias) {
            return {
                r: Math.floor((bias * color1.r + (1 - bias) * color2.r)),
                g: Math.floor((bias * color1.g + (1 - bias) * color2.g)),
                b: Math.floor((bias * color1.b + (1 - bias) * color2.b))
            };
        }
    
        const originalRgb = hexToRgb(hexColor);
        const greyRgb = hexToRgb(targetGrey);
    
        const blendedRgb = blendColors(originalRgb, greyRgb, 0.25);
    
        return rgbToHex(blendedRgb.r, blendedRgb.g, blendedRgb.b);
    }

    const hexStyle = (terrain, inFog) => {
        const terrainToColor = {
            'forest': '#228B22',
            'desert': '#FFFFAA',
            'plains': '#CBC553',
            'hills': '#9B9553',
            'mountain': '#8B4513',
            'grassland': '#AAFF77',
            'tundra': '#BBAABB',
            'jungle': '#00BB00',
            'marsh': '#00FFFF',
        }

        return { fill: inFog ? greyOutHexColor(terrainToColor[terrain], '#AAAAAA') : terrainToColor[terrain], fillOpacity: '0.8' }; // example color for forest
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
                                 cellStyle={hex.yields ? hexStyle(hex.terrain, false) : hexStyle(hex.terrain, true)} 
                                 onClick={() => console.log('hello')}>
                            {hex.yields ? <YieldImages yields={hex.yields} /> : null}
                            {hex.city && <City city={hex.city}/>}
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