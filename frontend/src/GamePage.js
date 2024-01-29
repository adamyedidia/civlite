import React, {useState, useEffect} from 'react';

import { HexGrid, Layout, Hexagon, Text, Pattern, Path, Hex, GridGenerator } from 'react-hexgrid';
import './GamePage.css';
import { Typography } from '@mui/material';
import { css } from '@emotion/react';
import { useSocket } from './SocketContext';
import { useParams, useLocation } from 'react-router-dom';
import { URL } from './settings';
import { Button } from '@mui/material';
import CivDisplay from './CivDisplay';
import CityIcon from './images/city.svg';
import TechDisplay from './TechDisplay';
import HexDisplay, { YieldImages } from './HexDisplay';
import CityDisplay from './CityDisplay';
import BuildingDisplay, { BriefBuildingDisplay, BriefBuildingDisplayTitle } from './BuildingDisplay';
import UnitDisplay, {BriefUnitDisplay, BriefUnitDisplayTitle} from './UnitDisplay';

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
    const [buildingTemplates, setBuildingTemplates] = useState(null);

    const unitTemplatesByBuildingName = {};
    Object.values(unitTemplates || {}).forEach(unitTemplate => {
        if (unitTemplate.building_name) {
            unitTemplatesByBuildingName[unitTemplate.building_name] = unitTemplate;
        }
    });

    const [hoveredCiv, setHoveredCiv] = useState(null);
    const [hoveredHex, setHoveredHex] = useState(null);

    const [hoveredUnit, setHoveredUnit] = useState(null);
    const [hoveredBuilding, setHoveredBuilding] = useState(null);

    const [hoveredCity, setHoveredCity] = useState(null);
    const [selectedCity, setSelectedCity] = useState(null);

    const [techChoices, setTechChoices] = useState(null);
    // const [selectedCityBuildingChoices, setSelectedCityBuildingChoices] = useState(null);


    const selectedCityBuildingChoices = selectedCity?.available_building_names;
    const selectedCityBuildingQueue = selectedCity?.buildings_queue;
    const selectedCityBuildings = selectedCity?.buildings;

    const selectedCityUnitChoices = selectedCity?.available_units;
    const selectedCityUnitQueue = selectedCity?.units_queue;

    const refreshSelectedCity = (newGameState) => {
        if (selectedCity?.id) {
            setSelectedCity(newGameState.hexes[selectedCity.hex].city);
        }
    }

    useEffect(() => {
        if (!!hoveredBuilding) {
            setHoveredUnit(null);
        }
    }, [!!hoveredBuilding])

    useEffect(() => {
        if (!!hoveredUnit) {
            setHoveredBuilding(null);
        }
    }, [!!hoveredUnit])

    const handleClickEndTurn = () => {
        const data = {
            player_num: playerNum,
        }

        fetch(`${URL}/api/end_turn/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify(data),
        }).then(response => response.json())
            .then(data => {
                if (data.game_state) {
                    // setGameState(data.game_state);
                }
            });
    }

    const handleClickBuildingChoice = (buildingName) => {
        const playerInput = {
            'building_name': (buildingName),
            'move_type': 'choose_building',
            'city_id': selectedCity.id,
        }

        const data = {
            player_num: playerNum,
            player_input: playerInput,
        }

        fetch(`${URL}/api/player_input/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        }).then(response => response.json())
            .then(data => {
                if (data.game_state) {
                    setGameState(data.game_state);
                    refreshSelectedCity(data.game_state);
                }
            });
    }

    const handleCancelBuilding = (buildingName) => {
        const playerInput = {
            'building_name': (buildingName),
            'move_type': 'cancel_building',
            'city_id': selectedCity.id,
        }

        const data = {
            player_num: playerNum,
            player_input: playerInput,
        }

        fetch(`${URL}/api/player_input/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        }).then(response => response.json())
            .then(data => {
                if (data.game_state) {
                    setGameState(data.game_state);
                    refreshSelectedCity(data.game_state);
                }
            });
    }

    const handleClickUnitChoice = (unitName) => {
        const playerInput = {
            'unit_name': (unitName),
            'move_type': 'choose_unit',
            'city_id': selectedCity.id,
        }

        const data = {
            player_num: playerNum,
            player_input: playerInput,
        }

        fetch(`${URL}/api/player_input/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        }).then(response => response.json())
            .then(data => {
                if (data.game_state) {
                    setGameState(data.game_state);
                    refreshSelectedCity(data.game_state);
                }
            });
    }

    const handleCancelUnit = (unitIndex) => {
        const playerInput = {
            'unit_index_in_queue': unitIndex,
            'move_type': 'cancel_unit',
            'city_id': selectedCity.id,
        }

        const data = {
            player_num: playerNum,
            player_input: playerInput,
        }

        fetch(`${URL}/api/player_input/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        }).then(response => response.json())
            .then(data => {
                if (data.game_state) {
                    setGameState(data.game_state);
                    refreshSelectedCity(data.game_state);
                }
            });
    }

    const handleClickTech = (tech) => {

        const playerInput = {
            'tech_name': tech.name,
            'move_type': 'choose_tech',
        }

        const data = {
            player_num: playerNum,
            player_input: playerInput,
        }
        fetch(`${URL}/api/player_input/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        }).then(response => response.json())
            .then(data => {
                if (data.game_state) {
                    setGameState(data.game_state);
                    setTechChoices(null);
                }
            });
    }

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

        fetch(`${URL}/api/building_templates`)
            .then(response => response.json())
            .then(data => setBuildingTemplates(data));
    }, [])


    // useEffect(() => {
    //     if (selectedCity?.id) {
    //         fetch(`${URL}/api/building_choices/${gameId}/${selectedCity?.id}`).then(response => response.json()).then(data => {
    //             setSelectedCityBuildingChoices(data.building_choices);
    //         });
    //     }
    // }, [selectedCity?.id])

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
        setHoveredCity(city);
    };

    const handleClickCity = (city) => {
        if (gameState.special_mode_by_player_num[playerNum] == 'starting_location') {
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
                    if (data.game_state) {
                        setGameState(data.game_state);
                    }
                });
        
        }
        setSelectedCity(city);
    };


    const City = ({ city, isHovered, isSelected, isUnitInHex }) => {
        const primaryColor = civTemplates[city.civ.name]?.primary_color;
        const secondaryColor = civTemplates[city.civ.name]?.secondary_color;
        const population = city.population;

        const pointer = isFriendlyCity(city);

    
        return (
            <>
                {isHovered && <circle cx="0" cy={`${isUnitInHex ? -1 : 0}`} r="2.25" fill="none" stroke="white" strokeWidth="0.2"/>}
                {isSelected && <circle cx="0" cy={`${isUnitInHex ? -1 : 0}`} r="2.25" fill="none" stroke="black" strokeWidth="0.2"/>}
                <svg width="3" height="3" viewBox="0 0 3 3" x={-1.5} y={isUnitInHex ? -2.5 : -1.5} onMouseEnter={() => handleMouseOverCity(city)} onClick={() => handleClickCity(city)} style={{...(pointer ? {cursor : 'pointer'} : {})}}>
                    <rect width="3" height="3" fill={primaryColor} stroke={secondaryColor} strokeWidth={0.5} />
                    <text x="50%" y="56%" dominantBaseline="middle" textAnchor="middle" fontSize="0.1" fill="white">
                        {population}
                    </text>
                </svg>
            </>
        );
    };

    const Unit = ({ unit, isCityInHex }) => {
        const primaryColor = civTemplates[unit.civ.name]?.primary_color;
        const secondaryColor = civTemplates[unit.civ.name]?.secondary_color;
        const unitImage = `/images/${unit.name}.svg`; // Path to the unit SVG image
    
        const scale = isCityInHex ? 0.95 : 1.4;
        const healthPercentage = unit.health / 100; // Calculate health as a percentage
        const healthBarColor = unit.health > 50 ? '#00ff00' : '#ff0000'; // Set color based on health
    
        return (
            <svg width={`${4*scale}`} height={`${4*scale}`} viewBox={`0 0 ${4*scale} ${4*scale}`} x={-2*scale} y={-2*scale + (isCityInHex ? 1 : 0)}>
                <circle cx={`${2*scale}`} cy={`${2*scale}`} r={`${scale}`} fill={primaryColor} stroke={secondaryColor} strokeWidth={0.5} />
                <image href={unitImage} x={`${scale}`} y={`${scale}`} height={`${2*scale}`} width={`${2*scale}`} fill={primaryColor} stroke={secondaryColor} />
                <rect x={`${scale}`} y={`${3.4*scale}`} width={`${2*scale}`} height={`${0.2*scale}`} fill="#ff0000" /> {/* Total health bar */}
                <rect x={`${scale}`} y={`${3.4*scale}`} width={`${2*scale*healthPercentage}`} height={`${0.2*scale}`} fill="#00ff00" /> {/* Current health bar */}
            </svg>          
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
        setHoveredHex(hex);
        if (hex.city) {
            setHoveredCiv(civTemplates[hex.city.civ.name]);
        }
        if (hex?.units?.length > 0) {
            setHoveredUnit(hex?.units?.[0]);
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
                <HexGrid width={2000} height={2000}>
                <Layout size={{ x: 3, y: 3 }}>
                    {hexagons.map((hex, i) => {
                        console.log(hex);
                        return (
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
                                    isUnitInHex={hex?.units?.length > 0}                              
                                />}
                                {hex?.units?.length > 0 && <Unit
                                    unit={hex.units[0]}
                                    isCityInHex={hex?.city}
                                />}
                            </Hexagon>
                        );
                    })}
                </Layout>         
                </HexGrid>
                {hoveredCiv && <CivDisplay civ={hoveredCiv} />}
                {hoveredHex && (
                    <HexDisplay hoveredHex={hoveredHex} unitTemplates={unitTemplates} />
                )}
                {selectedCity && <CityDisplay city={selectedCity} setHoveredUnit={setHoveredUnit} />}
                {selectedCityBuildingChoices && (
                    <div className="building-choices-container">
                        <BriefBuildingDisplayTitle title="Building Choices" />
                        {selectedCityBuildingChoices.map((buildingName, index) => (
                            <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} onClick={() => handleClickBuildingChoice(buildingName)} />
                        ))}
                    </div>
                )};
                {selectedCityBuildingQueue && (
                    <div className="building-queue-container">
                        <BriefBuildingDisplayTitle title="Building Queue" />
                        {selectedCityBuildingQueue.map((buildingName, index) => (
                            <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} onClick={() => handleCancelBuilding(buildingName)}/>
                        ))}
                    </div>
                )};                
                {selectedCityBuildings && (
                    <div className="existing-buildings-container">
                        <BriefBuildingDisplayTitle title="Existing buildings" />
                        {selectedCityBuildings.map((buildingName, index) => (
                            <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} />
                        ))}
                    </div>
                )};  
                {selectedCityUnitChoices && (
                    <div className="unit-choices-container">
                        <BriefUnitDisplayTitle title="Unit Choices" />
                        {selectedCityUnitChoices.map((unitName, index) => (
                            <BriefUnitDisplay key={index} unitName={unitName} unitTemplates={unitTemplates} setHoveredUnit={setHoveredUnit} onClick={() => handleClickUnitChoice(unitName)} />
                        ))}
                    </div>
                )};
                {selectedCityUnitQueue && (
                    <div className="unit-queue-container">
                        <BriefUnitDisplayTitle title="Unit Queue" />
                        {selectedCityUnitQueue.map((unitName, index) => (
                            <BriefUnitDisplay key={index} unitName={unitName} unitTemplates={unitTemplates} setHoveredUnit={setHoveredUnit} onClick={() => handleCancelUnit(index)}/>
                        ))}
                    </div>
                )};                  
                <div style={{position: 'fixed', top: '10px', left: '50%', transform: 'translate(-50%, 0%)'}}>                             
                    {hoveredBuilding && (
                        <BuildingDisplay buildingName={hoveredBuilding} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} />
                    )}
                    {hoveredUnit && (
                        <UnitDisplay unit={unitTemplates[hoveredUnit]} />
                    )}                
                </div>
                <Button 
                    style={{
                        position: 'fixed', 
                        bottom: '10px', 
                        left: '50%', 
                        transform: 'translate(-50%, 0%)', 
                        backgroundColor: "#cccc88",
                        color: "black",
                        padding: '10px 20px', // Increase padding for larger button
                        fontSize: '1.5em' // Increase font size for larger text
                    }} 
                    variant="contained"
                    onClick={handleClickEndTurn}
                >
                    End turn
                </Button>
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
                    getMovie();
                }
                if (data.players) {
                    setPlayersInGame(data.players);
                }
            });
    
    }

    const getMovie = () => {
        fetch(`${URL}/api/movie/${gameId}?player_num=${playerNum}`)
            .then(response => response.json())
            .then(data => {
                if (data.animation_frames) {
                    // setGameState(data.game_state);
                    // Set it to the last animation frame
                    setFrameNum(data.animation_frames.length - 1);
                    setGameState(data.animation_frames[data.animation_frames.length - 1]);
                }
                if (data.turn_num) {
                    setTurnNum(data.turn_num);
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
          getMovie();
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
            {gameState ? null : playersInGame ? (
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
                        <TechDisplay key={index} tech={tech} unitTemplates={unitTemplates} onClick={() => handleClickTech(tech)} />
                    ))}
                </div>
            )}
        </div>
    )
}