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
import CivDisplay from './CivDisplay';
import CityIcon from './images/city.svg';
import TechDisplay from './TechDisplay';

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
    const [unitTemplates, setUnitTemplates] = useState(null);
    const [techTemplates, setTechTemplates] = useState(null);

    const [hoveredCiv, setHoveredCiv] = useState(null);

    const [hoveredCity, setHoveredCity] = useState(null);
    const [selectedCity, setSelectedCity] = useState(null);

    const [techChoices, setTechChoices] = useState(null);

    console.log(selectedCity);

    console.log(civTemplates);

    useEffect(() => {
        fetch(`${URL}/api/civ_templates`)
            .then(response => response.json())
            .then(data => setCivTemplates(data));

        fetch(`${URL}/api/unit_templates`)
            .then(response => response.json())
            .then(data => setUnitTemplates(data));
        
        fetch(`${URL}/api/tech_templates`)
            .then(response => response.json())
            .then(data => setTechTemplates(data));
    }, [])

    console.log(playersInGame);

    console.log(gameState);

    const isFriendlyCityHex = (hex) => {
        return isFriendlyCity(hex?.city);
    }

    const isFriendlyCity = (city) => {
        const playerNum = city?.civ?.game_player?.player_num;
        if (playerNum !== null && playerNum !== undefined) {
            return city.civ.game_player.player_num == playerNum
        }
        return false;
    }

    // const City = ({ primaryColor, secondaryColor }) => {
    //     return (
    //         <CityIcon fill={primaryColor} stroke={secondaryColor} strokeWidth="5" />
    //     );
    // };

    const handleMouseOverCity = (city) => {
        console.log('mousing over ')
        setHoveredCity(city);
    };

    const handleClickCity = (city) => {
        if (gameState.special_mode == 'starting_location') {
            const data = {
                player_num: playerNum,
                city_id: city.id,
            }
            fetch(`${URL}/api/starting_location/${gameId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
            }).then(response => response.json())
                .then(data => {
                    setTechChoices(data.tech_choices);
                });
        
        }
        setSelectedCity(city);
    };


    const City = ({ city, isHovered, isSelected }) => {
        const primaryColor = civTemplates[city.civ.name].primary_color;
        const secondaryColor = civTemplates[city.civ.name].secondary_color;
        const population = city.population;

        const pointer = isFriendlyCity(city);

    
        return (
            <>
                {isHovered && <circle cx="0" cy="0" r="1.5" fill="none" stroke="white" strokeWidth="0.2"/>}
                {isSelected && <circle cx="0" cy="0" r="1.5" fill="none" stroke="black" strokeWidth="0.2"/>}
                <svg width="2" height="2" viewBox="0 0 2 2" x={-1} y={-1} onMouseEnter={() => handleMouseOverCity(city)} onClick={() => handleClickCity(city)} style={{...(pointer ? {cursor : 'pointer'} : {})}}>
                    <rect width="2" height="2" fill={primaryColor} stroke={secondaryColor} strokeWidth={0.5} />
                    <text x="50%" y="56%" dominantBaseline="middle" textAnchor="middle" fontSize="0.1" fill="black">
                        {population}
                    </text>
                </svg>
            </>
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

    const hexStyle = (terrain, inFog, pointer) => {
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

        return { fill: inFog ? greyOutHexColor(terrainToColor[terrain], '#AAAAAA') : terrainToColor[terrain], fillOpacity: '0.8', ...(pointer ? {cursor: 'pointer'} : {})}; // example color for forest
    };

    const handleMouseLeaveHex = (hex) => {
    };

    const handleMouseOverHex = (hex) => {
        if (hex.city) {
            setHoveredCiv(civTemplates[hex.city.civ.name]);
        }
        else {
            setHoveredCiv(null);
            setHoveredCity(null);
        }
    };

    const handleClickHex = (hex) => {
        setHoveredCity(null);
        // setSelectedCity(null);
    };

    const displayGameState = (gameState) => {
        // return <Typography>{JSON.stringify(gameState)}</Typography>
        const hexagons = Object.values(gameState.hexes)
        return (
            <div className="basic-example">
                <h1>Basic example of HexGrid usage.</h1>
                <HexGrid width={2000} height={2000}>
                <Layout size={{ x: 3, y: 3 }}>
                    {hexagons.map((hex, i) => (
                        <Hexagon key={i} q={hex.q} r={hex.r} s={hex.s} 
                                 cellStyle={hex.yields ? hexStyle(hex.terrain, false) : hexStyle(hex.terrain, true)} 
                                 onClick={() => handleClickHex(hex)} 
                                 onMouseOver={() => handleMouseOverHex(hex)}
                                 onMouseLeave={() => handleMouseLeaveHex(hex)}>
                            {hex.yields ? <YieldImages yields={hex.yields} /> : null}
                            {hex.city && <City 
                                city={hex.city}
                                isHovered={hex?.city?.id === hoveredCity?.id}
                                isSelected={hex?.city?.id === selectedCity?.id}                                
                            />}
                        </Hexagon>
                    ))}
                </Layout>         
                </HexGrid>
                {hoveredCiv && <CivDisplay civ={hoveredCiv} />}
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

    if (!civTemplates || !unitTemplates || !techTemplates) {
        return (
            <div>
                <h1>Game Page</h1>
                <Typography variant="h5">Loading...</Typography>
            </div>
        )
    }

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
            {techChoices && (
                <div className="tech-choices-container">
                    {techChoices.map((tech, index) => (
                        <TechDisplay key={index} tech={tech} unitTemplates={unitTemplates} />
                    ))}
                </div>
            )}
        </div>
    )
}