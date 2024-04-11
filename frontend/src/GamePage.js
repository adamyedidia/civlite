import React, {useState, useEffect} from 'react';

import { HexGrid, Layout, Hexagon } from 'react-hexgrid';
import './arrow.css';
import './GamePage.css';
import { Typography, IconButton } from '@mui/material';
import { useSocket } from './SocketContext';
import { useParams, useLocation } from 'react-router-dom';
import { URL } from './settings';
import { 
    Button, 
    Dialog, 
    DialogTitle, 
    DialogContent, 
    DialogContentText,
    DialogActions,
    Grid,
    Select,
    MenuItem,
} from '@mui/material';
import EngineStates from './EngineStates';
import CivDisplay from './CivDisplay';
import TechDisplay from './TechDisplay';
import HexDisplay, { YieldImages } from './HexDisplay';
import BuildingDisplay from './BuildingDisplay';
import UnitDisplay from './UnitDisplay';
import CityDetailWindow from './CityDetailWindow';
import UpperRightDisplay from './UpperRightDisplay';
import LowerRightDisplay from './LowerRightDisplay.js';
import TechListDialog from './TechListDialog';
import TaskBar from './TaskBar';
import GreatPerson from './GreatPerson';
import { romanNumeral } from './TechListDialog';
import moveSound from './sounds/movement.mp3';
import meleeAttackSound from './sounds/melee_attack.mp3';
import rangedAttackSound from './sounds/ranged_attack.mp3';
import medievalCitySound from './sounds/medieval_city.mp3';
import modernCitySound from './sounds/modern_city.mp3';
import gunpowderMeleeAttackSound from './sounds/gunpowder_melee.mp3';
import gunpowderRangedAttackSound from './sounds/gunpowder_ranged.mp3';
import SettingsDialog from './SettingsDialog';
import workerIcon from './images/worker.png';
import vpImage from './images/crown.png';
import vitalityImg from './images/heart.png';
import { lowercaseAndReplaceSpacesWithUnderscores } from './lowercaseAndReplaceSpacesWithUnderscores';

const coordsToObject = (coords) => {
    if (!coords) {
        return null;
    }
    const [q, r, s] = coords.split(',').map(coord => parseInt(coord));
    return {q: q, r: r, s: s};
}

const MIN_ANIMATION_DELAY = 100;
const MAX_ANIMATION_DELAY = 300;

const now = () => {
    const now = new Date();
    return `${now.getHours()}:${now.getMinutes()}:${now.getSeconds()}.${now.getMilliseconds()}`;
}

let userHasInteracted = false;

window.addEventListener('click', () => {
    userHasInteracted = true;
});


function RulesDialog({open, onClose, gameConstants}) {
    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>Rules</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    Civlite is a turn-based strategy game. On the first turn of the game, you choose your starting city and civilization from three options. Afterwards, you 
                    queue up units and buildings at your cities and choose technologies from among three options.
                </DialogContentText>
                <br />
                <DialogContentText>
                    <b>Resources</b>
                </DialogContentText>
                <DialogContentText>
                    The game has four resources: food, wood, metal, and science. Food is used to grow your cities. Your city automatically grows after it collects food; growing 
                    a population costs {gameConstants?.base_food_cost_of_pop} food + {gameConstants?.additional_per_pop_food_cost} per current population. Metal is used to build units.
                    Every unit in the game (except Warriors) require a building a production building before you can build them in the city. Wood is used to build buildings.
                    There are a few kinds of buildings: unit production buildings do nothing, except for unlock the ability to build their corresponding unit in a single city. Wonders 
                    can be built only once in the game. National wonders can be built once per civilization. Science is used to research technologies, which unlock more units and buildings.
                    Science is shared across your civilization, but food, metal, and wood are stored in each city. In general, everything is infinitely stockpilable; if you fail to put anything
                    in your queue, there's no penalty and you can just accumulate more resources and spend them later. Putting something in your queue doesn't have any effect until you 
                    actually accumulate enough resources to build it, at which point it will be built and removed from your queue.
                </DialogContentText>
                <DialogContentText>
                    You collect food, wood, metal, and science yields from two sources: the hexes around your cities, and the city's population. Your cities always collect yields from 
                    the seven hexes that are adjacent to or underneath them. Also, each population in each of your cities collects 1 science + 1 yield of your choice (the "focus" of your city).
                    Certain buildings and civ abilities can enhance the yields of hexes; when you enhance the yield of a hex, that hex's yields are increased permanently, and the enhancement
                    applies to other cities working that hex as well.
                </DialogContentText>
                <br />
                <DialogContentText>
                    <b>Founding cities</b>
                </DialogContentText>
                <DialogContentText>
                    There's another resource, called "city power", which you collect passively; your city power income is equal to {gameConstants?.base_city_power_income} plus the 
                    total food income across all your cities. Cities passively make 2 food. When you have enough city power, you can found a new city. Founding a new city costs 100 city power.
                    You can only found cities on hexes that satisfy all of the following properties:
                    <ul>
                        <li>There is a friendly unit on the hex</li>
                        <li>The hex is not adjacent to any other city</li>
                        <li>The hex is not adjacent to any enemy units</li>
                        <li>The hex is not adjacent to any barbarian camps</li>
                    </ul>
                    When you found a new city, you spend 100 of your city power. You get {gameConstants.camp_clear_city_power_reward} city power for clearing a barbarian camp.
                </DialogContentText>
                <br />
                <DialogContentText>
                    <b>Civ vitality</b>
                </DialogContentText>
                <DialogContentText>
                    Your civilization has a "vitality" statistic, which starts out high and then declines over time. Your civilization's starting vitality is equal 200% plus another 10% 
                    per turn since the start of the game. Vitality decays exponentially at a rate of x{gameConstants.fast_vitality_decay_rate} per turn when it's above 100%, and by{' '}
                    x{gameConstants.vitality_decay_rate} per turn when it's below 100%. Vitality is a multiplier that gets applied to your income of all resources in all your cities. 
                </DialogContentText>
                <br />
                <DialogContentText>
                    <b>Entering decline</b>
                </DialogContentText>
                <DialogContentText>
                    When your civilization's vitality has fallen too low, or things have started going badly for you, you can choose to have your civilization "enter decline." When this happens,
                    a bot takes over your current civilization, and you start a new civilization somewhere else. The way this works is that your presented with three options for new civilizations to found, in 
                    three different cities where you can found them. The city you take over might be an already-existing city on the map that belongs to a different player. If you choose such a city as your starting city, 
                    that city will "revolt": you'll take over that city, and all units adjacent to that city, and the player who previously owned the city and units will be compensated with victory points. 
                    Whatever city you choose will be your new capital. Your new civilization will start with a high vitality (200% + 10% per turn since the start of the game). 
                    If you don't like your three civ choices, you can end your turn and "mulligan" your three choices; each time you do that, you'll lose {gameConstants.mulligan_penalty} VP.
                    You'll also start with some technologies, corresponding
                    to the median player-controlled civilization's techs. When you enter decline and start a new civilization, you are starting over from scratch, and leaving literally everything behind 
                    with just one exception: your victory points.
                </DialogContentText>
                <br />
                <DialogContentText>
                    <b>Victory points</b>
                </DialogContentText>
                <DialogContentText>
                    The goal of the game is to get to the most victory points, and your victory points are held by you, the player. The game ends when someone reaches a sufficiently high score, which is given by {gameConstants.game_end_score} VPs + {gameConstants.extra_game_end_score_per_player} VPs per player. 
                    (So, for example, in a 4-player game, the game ends at {gameConstants.game_end_score + 4*gameConstants.extra_game_end_score_per_player} VPs.)
                    You get VPs from a variety of sources:
                    <ul>
                        <li>{gameConstants.unit_kill_reward} VP per unit killed</li>
                        <li>{gameConstants.city_capture_reward} VP per city captured that wasn't previously controlled by you</li>
                        <li>{gameConstants.camp_clear_reward} VP per barbarian camp cleared</li>
                        <li>{gameConstants.tech_vp_reward} VP per tech researched</li>
                        <li>Some buildings give you VPs for building them (almost all wonders give 5 VP, and a few basic buildings give you 1 VP and have no other abilities)</li>
                        <li>Whenever a player enters decline, all other players get {gameConstants.survival_bonus} VP</li>
                        <li>When a player's city "revolts" and becomes part of a new player's civilization, that player is compensated with a pile of victory points; 5 VP + 1 VP per (between 5 and 20ish depending on turn number) city base yields + 1 VP per unit stolen</li>
                    </ul>
                </DialogContentText>
                <br />
                <DialogContentText>
                    <b>Unit movement and combat</b>
                </DialogContentText>
                <DialogContentText>
                    You don't have fine-grained control over your units in this game. Instead, you set two "targets" on the map, repesented by flags. Your units will attack-move to those flags, and choose whichever of the two
                    is closer. If a unit is adjacent to an enemy unit, it will attack that unit. When two units fight, they each deal damage to the other according to a complicated function of their respective strengths, meant to 
                    approximately imitate what would happen in Civ 5 or other games with this system. Ranged units don't take damage back when they attack. If you occupy an enemy city or a camp, that city or camp is now "under siege"
                    (and will appear as on fire); if you then occupy it for a second turn in a row, you'll capture the city or clear the camp. Cities don't take any damage or population loss from being captured. Barbarian camps spawn a 
                    Warrior unit every other turn.
                </DialogContentText>
            </DialogContent>

            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Close
                </Button>
            </DialogActions>
        </Dialog>
    )
}

function GameOverDialog({open, onClose, gameState}) {
    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>
                <Typography variant="h2" component="div">  
                    {/* component="div" removes an html error complaining of nested h2s */}
                    Game over
                </Typography>
            </DialogTitle>
            <DialogContent>
                <Grid container direction="column" spacing={2}>
                    {Object.values(gameState?.game_player_by_player_num).map((gamePlayer) => {
                        return (
                            <Grid item key={gamePlayer.player_num}>
                                <Typography variant="h5">{gamePlayer.username}</Typography>
                                <Typography>Score: {gamePlayer.score}</Typography>
                            </Grid>
                        )
                    })}
                </Grid>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Close
                </Button>
            </DialogActions>
        </Dialog>
    )
}

function GreatPersonChoiceDialog({open, onClose, greatPersonChoices, handleSelectGreatPerson, setHoveredUnit, setHoveredTech, templates}) {
    return <div className="tech-choices-container">
        <DialogTitle>
            <Typography variant="h5" component="div" style={{ flexGrow: 1, textAlign: 'center' }}>
                Choose Great Person
            </Typography>
            <IconButton
                aria-label="close"
                onClick={onClose}
                style={{
                    position: 'absolute',
                    right: 8,
                    top: 8,
                    color: (theme) => theme.palette.grey[500],
                }}
                color="primary"
            >
                Minimize
            </IconButton>
        </DialogTitle>
        <div className="tech-choices-content">
            {greatPersonChoices.map((person, index) => (
                <GreatPerson key={index} greatPerson={person} handleSelectGreatPerson={handleSelectGreatPerson} 
                    setHoveredUnit={setHoveredUnit} setHoveredTech={setHoveredTech} templates={templates}/>
            ))}
        </div>
    </div>
}

function DeclineFailedDialog({open, onClose}) {
    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>
                <Typography variant="h2" component="div">  
                   Decline Failed
                </Typography>
            </DialogTitle>
            <DialogContent>
                <DialogContentText>
                    Another player has already declined to this city. They have lower score than you, so they get it. Sorry.
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Close
                </Button>
            </DialogActions>
        </Dialog>
    )
}

function DeclinePreemptedDialog({open, onClose}) {
    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>
                <Typography variant="h2" component="div">  
                   Decline Preempted
                </Typography>
            </DialogTitle>
            <DialogContent>
                <DialogContentText>
                    Another player with lower score has chosen this decline option this turn.
                </DialogContentText>
                <DialogContentText>
                    You will be put back into your prior civ.
                </DialogContentText>
                <DialogContentText>
                    You can continue or choose another decline option.
                </DialogContentText>
                <DialogContentText>
                    There is no timer this turn so you can decide.
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Close
                </Button>
            </DialogActions>
        </Dialog>
    )
}

const generateUniqueId = () => {
    return Math.random().toString(36).substring(2);
}

const ChooseCapitalButton = ({playerNum, isOvertime, myGamePlayer, selectedCity, nonDeclineViewGameState, engineState, handleFoundCapital, civsById}) => {
    const isMyCity = nonDeclineViewGameState?.cities_by_id[selectedCity.id] && civsById[nonDeclineViewGameState?.cities_by_id[selectedCity.id].civ_id]?.game_player?.player_num === playerNum;
    const disabledMsg = isMyCity ? "Can't decline to my own city" 
            : myGamePlayer?.decline_this_turn ? "Already declined this turn"
            : (isOvertime && !myGamePlayer?.failed_to_decline_this_turn) ? "Can't decline in overtime"
            : null;
    const content = disabledMsg ? disabledMsg : `Make ${selectedCity.name} my capital`;
    const disabled = engineState !== EngineStates.PLAYING || disabledMsg !== null;
    return <Button
        style={{
            backgroundColor: disabled ? "#aaaaaa" : "#ccffaa",
            color: "black",
            marginLeft: '20px',
            padding: '10px 20px', // Increase padding for larger button
            fontSize: '1.5em', // Increase font size for larger text
            marginBottom: '10px',
        }} 
        variant="contained"
        onClick={() => handleFoundCapital()}
        disabled={disabled}
    >
        {content}
    </Button>
}

export default function GamePage() {
    const { gameId } = useParams();
    const location = useLocation();
    const queryParams = new URLSearchParams(location.search);
    const socket = useSocket();

    const [username, setUsername] = useState(localStorage.getItem('username') || ''); // Retrieve from localStorage

    // parse as int if you can, otherwise set it to null
    const { playerNum } = queryParams.get('playerNum') ? { playerNum: parseInt(queryParams.get('playerNum')) } : { playerNum: null };

    const [gameState, setGameState] = useState(null);

    const [engineState, setEngineState] = useState(EngineStates.PLAYING);
    // Ref to keep track of the current engineState
    const engineStateRef = React.useRef(engineState);

    const [timerStatus, setTimerStatus] = useState(null);

    const [overtimeDeclineCivs, setOvertimeDeclineCivs] = useState(null);

    const animationFrameLastPlayedRef = React.useRef(0);

    const [animationTotalFrames, setAnimationTotalFrames] = useState(null);
    const animationFinalStateRef = React.useRef(null);
    const [animationActiveDelay, setAnimationActiveDelay] = useState(null);
    const animationsLastStartedAtRef = React.useRef(null);

    const [playersInGame, setPlayersInGame] = useState(null);
    const [nextForcedRollAt, setNextForcedRollAt] = useState(null);

    const [templates, setTemplates] = useState(null);
    const [volume, setVolume] = useState(100);
    const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);

    const unitTemplatesByBuildingName = {};
    Object.values(templates?.UNITS || {}).forEach(unitTemplate => {
        if (unitTemplate.building_name) {
            unitTemplatesByBuildingName[unitTemplate.building_name] = unitTemplate;
        }
    });

    const [hoveredCiv, setHoveredCiv] = useState(null);
    const [hoveredGamePlayer, setHoveredGamePlayer] = useState(null);
    const [hoveredHex, setHoveredHex] = useState(null);

    const [hoveredUnit, setHoveredUnit] = useState(null);
    const [hoveredBuilding, setHoveredBuilding] = useState(null);
    const [hoveredTech, setHoveredTech] = useState(null);

    const [hoveredCity, setHoveredCity] = useState(null);

    const [showFlagArrows, setShowFlagArrows] = useState(false);
    const flagArrowsTimeoutRef = React.useRef(null);

    const [selectedCity, setSelectedCity] = useState(null);

    const [techChoiceDialogOpen, setTechChoiceDialogOpen] = useState(false);
    const [greatPersonChoiceDialogOpen, setGreatPersonChoiceDialogOpen] = useState(false);

    const [lastSetPrimaryTarget, setLastSetPrimaryTarget] = useState(false);

    // TODO(dfarhi) combine thes flags into one state flag rather than several bools.
    const [foundingCity, setFoundingCity] = useState(false);
    const [declineOptionsView, setDeclineOptionsView] = useState(false);

    const [declineViewGameState, setDeclineViewGameState] = useState(null);
    const [nonDeclineViewGameState, setNonDeclineViewGameState] = useState(null);  // My real game state, for if I cancel decline view

    const [techListDialogOpen, setTechListDialogOpen] = useState(false);

    const [gameConstants, setGameConstants] = useState(null);

    const [rulesDialogOpen, setRulesDialogOpen] = useState(false);
    const [declinePreemptedDialogOpen, setDeclinePreemptedDialogOpen] = useState(false);
    const [declineFailedDialogOpen, setDeclineFailedDialogOpen] = useState(false);

    const [turnTimer, setTurnTimer] = useState(-1);

    const [turnEndedByPlayerNum, setTurnEndedByPlayerNum] = useState({});
    const [gameOverDialogOpen, setGameOverDialogOpen] = useState(false);

    const gameStateExistsRef = React.useRef(false);
    const firstRenderRef = React.useRef(true);

    const getMyInfo = (gameState) => {
        const gamePlayer = gameState?.game_player_by_player_num?.[playerNum];
        const myCivId = gamePlayer?.civ_id;
        const myCiv = gameState?.civs_by_id?.[myCivId];
        return {gamePlayer, myCivId, myCiv};
    }
    const mainGameState = declineOptionsView ? nonDeclineViewGameState : gameState;
    const info = getMyInfo(mainGameState);
    const myGamePlayer = info.gamePlayer;
    const myCivId = info.myCivId;
    const myCiv = info.myCiv;

    const techChoices = myCiv?.current_tech_choices;

    const civsById = gameState?.civs_by_id;

    const myCities = Object.values(mainGameState?.cities_by_id || {}).filter(city => civsById?.[city.civ_id]?.game_player?.player_num === myGamePlayer?.player_num);
    const myTerritoryCapitals = myCities.filter(city => city.territory_parent_coords === null);
    const myUnits = Object.values(mainGameState?.hexes || {})
        .filter(hex => hex.units?.length > 0 && civsById?.[hex.units[0].civ_id]?.game_player?.player_num === myGamePlayer?.player_num)
        .map(hex => hex.units[0])

    const target1 = coordsToObject(myCiv?.target1);
    const target2 = coordsToObject(myCiv?.target2);

    const myCivIdRef = React.useRef(myCivId);
    const hoveredHexRef = React.useRef(hoveredHex);
    const civsByIdRef = React.useRef(civsById);
    const lastSetPrimaryTargetRef = React.useRef(lastSetPrimaryTarget);
    const playerApiUrl= `${URL}/api/player_input/${gameId}`
    const target1Ref = React.useRef(target1);
    const target2Ref = React.useRef(target2);
    const playerNumRef = React.useRef(playerNum);
    const gameStateRef = React.useRef(gameState);
    const turnEndedByPlayerNumRef = React.useRef(turnEndedByPlayerNum);

    useEffect(() => {
        hoveredHexRef.current = hoveredHex;
    }, [hoveredHex]);

    useEffect(() => {
        lastSetPrimaryTargetRef.current = lastSetPrimaryTarget;
    }, [lastSetPrimaryTarget]);

    useEffect(() => {
        target1Ref.current = target1;
    }, [target1]);

    useEffect(() => {
        target2Ref.current = target2;
    }, [target2]);

    useEffect(() => {
        myCivIdRef.current = myCivId;
    }, [myCivId]);

    useEffect(() => {
        civsByIdRef.current = civsById;
    }, [civsById])

    useEffect(() => {
        playerNumRef.current = playerNum;
    }, [playerNum]);

    useEffect(() => {
        gameStateRef.current = gameState;
    }, [gameState]);

    useEffect(() => {
        turnEndedByPlayerNumRef.current = turnEndedByPlayerNum;
    }, [turnEndedByPlayerNum]);

    useEffect(() => {
        if (gameState?.game_over) {
            transitionEngineState(EngineStates.GAME_OVER);
            setGameOverDialogOpen(true);
        }
    }, [gameState?.game_over]);

    useEffect(() => {
        engineStateRef.current = engineState;
    }, [engineState]);

    const transitionEngineState = (newState, oldState) => {
        if (oldState && engineStateRef.current !== oldState) {
            console.error(`Tried to transition from ${oldState} to ${newState} but engine state is ${engineStateRef.current}`);
            return;
        }
        setEngineState(newState);
    }

    // For testing that my backend stuff actually works

    // useEffect(() => {
    //     fetch(`${URL}/api/decline_view/${gameId}`, {
    //         method: 'GET',
    //         headers: {
    //             'Content-Type': 'application/json'
    //         },
    //     }).then(response => response.json())
    //         .then(data => {
    //             console.log(data);
    //             setGameState(data.game_state);
    //         });
    // }, [rulesDialogOpen])

    // console.log(selectedCity);

    // console.log(hoveredHex);

    useEffect(() => {
        // When the user presses escape
        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                setSelectedCity(null);
                setFoundingCity(false);
                setShowFlagArrows(false);
                setTechChoiceDialogOpen(false);
                setGreatPersonChoiceDialogOpen(false);
                setDeclineOptionsView(false);
            }
        };
    
        // Add event listener
        window.addEventListener('keydown', handleKeyDown);
    
        // Remove event listener on cleanup
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []); // Empty dependency array ensures this effect runs only once after the initial render

    useEffect(() => {
        // Prevent the default action of the spacebar (it scrolls to the bottom in default browser mode)
        const handleKeyDown = (event) => {
            if (event.key === ' ') {
                event.preventDefault();
            }
        };

        // Add event listener
        window.addEventListener('keydown', handleKeyDown);

        // Remove event listener on cleanup
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []); // Empty dependency array ensures this effect runs only once after the initial render

    
    useEffect(() => {
        // When the user presses B
        const handleKeyDown = (event) => {
            if (event.key === 'b' || event.key === 'B') {
                if (engineState === EngineStates.PLAYING) {
                    toggleFoundingCity();
                }
            }
        };
    
        // Add event listener
        window.addEventListener('keydown', handleKeyDown);
    
        // Remove event listener on cleanup
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [foundingCity, engineState]); // Dependency ensures foundingCity is in a valid state before running

    useEffect(() => {
        // Define a variable outside of your event listener to keep track of the interval ID
        let scrollIntervalId = null;
        const interval = 60;

        const handleKeyDown = (event) => {
            // Prevent multiple intervals from being set if a key is already being held down
            if (scrollIntervalId !== null) return;

            const scroll = (offsetX, offsetY) => window.scrollBy({ top: offsetY, left: offsetX, behavior: 'smooth' });

            const scrollAmount = 100
            switch (event.key) {
                case 'w':
                case 'W':
                    scroll(0, -scrollAmount);
                    scrollIntervalId = setInterval(() => scroll(0, -scrollAmount), interval);
                    break;
                case 's':
                case 'S':
                    scroll(0, scrollAmount);
                    scrollIntervalId = setInterval(() => scroll(0, scrollAmount), interval);
                    break;
                case 'a':
                case 'A':
                    scroll(-scrollAmount, 0);
                    scrollIntervalId = setInterval(() => scroll(-scrollAmount, 0), interval);
                    break;
                case 'd':
                case 'D':
                    scroll(scrollAmount, 0);
                    scrollIntervalId = setInterval(() => scroll(scrollAmount, 0), interval);
                    break;
                default:
                    break;
            }
        };

        const handleKeyUp = (event) => {
            // Clear the interval when the key is released
            if (['w', 'W', 's', 'S', 'a', 'S', 'd', 'D'].includes(event.key)) {
                clearInterval(scrollIntervalId);
                scrollIntervalId = null;
            }
        };

        // Add event listeners for key down and key up
        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);

        // Remember to remove the event listeners on cleanup
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('keyup', handleKeyUp);
        };
    }, []); // Empty dependency array ensures this effect runs only once after the initial render

    const handleWheel = (event) => {
        const hexGridElement = document.getElementsByClassName('grid')[0];

        if (hexGridElement && hexGridElement.contains(event.target)) {
            event.preventDefault();
            const zoomFactor = 0.01;
            const minScale = 0.5; // Minimum scale limit
            if (!hexGridElement) return;
    
            let newScale = parseFloat(hexGridElement.style.transform.replace('scale(', '').replace(')', '')) || 1;
            if (event.deltaY < 0) {
                newScale += zoomFactor;
            } else {
                newScale = Math.max(minScale, newScale - zoomFactor); // Ensure newScale does not go below minScale
            }
            hexGridElement.style.transform = `scale(${newScale})`;
        }
    };

    const disableBigWheel = (event) => {
        // Function to check if the target or any parent has overflow-y: auto
        const hasOverflowingAutoY = (target) => {
            while (target && target !== document) {
                const overflowY = window.getComputedStyle(target).overflowY;
                const isOverflowing = target.scrollHeight > target.clientHeight;
                if (overflowY === 'auto' && isOverflowing) {
                    return true;
                }
                target = target.parentNode;
            }
            return false;
        };

        // Only prevent default if the target is not within an element that has overflow-y: auto
        if (!hasOverflowingAutoY(event.target)) {
            event.preventDefault();
        }
    }

    useEffect(() => {
        window.addEventListener('wheel', handleWheel, { passive: false });

        window.addEventListener('wheel', disableBigWheel, { passive: false });

        return () => {
            window.removeEventListener('wheel', handleWheel);
            window.removeEventListener('wheel', disableBigWheel);
        };
    }, []);
    
    const centerMap = (coords) => {
        // coords should be like "0,0,0"
        console.log("Centering on ", coords);
        const hexRef = hexRefs.current[coords].current;

        const hexGridRect = hexRef.getBoundingClientRect();
        // Current x, y coords
        const hexGridCenterX = hexGridRect.left + (hexGridRect.width / 2);
        const hexGridCenterY = hexGridRect.top + (hexGridRect.height / 2);

        // Absolute x, y coords
        const hexGridAbsCenterX = hexGridCenterX + window.scrollX;
        const hexGridAbsCenterY = hexGridCenterY + window.scrollY;

        // Calculate the window's center position
        const windowCenterX = window.innerWidth / 2;
        const windowCenterY = window.innerHeight / 2;

        // Scroll to the HexGrid's center
        window.scrollTo(hexGridAbsCenterX - windowCenterX, hexGridAbsCenterY - windowCenterY);
    }

    // Center the map on initial load
    const hasRunCenterRef = React.useRef(false);
    useEffect(() => {
        // Don't run if we've already run.
        if (!gameState || hasRunCenterRef.current) return;

        // Scroll to the middle of the map at start
        const centerCoords = "0,0,0";
        centerMap(centerCoords);
        hasRunCenterRef.current = true;
    }, [gameState]);

    useEffect(() => {
        const setTarget = (hex, isSecondary) => {
            if (!myCivIdRef.current || gameStateRef?.current?.special_mode_by_player_num?.[playerNumRef.current]) return;
    
            if (isSecondary) {
                setLastSetPrimaryTarget(false);
            }
            else {
                setLastSetPrimaryTarget(true);
            }
    
            const playerInput = {
                'move_type': `set_civ_${isSecondary ? "secondary" : "primary"}_target`,
                'target_coords': `${hex.q},${hex.r},${hex.s}`,
            }
            submitPlayerInput(playerInput);
        }
    
        const removeTarget = (isSecondary) => {
            if (!myCivIdRef.current) return;
    
            const playerInput = {
                'move_type': `remove_civ_${isSecondary ? "secondary" : "primary"}_target`,
            }
            submitPlayerInput(playerInput);
        }

        const handleContextMenu = (e) => {
            if (hoveredHexRef.current || !process.env.REACT_APP_LOCAL) {
                e.preventDefault();
            } 
    
            if (hoveredHexRef.current) {
                setHoveredCity(null);
    
                if (engineState !== EngineStates.PLAYING) {return;}
    
                if (hexesAreEqual(hoveredHexRef.current, target1Ref.current)) {
                    removeTarget(false);
                } else if (hexesAreEqual(hoveredHexRef.current, target2Ref.current)) {
                    removeTarget(true);
                } else {
                    setTarget(hoveredHexRef.current, !target1Ref.current ? false : !target2Ref.current ? true : lastSetPrimaryTargetRef.current ? true : false);
                }
                
                // Show flag arrows for 1s. Start after 100ms so there's time for the system to react to the update.
                clearTimeout(flagArrowsTimeoutRef.current);
                setTimeout(() => setShowFlagArrows(true), 100);
                flagArrowsTimeoutRef.current = setTimeout(() => setShowFlagArrows(false), 1000);
            }
        }

        document.addEventListener('contextmenu', handleContextMenu);

        return () => {
            document.removeEventListener('contextmenu', handleContextMenu);
        };
    }, [engineState]);

    useEffect(() => {
        if (engineState !== EngineStates.PLAYING && engineState !== EngineStates.GAME_OVER) {
            document.body.style.cursor = 'wait';
        } else {
            document.body.style.cursor = 'default';
        }
    }, [engineState]);

    const handleChangeTurnTimer = (value) => {
        const data = {
            seconds_per_turn: value === -1 ? null : value,
        }

        fetch(`${URL}/api/set_turn_timer/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        })
    }

    useEffect(() => {
        firstRenderRef.current = false;
    }, []);

    useEffect(() => {
        if (gameState) {
            gameStateExistsRef.current = true;
        }
    }, [gameState]);

    const volumeRef = React.useRef(volume);

    useEffect(() => {
        volumeRef.current = volume;
    }, [volume]);

    function playMoveSound(moveSound) {
        if (!userHasInteracted) return;
    
        try {
            let audio = new Audio(moveSound);
            audio.volume = 0.5 * volumeRef.current / 100;
            audio.play();
        } catch (error) {
            console.error('Error playing sound:', error);
        }
    }

    function playMeleeAttackSound(meleeAttackSound) {
        if (!userHasInteracted) return;
    
        try {
            let audio = new Audio(meleeAttackSound);
            audio.volume = 0.1 * volumeRef.current / 100;
            audio.play();
        } catch (error) {
            console.error('Error playing sound:', error);
        }
    }

    function playRangedAttackSound(rangedAttackSound) {
        if (!userHasInteracted) return;

        try {
            let audio = new Audio(rangedAttackSound);
            audio.volume = 1.0 * volumeRef.current / 100;
            audio.play();
        } catch (error) {
            console.error('Error playing sound:', error);
        }
    }

    function playCitySound(medievalCitySound, modernCitySound, isModern) {
        if (!userHasInteracted) return;

        try {
            let audio = new Audio(isModern ? modernCitySound : medievalCitySound);
            audio.volume = 0.3 * volumeRef.current / 100;
            audio.play();
            const fadeOutInterval = setInterval(() => {
                if (audio.volume >= 0.05 * volumeRef.current / 100) {
                    audio.volume -= 0.05 * volumeRef.current / 100;
                } else {
                    clearInterval(fadeOutInterval);
                    audio.pause();
                }
            }, 1000); // Adjust the interval for desired fade out speed
        }
        catch (error) {
            console.error('Error playing sound:', error);
        }
    }        

    function playGunpowderMeleeAttackSound(gunpowderMeleeAttackSound) {
        if (!userHasInteracted) return;

        try {
            let audio = new Audio(gunpowderMeleeAttackSound);
            audio.volume = 0.1 * volumeRef.current / 100;
            audio.play();
        } catch (error) {
            console.error('Error playing sound:', error);
        }
    }

    function playGunpowderRangedAttackSound(gunpowderRangedAttackSound) {
        if (!userHasInteracted) return;

        try {
            let audio = new Audio(gunpowderRangedAttackSound);
            audio.volume = 0.09 * volumeRef.current / 100;
            audio.play();
        } catch (error) {
            console.error('Error playing sound:', error);
        }
    }

    const hexRefs = React.useRef({
        '-20,0,20': React.createRef(),
        '-20,1,19': React.createRef(),
        '-20,2,18': React.createRef(),
        '-20,3,17': React.createRef(),
        '-20,4,16': React.createRef(),
        '-20,5,15': React.createRef(),
        '-20,6,14': React.createRef(),
        '-20,7,13': React.createRef(),
        '-20,8,12': React.createRef(),
        '-20,9,11': React.createRef(),
        '-20,10,10': React.createRef(),
        '-20,11,9': React.createRef(),
        '-20,12,8': React.createRef(),
        '-20,13,7': React.createRef(),
        '-20,14,6': React.createRef(),
        '-20,15,5': React.createRef(),
        '-20,16,4': React.createRef(),
        '-20,17,3': React.createRef(),
        '-20,18,2': React.createRef(),
        '-20,19,1': React.createRef(),
        '-20,20,0': React.createRef(),
        '-19,-1,20': React.createRef(),
        '-19,0,19': React.createRef(),
        '-19,1,18': React.createRef(),
        '-19,2,17': React.createRef(),
        '-19,3,16': React.createRef(),
        '-19,4,15': React.createRef(),
        '-19,5,14': React.createRef(),
        '-19,6,13': React.createRef(),
        '-19,7,12': React.createRef(),
        '-19,8,11': React.createRef(),
        '-19,9,10': React.createRef(),
        '-19,10,9': React.createRef(),
        '-19,11,8': React.createRef(),
        '-19,12,7': React.createRef(),
        '-19,13,6': React.createRef(),
        '-19,14,5': React.createRef(),
        '-19,15,4': React.createRef(),
        '-19,16,3': React.createRef(),
        '-19,17,2': React.createRef(),
        '-19,18,1': React.createRef(),
        '-19,19,0': React.createRef(),
        '-19,20,-1': React.createRef(),
        '-18,-2,20': React.createRef(),
        '-18,-1,19': React.createRef(),
        '-18,0,18': React.createRef(),
        '-18,1,17': React.createRef(),
        '-18,2,16': React.createRef(),
        '-18,3,15': React.createRef(),
        '-18,4,14': React.createRef(),
        '-18,5,13': React.createRef(),
        '-18,6,12': React.createRef(),
        '-18,7,11': React.createRef(),
        '-18,8,10': React.createRef(),
        '-18,9,9': React.createRef(),
        '-18,10,8': React.createRef(),
        '-18,11,7': React.createRef(),
        '-18,12,6': React.createRef(),
        '-18,13,5': React.createRef(),
        '-18,14,4': React.createRef(),
        '-18,15,3': React.createRef(),
        '-18,16,2': React.createRef(),
        '-18,17,1': React.createRef(),
        '-18,18,0': React.createRef(),
        '-18,19,-1': React.createRef(),
        '-18,20,-2': React.createRef(),
        '-17,-3,20': React.createRef(),
        '-17,-2,19': React.createRef(),
        '-17,-1,18': React.createRef(),
        '-17,0,17': React.createRef(),
        '-17,1,16': React.createRef(),
        '-17,2,15': React.createRef(),
        '-17,3,14': React.createRef(),
        '-17,4,13': React.createRef(),
        '-17,5,12': React.createRef(),
        '-17,6,11': React.createRef(),
        '-17,7,10': React.createRef(),
        '-17,8,9': React.createRef(),
        '-17,9,8': React.createRef(),
        '-17,10,7': React.createRef(),
        '-17,11,6': React.createRef(),
        '-17,12,5': React.createRef(),
        '-17,13,4': React.createRef(),
        '-17,14,3': React.createRef(),
        '-17,15,2': React.createRef(),
        '-17,16,1': React.createRef(),
        '-17,17,0': React.createRef(),
        '-17,18,-1': React.createRef(),
        '-17,19,-2': React.createRef(),
        '-17,20,-3': React.createRef(),
        '-16,-4,20': React.createRef(),
        '-16,-3,19': React.createRef(),
        '-16,-2,18': React.createRef(),
        '-16,-1,17': React.createRef(),
        '-16,0,16': React.createRef(),
        '-16,1,15': React.createRef(),
        '-16,2,14': React.createRef(),
        '-16,3,13': React.createRef(),
        '-16,4,12': React.createRef(),
        '-16,5,11': React.createRef(),
        '-16,6,10': React.createRef(),
        '-16,7,9': React.createRef(),
        '-16,8,8': React.createRef(),
        '-16,9,7': React.createRef(),
        '-16,10,6': React.createRef(),
        '-16,11,5': React.createRef(),
        '-16,12,4': React.createRef(),
        '-16,13,3': React.createRef(),
        '-16,14,2': React.createRef(),
        '-16,15,1': React.createRef(),
        '-16,16,0': React.createRef(),
        '-16,17,-1': React.createRef(),
        '-16,18,-2': React.createRef(),
        '-16,19,-3': React.createRef(),
        '-16,20,-4': React.createRef(),
        '-15,-5,20': React.createRef(),
        '-15,-4,19': React.createRef(),
        '-15,-3,18': React.createRef(),
        '-15,-2,17': React.createRef(),
        '-15,-1,16': React.createRef(),
        '-15,0,15': React.createRef(),
        '-15,1,14': React.createRef(),
        '-15,2,13': React.createRef(),
        '-15,3,12': React.createRef(),
        '-15,4,11': React.createRef(),
        '-15,5,10': React.createRef(),
        '-15,6,9': React.createRef(),
        '-15,7,8': React.createRef(),
        '-15,8,7': React.createRef(),
        '-15,9,6': React.createRef(),
        '-15,10,5': React.createRef(),
        '-15,11,4': React.createRef(),
        '-15,12,3': React.createRef(),
        '-15,13,2': React.createRef(),
        '-15,14,1': React.createRef(),
        '-15,15,0': React.createRef(),
        '-15,16,-1': React.createRef(),
        '-15,17,-2': React.createRef(),
        '-15,18,-3': React.createRef(),
        '-15,19,-4': React.createRef(),
        '-15,20,-5': React.createRef(),
        '-14,-6,20': React.createRef(),
        '-14,-5,19': React.createRef(),
        '-14,-4,18': React.createRef(),
        '-14,-3,17': React.createRef(),
        '-14,-2,16': React.createRef(),
        '-14,-1,15': React.createRef(),
        '-14,0,14': React.createRef(),
        '-14,1,13': React.createRef(),
        '-14,2,12': React.createRef(),
        '-14,3,11': React.createRef(),
        '-14,4,10': React.createRef(),
        '-14,5,9': React.createRef(),
        '-14,6,8': React.createRef(),
        '-14,7,7': React.createRef(),
        '-14,8,6': React.createRef(),
        '-14,9,5': React.createRef(),
        '-14,10,4': React.createRef(),
        '-14,11,3': React.createRef(),
        '-14,12,2': React.createRef(),
        '-14,13,1': React.createRef(),
        '-14,14,0': React.createRef(),
        '-14,15,-1': React.createRef(),
        '-14,16,-2': React.createRef(),
        '-14,17,-3': React.createRef(),
        '-14,18,-4': React.createRef(),
        '-14,19,-5': React.createRef(),
        '-14,20,-6': React.createRef(),
        '-13,-7,20': React.createRef(),
        '-13,-6,19': React.createRef(),
        '-13,-5,18': React.createRef(),
        '-13,-4,17': React.createRef(),
        '-13,-3,16': React.createRef(),
        '-13,-2,15': React.createRef(),
        '-13,-1,14': React.createRef(),
        '-13,0,13': React.createRef(),
        '-13,1,12': React.createRef(),
        '-13,2,11': React.createRef(),
        '-13,3,10': React.createRef(),
        '-13,4,9': React.createRef(),
        '-13,5,8': React.createRef(),
        '-13,6,7': React.createRef(),
        '-13,7,6': React.createRef(),
        '-13,8,5': React.createRef(),
        '-13,9,4': React.createRef(),
        '-13,10,3': React.createRef(),
        '-13,11,2': React.createRef(),
        '-13,12,1': React.createRef(),
        '-13,13,0': React.createRef(),
        '-13,14,-1': React.createRef(),
        '-13,15,-2': React.createRef(),
        '-13,16,-3': React.createRef(),
        '-13,17,-4': React.createRef(),
        '-13,18,-5': React.createRef(),
        '-13,19,-6': React.createRef(),
        '-13,20,-7': React.createRef(),
        '-12,-8,20': React.createRef(),
        '-12,-7,19': React.createRef(),
        '-12,-6,18': React.createRef(),
        '-12,-5,17': React.createRef(),
        '-12,-4,16': React.createRef(),
        '-12,-3,15': React.createRef(),
        '-12,-2,14': React.createRef(),
        '-12,-1,13': React.createRef(),
        '-12,0,12': React.createRef(),
        '-12,1,11': React.createRef(),
        '-12,2,10': React.createRef(),
        '-12,3,9': React.createRef(),
        '-12,4,8': React.createRef(),
        '-12,5,7': React.createRef(),
        '-12,6,6': React.createRef(),
        '-12,7,5': React.createRef(),
        '-12,8,4': React.createRef(),
        '-12,9,3': React.createRef(),
        '-12,10,2': React.createRef(),
        '-12,11,1': React.createRef(),
        '-12,12,0': React.createRef(),
        '-12,13,-1': React.createRef(),
        '-12,14,-2': React.createRef(),
        '-12,15,-3': React.createRef(),
        '-12,16,-4': React.createRef(),
        '-12,17,-5': React.createRef(),
        '-12,18,-6': React.createRef(),
        '-12,19,-7': React.createRef(),
        '-12,20,-8': React.createRef(),
        '-11,-9,20': React.createRef(),
        '-11,-8,19': React.createRef(),
        '-11,-7,18': React.createRef(),
        '-11,-6,17': React.createRef(),
        '-11,-5,16': React.createRef(),
        '-11,-4,15': React.createRef(),
        '-11,-3,14': React.createRef(),
        '-11,-2,13': React.createRef(),
        '-11,-1,12': React.createRef(),
        '-11,0,11': React.createRef(),
        '-11,1,10': React.createRef(),
        '-11,2,9': React.createRef(),
        '-11,3,8': React.createRef(),
        '-11,4,7': React.createRef(),
        '-11,5,6': React.createRef(),
        '-11,6,5': React.createRef(),
        '-11,7,4': React.createRef(),
        '-11,8,3': React.createRef(),
        '-11,9,2': React.createRef(),
        '-11,10,1': React.createRef(),
        '-11,11,0': React.createRef(),
        '-11,12,-1': React.createRef(),
        '-11,13,-2': React.createRef(),
        '-11,14,-3': React.createRef(),
        '-11,15,-4': React.createRef(),
        '-11,16,-5': React.createRef(),
        '-11,17,-6': React.createRef(),
        '-11,18,-7': React.createRef(),
        '-11,19,-8': React.createRef(),
        '-11,20,-9': React.createRef(),
        '-10,-10,20': React.createRef(),
        '-10,-9,19': React.createRef(),
        '-10,-8,18': React.createRef(),
        '-10,-7,17': React.createRef(),
        '-10,-6,16': React.createRef(),
        '-10,-5,15': React.createRef(),
        '-10,-4,14': React.createRef(),
        '-10,-3,13': React.createRef(),
        '-10,-2,12': React.createRef(),
        '-10,-1,11': React.createRef(),
        '-10,0,10': React.createRef(),
        '-10,1,9': React.createRef(),
        '-10,2,8': React.createRef(),
        '-10,3,7': React.createRef(),
        '-10,4,6': React.createRef(),
        '-10,5,5': React.createRef(),
        '-10,6,4': React.createRef(),
        '-10,7,3': React.createRef(),
        '-10,8,2': React.createRef(),
        '-10,9,1': React.createRef(),
        '-10,10,0': React.createRef(),
        '-10,11,-1': React.createRef(),
        '-10,12,-2': React.createRef(),
        '-10,13,-3': React.createRef(),
        '-10,14,-4': React.createRef(),
        '-10,15,-5': React.createRef(),
        '-10,16,-6': React.createRef(),
        '-10,17,-7': React.createRef(),
        '-10,18,-8': React.createRef(),
        '-10,19,-9': React.createRef(),
        '-10,20,-10': React.createRef(),
        '-9,-11,20': React.createRef(),
        '-9,-10,19': React.createRef(),
        '-9,-9,18': React.createRef(),
        '-9,-8,17': React.createRef(),
        '-9,-7,16': React.createRef(),
        '-9,-6,15': React.createRef(),
        '-9,-5,14': React.createRef(),
        '-9,-4,13': React.createRef(),
        '-9,-3,12': React.createRef(),
        '-9,-2,11': React.createRef(),
        '-9,-1,10': React.createRef(),
        '-9,0,9': React.createRef(),
        '-9,1,8': React.createRef(),
        '-9,2,7': React.createRef(),
        '-9,3,6': React.createRef(),
        '-9,4,5': React.createRef(),
        '-9,5,4': React.createRef(),
        '-9,6,3': React.createRef(),
        '-9,7,2': React.createRef(),
        '-9,8,1': React.createRef(),
        '-9,9,0': React.createRef(),
        '-9,10,-1': React.createRef(),
        '-9,11,-2': React.createRef(),
        '-9,12,-3': React.createRef(),
        '-9,13,-4': React.createRef(),
        '-9,14,-5': React.createRef(),
        '-9,15,-6': React.createRef(),
        '-9,16,-7': React.createRef(),
        '-9,17,-8': React.createRef(),
        '-9,18,-9': React.createRef(),
        '-9,19,-10': React.createRef(),
        '-9,20,-11': React.createRef(),
        '-8,-12,20': React.createRef(),
        '-8,-11,19': React.createRef(),
        '-8,-10,18': React.createRef(),
        '-8,-9,17': React.createRef(),
        '-8,-8,16': React.createRef(),
        '-8,-7,15': React.createRef(),
        '-8,-6,14': React.createRef(),
        '-8,-5,13': React.createRef(),
        '-8,-4,12': React.createRef(),
        '-8,-3,11': React.createRef(),
        '-8,-2,10': React.createRef(),
        '-8,-1,9': React.createRef(),
        '-8,0,8': React.createRef(),
        '-8,1,7': React.createRef(),
        '-8,2,6': React.createRef(),
        '-8,3,5': React.createRef(),
        '-8,4,4': React.createRef(),
        '-8,5,3': React.createRef(),
        '-8,6,2': React.createRef(),
        '-8,7,1': React.createRef(),
        '-8,8,0': React.createRef(),
        '-8,9,-1': React.createRef(),
        '-8,10,-2': React.createRef(),
        '-8,11,-3': React.createRef(),
        '-8,12,-4': React.createRef(),
        '-8,13,-5': React.createRef(),
        '-8,14,-6': React.createRef(),
        '-8,15,-7': React.createRef(),
        '-8,16,-8': React.createRef(),
        '-8,17,-9': React.createRef(),
        '-8,18,-10': React.createRef(),
        '-8,19,-11': React.createRef(),
        '-8,20,-12': React.createRef(),
        '-7,-13,20': React.createRef(),
        '-7,-12,19': React.createRef(),
        '-7,-11,18': React.createRef(),
        '-7,-10,17': React.createRef(),
        '-7,-9,16': React.createRef(),
        '-7,-8,15': React.createRef(),
        '-7,-7,14': React.createRef(),
        '-7,-6,13': React.createRef(),
        '-7,-5,12': React.createRef(),
        '-7,-4,11': React.createRef(),
        '-7,-3,10': React.createRef(),
        '-7,-2,9': React.createRef(),
        '-7,-1,8': React.createRef(),
        '-7,0,7': React.createRef(),
        '-7,1,6': React.createRef(),
        '-7,2,5': React.createRef(),
        '-7,3,4': React.createRef(),
        '-7,4,3': React.createRef(),
        '-7,5,2': React.createRef(),
        '-7,6,1': React.createRef(),
        '-7,7,0': React.createRef(),
        '-7,8,-1': React.createRef(),
        '-7,9,-2': React.createRef(),
        '-7,10,-3': React.createRef(),
        '-7,11,-4': React.createRef(),
        '-7,12,-5': React.createRef(),
        '-7,13,-6': React.createRef(),
        '-7,14,-7': React.createRef(),
        '-7,15,-8': React.createRef(),
        '-7,16,-9': React.createRef(),
        '-7,17,-10': React.createRef(),
        '-7,18,-11': React.createRef(),
        '-7,19,-12': React.createRef(),
        '-7,20,-13': React.createRef(),
        '-6,-14,20': React.createRef(),
        '-6,-13,19': React.createRef(),
        '-6,-12,18': React.createRef(),
        '-6,-11,17': React.createRef(),
        '-6,-10,16': React.createRef(),
        '-6,-9,15': React.createRef(),
        '-6,-8,14': React.createRef(),
        '-6,-7,13': React.createRef(),
        '-6,-6,12': React.createRef(),
        '-6,-5,11': React.createRef(),
        '-6,-4,10': React.createRef(),
        '-6,-3,9': React.createRef(),
        '-6,-2,8': React.createRef(),
        '-6,-1,7': React.createRef(),
        '-6,0,6': React.createRef(),
        '-6,1,5': React.createRef(),
        '-6,2,4': React.createRef(),
        '-6,3,3': React.createRef(),
        '-6,4,2': React.createRef(),
        '-6,5,1': React.createRef(),
        '-6,6,0': React.createRef(),
        '-6,7,-1': React.createRef(),
        '-6,8,-2': React.createRef(),
        '-6,9,-3': React.createRef(),
        '-6,10,-4': React.createRef(),
        '-6,11,-5': React.createRef(),
        '-6,12,-6': React.createRef(),
        '-6,13,-7': React.createRef(),
        '-6,14,-8': React.createRef(),
        '-6,15,-9': React.createRef(),
        '-6,16,-10': React.createRef(),
        '-6,17,-11': React.createRef(),
        '-6,18,-12': React.createRef(),
        '-6,19,-13': React.createRef(),
        '-6,20,-14': React.createRef(),
        '-5,-15,20': React.createRef(),
        '-5,-14,19': React.createRef(),
        '-5,-13,18': React.createRef(),
        '-5,-12,17': React.createRef(),
        '-5,-11,16': React.createRef(),
        '-5,-10,15': React.createRef(),
        '-5,-9,14': React.createRef(),
        '-5,-8,13': React.createRef(),
        '-5,-7,12': React.createRef(),
        '-5,-6,11': React.createRef(),
        '-5,-5,10': React.createRef(),
        '-5,-4,9': React.createRef(),
        '-5,-3,8': React.createRef(),
        '-5,-2,7': React.createRef(),
        '-5,-1,6': React.createRef(),
        '-5,0,5': React.createRef(),
        '-5,1,4': React.createRef(),
        '-5,2,3': React.createRef(),
        '-5,3,2': React.createRef(),
        '-5,4,1': React.createRef(),
        '-5,5,0': React.createRef(),
        '-5,6,-1': React.createRef(),
        '-5,7,-2': React.createRef(),
        '-5,8,-3': React.createRef(),
        '-5,9,-4': React.createRef(),
        '-5,10,-5': React.createRef(),
        '-5,11,-6': React.createRef(),
        '-5,12,-7': React.createRef(),
        '-5,13,-8': React.createRef(),
        '-5,14,-9': React.createRef(),
        '-5,15,-10': React.createRef(),
        '-5,16,-11': React.createRef(),
        '-5,17,-12': React.createRef(),
        '-5,18,-13': React.createRef(),
        '-5,19,-14': React.createRef(),
        '-5,20,-15': React.createRef(),
        '-4,-16,20': React.createRef(),
        '-4,-15,19': React.createRef(),
        '-4,-14,18': React.createRef(),
        '-4,-13,17': React.createRef(),
        '-4,-12,16': React.createRef(),
        '-4,-11,15': React.createRef(),
        '-4,-10,14': React.createRef(),
        '-4,-9,13': React.createRef(),
        '-4,-8,12': React.createRef(),
        '-4,-7,11': React.createRef(),
        '-4,-6,10': React.createRef(),
        '-4,-5,9': React.createRef(),
        '-4,-4,8': React.createRef(),
        '-4,-3,7': React.createRef(),
        '-4,-2,6': React.createRef(),
        '-4,-1,5': React.createRef(),
        '-4,0,4': React.createRef(),
        '-4,1,3': React.createRef(),
        '-4,2,2': React.createRef(),
        '-4,3,1': React.createRef(),
        '-4,4,0': React.createRef(),
        '-4,5,-1': React.createRef(),
        '-4,6,-2': React.createRef(),
        '-4,7,-3': React.createRef(),
        '-4,8,-4': React.createRef(),
        '-4,9,-5': React.createRef(),
        '-4,10,-6': React.createRef(),
        '-4,11,-7': React.createRef(),
        '-4,12,-8': React.createRef(),
        '-4,13,-9': React.createRef(),
        '-4,14,-10': React.createRef(),
        '-4,15,-11': React.createRef(),
        '-4,16,-12': React.createRef(),
        '-4,17,-13': React.createRef(),
        '-4,18,-14': React.createRef(),
        '-4,19,-15': React.createRef(),
        '-4,20,-16': React.createRef(),
        '-3,-17,20': React.createRef(),
        '-3,-16,19': React.createRef(),
        '-3,-15,18': React.createRef(),
        '-3,-14,17': React.createRef(),
        '-3,-13,16': React.createRef(),
        '-3,-12,15': React.createRef(),
        '-3,-11,14': React.createRef(),
        '-3,-10,13': React.createRef(),
        '-3,-9,12': React.createRef(),
        '-3,-8,11': React.createRef(),
        '-3,-7,10': React.createRef(),
        '-3,-6,9': React.createRef(),
        '-3,-5,8': React.createRef(),
        '-3,-4,7': React.createRef(),
        '-3,-3,6': React.createRef(),
        '-3,-2,5': React.createRef(),
        '-3,-1,4': React.createRef(),
        '-3,0,3': React.createRef(),
        '-3,1,2': React.createRef(),
        '-3,2,1': React.createRef(),
        '-3,3,0': React.createRef(),
        '-3,4,-1': React.createRef(),
        '-3,5,-2': React.createRef(),
        '-3,6,-3': React.createRef(),
        '-3,7,-4': React.createRef(),
        '-3,8,-5': React.createRef(),
        '-3,9,-6': React.createRef(),
        '-3,10,-7': React.createRef(),
        '-3,11,-8': React.createRef(),
        '-3,12,-9': React.createRef(),
        '-3,13,-10': React.createRef(),
        '-3,14,-11': React.createRef(),
        '-3,15,-12': React.createRef(),
        '-3,16,-13': React.createRef(),
        '-3,17,-14': React.createRef(),
        '-3,18,-15': React.createRef(),
        '-3,19,-16': React.createRef(),
        '-3,20,-17': React.createRef(),
        '-2,-18,20': React.createRef(),
        '-2,-17,19': React.createRef(),
        '-2,-16,18': React.createRef(),
        '-2,-15,17': React.createRef(),
        '-2,-14,16': React.createRef(),
        '-2,-13,15': React.createRef(),
        '-2,-12,14': React.createRef(),
        '-2,-11,13': React.createRef(),
        '-2,-10,12': React.createRef(),
        '-2,-9,11': React.createRef(),
        '-2,-8,10': React.createRef(),
        '-2,-7,9': React.createRef(),
        '-2,-6,8': React.createRef(),
        '-2,-5,7': React.createRef(),
        '-2,-4,6': React.createRef(),
        '-2,-3,5': React.createRef(),
        '-2,-2,4': React.createRef(),
        '-2,-1,3': React.createRef(),
        '-2,0,2': React.createRef(),
        '-2,1,1': React.createRef(),
        '-2,2,0': React.createRef(),
        '-2,3,-1': React.createRef(),
        '-2,4,-2': React.createRef(),
        '-2,5,-3': React.createRef(),
        '-2,6,-4': React.createRef(),
        '-2,7,-5': React.createRef(),
        '-2,8,-6': React.createRef(),
        '-2,9,-7': React.createRef(),
        '-2,10,-8': React.createRef(),
        '-2,11,-9': React.createRef(),
        '-2,12,-10': React.createRef(),
        '-2,13,-11': React.createRef(),
        '-2,14,-12': React.createRef(),
        '-2,15,-13': React.createRef(),
        '-2,16,-14': React.createRef(),
        '-2,17,-15': React.createRef(),
        '-2,18,-16': React.createRef(),
        '-2,19,-17': React.createRef(),
        '-2,20,-18': React.createRef(),
        '-1,-19,20': React.createRef(),
        '-1,-18,19': React.createRef(),
        '-1,-17,18': React.createRef(),
        '-1,-16,17': React.createRef(),
        '-1,-15,16': React.createRef(),
        '-1,-14,15': React.createRef(),
        '-1,-13,14': React.createRef(),
        '-1,-12,13': React.createRef(),
        '-1,-11,12': React.createRef(),
        '-1,-10,11': React.createRef(),
        '-1,-9,10': React.createRef(),
        '-1,-8,9': React.createRef(),
        '-1,-7,8': React.createRef(),
        '-1,-6,7': React.createRef(),
        '-1,-5,6': React.createRef(),
        '-1,-4,5': React.createRef(),
        '-1,-3,4': React.createRef(),
        '-1,-2,3': React.createRef(),
        '-1,-1,2': React.createRef(),
        '-1,0,1': React.createRef(),
        '-1,1,0': React.createRef(),
        '-1,2,-1': React.createRef(),
        '-1,3,-2': React.createRef(),
        '-1,4,-3': React.createRef(),
        '-1,5,-4': React.createRef(),
        '-1,6,-5': React.createRef(),
        '-1,7,-6': React.createRef(),
        '-1,8,-7': React.createRef(),
        '-1,9,-8': React.createRef(),
        '-1,10,-9': React.createRef(),
        '-1,11,-10': React.createRef(),
        '-1,12,-11': React.createRef(),
        '-1,13,-12': React.createRef(),
        '-1,14,-13': React.createRef(),
        '-1,15,-14': React.createRef(),
        '-1,16,-15': React.createRef(),
        '-1,17,-16': React.createRef(),
        '-1,18,-17': React.createRef(),
        '-1,19,-18': React.createRef(),
        '-1,20,-19': React.createRef(),
        '0,-20,20': React.createRef(),
        '0,-19,19': React.createRef(),
        '0,-18,18': React.createRef(),
        '0,-17,17': React.createRef(),
        '0,-16,16': React.createRef(),
        '0,-15,15': React.createRef(),
        '0,-14,14': React.createRef(),
        '0,-13,13': React.createRef(),
        '0,-12,12': React.createRef(),
        '0,-11,11': React.createRef(),
        '0,-10,10': React.createRef(),
        '0,-9,9': React.createRef(),
        '0,-8,8': React.createRef(),
        '0,-7,7': React.createRef(),
        '0,-6,6': React.createRef(),
        '0,-5,5': React.createRef(),
        '0,-4,4': React.createRef(),
        '0,-3,3': React.createRef(),
        '0,-2,2': React.createRef(),
        '0,-1,1': React.createRef(),
        '0,0,0': React.createRef(),
        '0,1,-1': React.createRef(),
        '0,2,-2': React.createRef(),
        '0,3,-3': React.createRef(),
        '0,4,-4': React.createRef(),
        '0,5,-5': React.createRef(),
        '0,6,-6': React.createRef(),
        '0,7,-7': React.createRef(),
        '0,8,-8': React.createRef(),
        '0,9,-9': React.createRef(),
        '0,10,-10': React.createRef(),
        '0,11,-11': React.createRef(),
        '0,12,-12': React.createRef(),
        '0,13,-13': React.createRef(),
        '0,14,-14': React.createRef(),
        '0,15,-15': React.createRef(),
        '0,16,-16': React.createRef(),
        '0,17,-17': React.createRef(),
        '0,18,-18': React.createRef(),
        '0,19,-19': React.createRef(),
        '0,20,-20': React.createRef(),
        '1,-20,19': React.createRef(),
        '1,-19,18': React.createRef(),
        '1,-18,17': React.createRef(),
        '1,-17,16': React.createRef(),
        '1,-16,15': React.createRef(),
        '1,-15,14': React.createRef(),
        '1,-14,13': React.createRef(),
        '1,-13,12': React.createRef(),
        '1,-12,11': React.createRef(),
        '1,-11,10': React.createRef(),
        '1,-10,9': React.createRef(),
        '1,-9,8': React.createRef(),
        '1,-8,7': React.createRef(),
        '1,-7,6': React.createRef(),
        '1,-6,5': React.createRef(),
        '1,-5,4': React.createRef(),
        '1,-4,3': React.createRef(),
        '1,-3,2': React.createRef(),
        '1,-2,1': React.createRef(),
        '1,-1,0': React.createRef(),
        '1,0,-1': React.createRef(),
        '1,1,-2': React.createRef(),
        '1,2,-3': React.createRef(),
        '1,3,-4': React.createRef(),
        '1,4,-5': React.createRef(),
        '1,5,-6': React.createRef(),
        '1,6,-7': React.createRef(),
        '1,7,-8': React.createRef(),
        '1,8,-9': React.createRef(),
        '1,9,-10': React.createRef(),
        '1,10,-11': React.createRef(),
        '1,11,-12': React.createRef(),
        '1,12,-13': React.createRef(),
        '1,13,-14': React.createRef(),
        '1,14,-15': React.createRef(),
        '1,15,-16': React.createRef(),
        '1,16,-17': React.createRef(),
        '1,17,-18': React.createRef(),
        '1,18,-19': React.createRef(),
        '1,19,-20': React.createRef(),
        '2,-20,18': React.createRef(),
        '2,-19,17': React.createRef(),
        '2,-18,16': React.createRef(),
        '2,-17,15': React.createRef(),
        '2,-16,14': React.createRef(),
        '2,-15,13': React.createRef(),
        '2,-14,12': React.createRef(),
        '2,-13,11': React.createRef(),
        '2,-12,10': React.createRef(),
        '2,-11,9': React.createRef(),
        '2,-10,8': React.createRef(),
        '2,-9,7': React.createRef(),
        '2,-8,6': React.createRef(),
        '2,-7,5': React.createRef(),
        '2,-6,4': React.createRef(),
        '2,-5,3': React.createRef(),
        '2,-4,2': React.createRef(),
        '2,-3,1': React.createRef(),
        '2,-2,0': React.createRef(),
        '2,-1,-1': React.createRef(),
        '2,0,-2': React.createRef(),
        '2,1,-3': React.createRef(),
        '2,2,-4': React.createRef(),
        '2,3,-5': React.createRef(),
        '2,4,-6': React.createRef(),
        '2,5,-7': React.createRef(),
        '2,6,-8': React.createRef(),
        '2,7,-9': React.createRef(),
        '2,8,-10': React.createRef(),
        '2,9,-11': React.createRef(),
        '2,10,-12': React.createRef(),
        '2,11,-13': React.createRef(),
        '2,12,-14': React.createRef(),
        '2,13,-15': React.createRef(),
        '2,14,-16': React.createRef(),
        '2,15,-17': React.createRef(),
        '2,16,-18': React.createRef(),
        '2,17,-19': React.createRef(),
        '2,18,-20': React.createRef(),
        '3,-20,17': React.createRef(),
        '3,-19,16': React.createRef(),
        '3,-18,15': React.createRef(),
        '3,-17,14': React.createRef(),
        '3,-16,13': React.createRef(),
        '3,-15,12': React.createRef(),
        '3,-14,11': React.createRef(),
        '3,-13,10': React.createRef(),
        '3,-12,9': React.createRef(),
        '3,-11,8': React.createRef(),
        '3,-10,7': React.createRef(),
        '3,-9,6': React.createRef(),
        '3,-8,5': React.createRef(),
        '3,-7,4': React.createRef(),
        '3,-6,3': React.createRef(),
        '3,-5,2': React.createRef(),
        '3,-4,1': React.createRef(),
        '3,-3,0': React.createRef(),
        '3,-2,-1': React.createRef(),
        '3,-1,-2': React.createRef(),
        '3,0,-3': React.createRef(),
        '3,1,-4': React.createRef(),
        '3,2,-5': React.createRef(),
        '3,3,-6': React.createRef(),
        '3,4,-7': React.createRef(),
        '3,5,-8': React.createRef(),
        '3,6,-9': React.createRef(),
        '3,7,-10': React.createRef(),
        '3,8,-11': React.createRef(),
        '3,9,-12': React.createRef(),
        '3,10,-13': React.createRef(),
        '3,11,-14': React.createRef(),
        '3,12,-15': React.createRef(),
        '3,13,-16': React.createRef(),
        '3,14,-17': React.createRef(),
        '3,15,-18': React.createRef(),
        '3,16,-19': React.createRef(),
        '3,17,-20': React.createRef(),
        '4,-20,16': React.createRef(),
        '4,-19,15': React.createRef(),
        '4,-18,14': React.createRef(),
        '4,-17,13': React.createRef(),
        '4,-16,12': React.createRef(),
        '4,-15,11': React.createRef(),
        '4,-14,10': React.createRef(),
        '4,-13,9': React.createRef(),
        '4,-12,8': React.createRef(),
        '4,-11,7': React.createRef(),
        '4,-10,6': React.createRef(),
        '4,-9,5': React.createRef(),
        '4,-8,4': React.createRef(),
        '4,-7,3': React.createRef(),
        '4,-6,2': React.createRef(),
        '4,-5,1': React.createRef(),
        '4,-4,0': React.createRef(),
        '4,-3,-1': React.createRef(),
        '4,-2,-2': React.createRef(),
        '4,-1,-3': React.createRef(),
        '4,0,-4': React.createRef(),
        '4,1,-5': React.createRef(),
        '4,2,-6': React.createRef(),
        '4,3,-7': React.createRef(),
        '4,4,-8': React.createRef(),
        '4,5,-9': React.createRef(),
        '4,6,-10': React.createRef(),
        '4,7,-11': React.createRef(),
        '4,8,-12': React.createRef(),
        '4,9,-13': React.createRef(),
        '4,10,-14': React.createRef(),
        '4,11,-15': React.createRef(),
        '4,12,-16': React.createRef(),
        '4,13,-17': React.createRef(),
        '4,14,-18': React.createRef(),
        '4,15,-19': React.createRef(),
        '4,16,-20': React.createRef(),
        '5,-20,15': React.createRef(),
        '5,-19,14': React.createRef(),
        '5,-18,13': React.createRef(),
        '5,-17,12': React.createRef(),
        '5,-16,11': React.createRef(),
        '5,-15,10': React.createRef(),
        '5,-14,9': React.createRef(),
        '5,-13,8': React.createRef(),
        '5,-12,7': React.createRef(),
        '5,-11,6': React.createRef(),
        '5,-10,5': React.createRef(),
        '5,-9,4': React.createRef(),
        '5,-8,3': React.createRef(),
        '5,-7,2': React.createRef(),
        '5,-6,1': React.createRef(),
        '5,-5,0': React.createRef(),
        '5,-4,-1': React.createRef(),
        '5,-3,-2': React.createRef(),
        '5,-2,-3': React.createRef(),
        '5,-1,-4': React.createRef(),
        '5,0,-5': React.createRef(),
        '5,1,-6': React.createRef(),
        '5,2,-7': React.createRef(),
        '5,3,-8': React.createRef(),
        '5,4,-9': React.createRef(),
        '5,5,-10': React.createRef(),
        '5,6,-11': React.createRef(),
        '5,7,-12': React.createRef(),
        '5,8,-13': React.createRef(),
        '5,9,-14': React.createRef(),
        '5,10,-15': React.createRef(),
        '5,11,-16': React.createRef(),
        '5,12,-17': React.createRef(),
        '5,13,-18': React.createRef(),
        '5,14,-19': React.createRef(),
        '5,15,-20': React.createRef(),
        '6,-20,14': React.createRef(),
        '6,-19,13': React.createRef(),
        '6,-18,12': React.createRef(),
        '6,-17,11': React.createRef(),
        '6,-16,10': React.createRef(),
        '6,-15,9': React.createRef(),
        '6,-14,8': React.createRef(),
        '6,-13,7': React.createRef(),
        '6,-12,6': React.createRef(),
        '6,-11,5': React.createRef(),
        '6,-10,4': React.createRef(),
        '6,-9,3': React.createRef(),
        '6,-8,2': React.createRef(),
        '6,-7,1': React.createRef(),
        '6,-6,0': React.createRef(),
        '6,-5,-1': React.createRef(),
        '6,-4,-2': React.createRef(),
        '6,-3,-3': React.createRef(),
        '6,-2,-4': React.createRef(),
        '6,-1,-5': React.createRef(),
        '6,0,-6': React.createRef(),
        '6,1,-7': React.createRef(),
        '6,2,-8': React.createRef(),
        '6,3,-9': React.createRef(),
        '6,4,-10': React.createRef(),
        '6,5,-11': React.createRef(),
        '6,6,-12': React.createRef(),
        '6,7,-13': React.createRef(),
        '6,8,-14': React.createRef(),
        '6,9,-15': React.createRef(),
        '6,10,-16': React.createRef(),
        '6,11,-17': React.createRef(),
        '6,12,-18': React.createRef(),
        '6,13,-19': React.createRef(),
        '6,14,-20': React.createRef(),
        '7,-20,13': React.createRef(),
        '7,-19,12': React.createRef(),
        '7,-18,11': React.createRef(),
        '7,-17,10': React.createRef(),
        '7,-16,9': React.createRef(),
        '7,-15,8': React.createRef(),
        '7,-14,7': React.createRef(),
        '7,-13,6': React.createRef(),
        '7,-12,5': React.createRef(),
        '7,-11,4': React.createRef(),
        '7,-10,3': React.createRef(),
        '7,-9,2': React.createRef(),
        '7,-8,1': React.createRef(),
        '7,-7,0': React.createRef(),
        '7,-6,-1': React.createRef(),
        '7,-5,-2': React.createRef(),
        '7,-4,-3': React.createRef(),
        '7,-3,-4': React.createRef(),
        '7,-2,-5': React.createRef(),
        '7,-1,-6': React.createRef(),
        '7,0,-7': React.createRef(),
        '7,1,-8': React.createRef(),
        '7,2,-9': React.createRef(),
        '7,3,-10': React.createRef(),
        '7,4,-11': React.createRef(),
        '7,5,-12': React.createRef(),
        '7,6,-13': React.createRef(),
        '7,7,-14': React.createRef(),
        '7,8,-15': React.createRef(),
        '7,9,-16': React.createRef(),
        '7,10,-17': React.createRef(),
        '7,11,-18': React.createRef(),
        '7,12,-19': React.createRef(),
        '7,13,-20': React.createRef(),
        '8,-20,12': React.createRef(),
        '8,-19,11': React.createRef(),
        '8,-18,10': React.createRef(),
        '8,-17,9': React.createRef(),
        '8,-16,8': React.createRef(),
        '8,-15,7': React.createRef(),
        '8,-14,6': React.createRef(),
        '8,-13,5': React.createRef(),
        '8,-12,4': React.createRef(),
        '8,-11,3': React.createRef(),
        '8,-10,2': React.createRef(),
        '8,-9,1': React.createRef(),
        '8,-8,0': React.createRef(),
        '8,-7,-1': React.createRef(),
        '8,-6,-2': React.createRef(),
        '8,-5,-3': React.createRef(),
        '8,-4,-4': React.createRef(),
        '8,-3,-5': React.createRef(),
        '8,-2,-6': React.createRef(),
        '8,-1,-7': React.createRef(),
        '8,0,-8': React.createRef(),
        '8,1,-9': React.createRef(),
        '8,2,-10': React.createRef(),
        '8,3,-11': React.createRef(),
        '8,4,-12': React.createRef(),
        '8,5,-13': React.createRef(),
        '8,6,-14': React.createRef(),
        '8,7,-15': React.createRef(),
        '8,8,-16': React.createRef(),
        '8,9,-17': React.createRef(),
        '8,10,-18': React.createRef(),
        '8,11,-19': React.createRef(),
        '8,12,-20': React.createRef(),
        '9,-20,11': React.createRef(),
        '9,-19,10': React.createRef(),
        '9,-18,9': React.createRef(),
        '9,-17,8': React.createRef(),
        '9,-16,7': React.createRef(),
        '9,-15,6': React.createRef(),
        '9,-14,5': React.createRef(),
        '9,-13,4': React.createRef(),
        '9,-12,3': React.createRef(),
        '9,-11,2': React.createRef(),
        '9,-10,1': React.createRef(),
        '9,-9,0': React.createRef(),
        '9,-8,-1': React.createRef(),
        '9,-7,-2': React.createRef(),
        '9,-6,-3': React.createRef(),
        '9,-5,-4': React.createRef(),
        '9,-4,-5': React.createRef(),
        '9,-3,-6': React.createRef(),
        '9,-2,-7': React.createRef(),
        '9,-1,-8': React.createRef(),
        '9,0,-9': React.createRef(),
        '9,1,-10': React.createRef(),
        '9,2,-11': React.createRef(),
        '9,3,-12': React.createRef(),
        '9,4,-13': React.createRef(),
        '9,5,-14': React.createRef(),
        '9,6,-15': React.createRef(),
        '9,7,-16': React.createRef(),
        '9,8,-17': React.createRef(),
        '9,9,-18': React.createRef(),
        '9,10,-19': React.createRef(),
        '9,11,-20': React.createRef(),
        '10,-20,10': React.createRef(),
        '10,-19,9': React.createRef(),
        '10,-18,8': React.createRef(),
        '10,-17,7': React.createRef(),
        '10,-16,6': React.createRef(),
        '10,-15,5': React.createRef(),
        '10,-14,4': React.createRef(),
        '10,-13,3': React.createRef(),
        '10,-12,2': React.createRef(),
        '10,-11,1': React.createRef(),
        '10,-10,0': React.createRef(),
        '10,-9,-1': React.createRef(),
        '10,-8,-2': React.createRef(),
        '10,-7,-3': React.createRef(),
        '10,-6,-4': React.createRef(),
        '10,-5,-5': React.createRef(),
        '10,-4,-6': React.createRef(),
        '10,-3,-7': React.createRef(),
        '10,-2,-8': React.createRef(),
        '10,-1,-9': React.createRef(),
        '10,0,-10': React.createRef(),
        '10,1,-11': React.createRef(),
        '10,2,-12': React.createRef(),
        '10,3,-13': React.createRef(),
        '10,4,-14': React.createRef(),
        '10,5,-15': React.createRef(),
        '10,6,-16': React.createRef(),
        '10,7,-17': React.createRef(),
        '10,8,-18': React.createRef(),
        '10,9,-19': React.createRef(),
        '10,10,-20': React.createRef(),
        '11,-20,9': React.createRef(),
        '11,-19,8': React.createRef(),
        '11,-18,7': React.createRef(),
        '11,-17,6': React.createRef(),
        '11,-16,5': React.createRef(),
        '11,-15,4': React.createRef(),
        '11,-14,3': React.createRef(),
        '11,-13,2': React.createRef(),
        '11,-12,1': React.createRef(),
        '11,-11,0': React.createRef(),
        '11,-10,-1': React.createRef(),
        '11,-9,-2': React.createRef(),
        '11,-8,-3': React.createRef(),
        '11,-7,-4': React.createRef(),
        '11,-6,-5': React.createRef(),
        '11,-5,-6': React.createRef(),
        '11,-4,-7': React.createRef(),
        '11,-3,-8': React.createRef(),
        '11,-2,-9': React.createRef(),
        '11,-1,-10': React.createRef(),
        '11,0,-11': React.createRef(),
        '11,1,-12': React.createRef(),
        '11,2,-13': React.createRef(),
        '11,3,-14': React.createRef(),
        '11,4,-15': React.createRef(),
        '11,5,-16': React.createRef(),
        '11,6,-17': React.createRef(),
        '11,7,-18': React.createRef(),
        '11,8,-19': React.createRef(),
        '11,9,-20': React.createRef(),
        '12,-20,8': React.createRef(),
        '12,-19,7': React.createRef(),
        '12,-18,6': React.createRef(),
        '12,-17,5': React.createRef(),
        '12,-16,4': React.createRef(),
        '12,-15,3': React.createRef(),
        '12,-14,2': React.createRef(),
        '12,-13,1': React.createRef(),
        '12,-12,0': React.createRef(),
        '12,-11,-1': React.createRef(),
        '12,-10,-2': React.createRef(),
        '12,-9,-3': React.createRef(),
        '12,-8,-4': React.createRef(),
        '12,-7,-5': React.createRef(),
        '12,-6,-6': React.createRef(),
        '12,-5,-7': React.createRef(),
        '12,-4,-8': React.createRef(),
        '12,-3,-9': React.createRef(),
        '12,-2,-10': React.createRef(),
        '12,-1,-11': React.createRef(),
        '12,0,-12': React.createRef(),
        '12,1,-13': React.createRef(),
        '12,2,-14': React.createRef(),
        '12,3,-15': React.createRef(),
        '12,4,-16': React.createRef(),
        '12,5,-17': React.createRef(),
        '12,6,-18': React.createRef(),
        '12,7,-19': React.createRef(),
        '12,8,-20': React.createRef(),
        '13,-20,7': React.createRef(),
        '13,-19,6': React.createRef(),
        '13,-18,5': React.createRef(),
        '13,-17,4': React.createRef(),
        '13,-16,3': React.createRef(),
        '13,-15,2': React.createRef(),
        '13,-14,1': React.createRef(),
        '13,-13,0': React.createRef(),
        '13,-12,-1': React.createRef(),
        '13,-11,-2': React.createRef(),
        '13,-10,-3': React.createRef(),
        '13,-9,-4': React.createRef(),
        '13,-8,-5': React.createRef(),
        '13,-7,-6': React.createRef(),
        '13,-6,-7': React.createRef(),
        '13,-5,-8': React.createRef(),
        '13,-4,-9': React.createRef(),
        '13,-3,-10': React.createRef(),
        '13,-2,-11': React.createRef(),
        '13,-1,-12': React.createRef(),
        '13,0,-13': React.createRef(),
        '13,1,-14': React.createRef(),
        '13,2,-15': React.createRef(),
        '13,3,-16': React.createRef(),
        '13,4,-17': React.createRef(),
        '13,5,-18': React.createRef(),
        '13,6,-19': React.createRef(),
        '13,7,-20': React.createRef(),
        '14,-20,6': React.createRef(),
        '14,-19,5': React.createRef(),
        '14,-18,4': React.createRef(),
        '14,-17,3': React.createRef(),
        '14,-16,2': React.createRef(),
        '14,-15,1': React.createRef(),
        '14,-14,0': React.createRef(),
        '14,-13,-1': React.createRef(),
        '14,-12,-2': React.createRef(),
        '14,-11,-3': React.createRef(),
        '14,-10,-4': React.createRef(),
        '14,-9,-5': React.createRef(),
        '14,-8,-6': React.createRef(),
        '14,-7,-7': React.createRef(),
        '14,-6,-8': React.createRef(),
        '14,-5,-9': React.createRef(),
        '14,-4,-10': React.createRef(),
        '14,-3,-11': React.createRef(),
        '14,-2,-12': React.createRef(),
        '14,-1,-13': React.createRef(),
        '14,0,-14': React.createRef(),
        '14,1,-15': React.createRef(),
        '14,2,-16': React.createRef(),
        '14,3,-17': React.createRef(),
        '14,4,-18': React.createRef(),
        '14,5,-19': React.createRef(),
        '14,6,-20': React.createRef(),
        '15,-20,5': React.createRef(),
        '15,-19,4': React.createRef(),
        '15,-18,3': React.createRef(),
        '15,-17,2': React.createRef(),
        '15,-16,1': React.createRef(),
        '15,-15,0': React.createRef(),
        '15,-14,-1': React.createRef(),
        '15,-13,-2': React.createRef(),
        '15,-12,-3': React.createRef(),
        '15,-11,-4': React.createRef(),
        '15,-10,-5': React.createRef(),
        '15,-9,-6': React.createRef(),
        '15,-8,-7': React.createRef(),
        '15,-7,-8': React.createRef(),
        '15,-6,-9': React.createRef(),
        '15,-5,-10': React.createRef(),
        '15,-4,-11': React.createRef(),
        '15,-3,-12': React.createRef(),
        '15,-2,-13': React.createRef(),
        '15,-1,-14': React.createRef(),
        '15,0,-15': React.createRef(),
        '15,1,-16': React.createRef(),
        '15,2,-17': React.createRef(),
        '15,3,-18': React.createRef(),
        '15,4,-19': React.createRef(),
        '15,5,-20': React.createRef(),
        '16,-20,4': React.createRef(),
        '16,-19,3': React.createRef(),
        '16,-18,2': React.createRef(),
        '16,-17,1': React.createRef(),
        '16,-16,0': React.createRef(),
        '16,-15,-1': React.createRef(),
        '16,-14,-2': React.createRef(),
        '16,-13,-3': React.createRef(),
        '16,-12,-4': React.createRef(),
        '16,-11,-5': React.createRef(),
        '16,-10,-6': React.createRef(),
        '16,-9,-7': React.createRef(),
        '16,-8,-8': React.createRef(),
        '16,-7,-9': React.createRef(),
        '16,-6,-10': React.createRef(),
        '16,-5,-11': React.createRef(),
        '16,-4,-12': React.createRef(),
        '16,-3,-13': React.createRef(),
        '16,-2,-14': React.createRef(),
        '16,-1,-15': React.createRef(),
        '16,0,-16': React.createRef(),
        '16,1,-17': React.createRef(),
        '16,2,-18': React.createRef(),
        '16,3,-19': React.createRef(),
        '16,4,-20': React.createRef(),
        '17,-20,3': React.createRef(),
        '17,-19,2': React.createRef(),
        '17,-18,1': React.createRef(),
        '17,-17,0': React.createRef(),
        '17,-16,-1': React.createRef(),
        '17,-15,-2': React.createRef(),
        '17,-14,-3': React.createRef(),
        '17,-13,-4': React.createRef(),
        '17,-12,-5': React.createRef(),
        '17,-11,-6': React.createRef(),
        '17,-10,-7': React.createRef(),
        '17,-9,-8': React.createRef(),
        '17,-8,-9': React.createRef(),
        '17,-7,-10': React.createRef(),
        '17,-6,-11': React.createRef(),
        '17,-5,-12': React.createRef(),
        '17,-4,-13': React.createRef(),
        '17,-3,-14': React.createRef(),
        '17,-2,-15': React.createRef(),
        '17,-1,-16': React.createRef(),
        '17,0,-17': React.createRef(),
        '17,1,-18': React.createRef(),
        '17,2,-19': React.createRef(),
        '17,3,-20': React.createRef(),
        '18,-20,2': React.createRef(),
        '18,-19,1': React.createRef(),
        '18,-18,0': React.createRef(),
        '18,-17,-1': React.createRef(),
        '18,-16,-2': React.createRef(),
        '18,-15,-3': React.createRef(),
        '18,-14,-4': React.createRef(),
        '18,-13,-5': React.createRef(),
        '18,-12,-6': React.createRef(),
        '18,-11,-7': React.createRef(),
        '18,-10,-8': React.createRef(),
        '18,-9,-9': React.createRef(),
        '18,-8,-10': React.createRef(),
        '18,-7,-11': React.createRef(),
        '18,-6,-12': React.createRef(),
        '18,-5,-13': React.createRef(),
        '18,-4,-14': React.createRef(),
        '18,-3,-15': React.createRef(),
        '18,-2,-16': React.createRef(),
        '18,-1,-17': React.createRef(),
        '18,0,-18': React.createRef(),
        '18,1,-19': React.createRef(),
        '18,2,-20': React.createRef(),
        '19,-20,1': React.createRef(),
        '19,-19,0': React.createRef(),
        '19,-18,-1': React.createRef(),
        '19,-17,-2': React.createRef(),
        '19,-16,-3': React.createRef(),
        '19,-15,-4': React.createRef(),
        '19,-14,-5': React.createRef(),
        '19,-13,-6': React.createRef(),
        '19,-12,-7': React.createRef(),
        '19,-11,-8': React.createRef(),
        '19,-10,-9': React.createRef(),
        '19,-9,-10': React.createRef(),
        '19,-8,-11': React.createRef(),
        '19,-7,-12': React.createRef(),
        '19,-6,-13': React.createRef(),
        '19,-5,-14': React.createRef(),
        '19,-4,-15': React.createRef(),
        '19,-3,-16': React.createRef(),
        '19,-2,-17': React.createRef(),
        '19,-1,-18': React.createRef(),
        '19,0,-19': React.createRef(),
        '19,1,-20': React.createRef(),
        '20,-20,0': React.createRef(),
        '20,-19,-1': React.createRef(),
        '20,-18,-2': React.createRef(),
        '20,-17,-3': React.createRef(),
        '20,-16,-4': React.createRef(),
        '20,-15,-5': React.createRef(),
        '20,-14,-6': React.createRef(),
        '20,-13,-7': React.createRef(),
        '20,-12,-8': React.createRef(),
        '20,-11,-9': React.createRef(),
        '20,-10,-10': React.createRef(),
        '20,-9,-11': React.createRef(),
        '20,-8,-12': React.createRef(),
        '20,-7,-13': React.createRef(),
        '20,-6,-14': React.createRef(),
        '20,-5,-15': React.createRef(),
        '20,-4,-16': React.createRef(),
        '20,-3,-17': React.createRef(),
        '20,-2,-18': React.createRef(),
        '20,-1,-19': React.createRef(),
        '20,0,-20': React.createRef(),
    });

    // const [selectedCityBuildingChoices, setSelectedCityBuildingChoices] = useState(null);

    const descriptions = selectedCity?.available_buildings_to_descriptions;

    const unsortedSelectedCityBuildingChoices = selectedCity?.available_building_names;

    let selectedCityBuildingChoices = [];

    if (descriptions && Object.keys(descriptions).length > 0) {
        selectedCityBuildingChoices = unsortedSelectedCityBuildingChoices?.sort((buildingName1, buildingName2) => {
            const description1 = descriptions[buildingName1];
            const description2 = descriptions[buildingName2];
        
            const getTypeOrder = (type) => {
                switch (type) {
                    case 'yield':
                        return 1;
                    case 'wonder_cost':
                        return 2;
                    case 'strength':
                        return 3;
                    default:
                        return 4;
                }
            };
        
            const typeOrder1 = getTypeOrder(description1?.type);
            const typeOrder2 = getTypeOrder(description2?.type);
        
            if (typeOrder1 !== typeOrder2) {
                return typeOrder1 - typeOrder2;
            } else {
                return description2?.value - description1?.value;
            }
        });
    }
    else {
        selectedCityBuildingChoices = unsortedSelectedCityBuildingChoices;
    }

    const selectedCityBuildingQueue = selectedCity?.buildings_queue;
    const selectedCityBuildings = selectedCity?.buildings?.map(building => building.name);

    const selectedCityUnitChoices = selectedCity?.available_units;

    const refreshSelectedCity = (newGameState) => {
        if (selectedCity?.id) {
            setSelectedCity(newGameState.hexes[selectedCity.hex].city);
        }
    }

    useEffect(() => {
        if (!!hoveredBuilding) {
            setHoveredUnit(null);
            setHoveredTech(null);
        }
    }, [hoveredBuilding])

    useEffect(() => {
        if (!!hoveredUnit) {
            setHoveredBuilding(null);
            setHoveredTech(null);
        }
    }, [hoveredUnit])

    useEffect(() => {
        if (!!hoveredTech) {
            setHoveredBuilding(null);
            setHoveredUnit(null);
        }
    }, [hoveredTech])

    const toggleFoundingCity = () => {
        setFoundingCity(!foundingCity);
    }

    const fetchDeclineViewGameState = async () => {
        setDeclineViewGameState(null);
        console.log("Fetching decline state.");
        const response = await fetch(`${URL}/api/decline_view/${gameId}`);
        const data = await response.json();
        setDeclineViewGameState(data.game_state);
        console.log("Fetched: ", declineViewGameState);
    }

    useEffect(() => {
        if (!declineViewGameState) {
            console.error("Decline view game state not fetched yet.");
            return;
        }
        if (declineOptionsView) {
            setNonDeclineViewGameState(gameState);
            setGameState(declineViewGameState);
            setTechChoiceDialogOpen(false);
            setGreatPersonChoiceDialogOpen(false);
        } else {
            // If we are toggling back from the decline view
            setGameState(nonDeclineViewGameState);
            setSelectedCity(null);
        }
    }, [declineOptionsView])

    const handleClickEndTurn = () => {
        const data = { player_num: playerNum };

        fetch(`${URL}/api/end_turn/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        });
    }

    const handleClickUnendTurn = () => {
        const data = {
            player_num: playerNum,
        }

        fetch(`${URL}/api/unend_turn/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },

            body: JSON.stringify(data),
        })
    }

    const submitPlayerInput = async (playerInput) => {
        if (engineState !== EngineStates.PLAYING) {return;}

        const data = {
            player_num: playerNum,
            turn_num: gameStateRef.current.turn_num,
            player_input: playerInput,
        }
        fetch(playerApiUrl, {
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
        if (engineState !== EngineStates.PLAYING) {return;}

        const playerInput = {
            'tech_name': tech.name,
            'move_type': 'choose_tech',
        }

        submitPlayerInput(playerInput).then(() => setTechChoiceDialogOpen(false));
    }
   
    useEffect(() => {
        fetch(`${URL}/api/templates`)
            .then(response => response.json())
            .then(data => setTemplates(data));
    }, [])

    const showSingleMovementArrow = (fromHexCoords, toHexCoords, arrowType = null) => {

        const fromHexClientRef = hexRefs?.current?.[fromHexCoords]?.current?.getBoundingClientRect();
        const toHexClientRef = hexRefs?.current?.[toHexCoords]?.current?.getBoundingClientRect();

        if (!fromHexClientRef || !toHexClientRef) {
            return;
        }

        const dx = toHexClientRef.left - fromHexClientRef.left;
        const dy = toHexClientRef.top - fromHexClientRef.top;
        const distance = Math.sqrt(dx * dx + dy * dy);

        // Create an arrow element and set its position and rotation
        const arrow = document.createElement('div');
        arrow.className = 'arrow';
        arrow.style.position = 'absolute'; // Make sure it's set to absolute
        arrow.style.left = `${fromHexClientRef.left + window.scrollX - 2}px`;
        arrow.style.top = `${fromHexClientRef.top + window.scrollY - 2}px`;
        arrow.style.width = `${distance}px`; // Set the length of the arrow

        const angle = Math.atan2(dy, dx) * (180 / Math.PI);
        arrow.style.transform = `rotate(${angle}deg)`;
        arrow.style.transformOrigin = "0 50%";

        if (arrowType === 'attack') {
            arrow.classList.add("attack");
        } 

        document.body.appendChild(arrow);

        setTimeout(() => {
            document.body.removeChild(arrow);
        }, MAX_ANIMATION_DELAY * 0.67);
    }

    const showMovementArrows = (coords) => {
        if (!coords || coords.length < 2) {
            return;
        }

        for (let i = 0; i < coords.length - 1; i++) {
            showSingleMovementArrow(coords[i], coords[i + 1]);
        }
    }

    const waitForFrame = async (frameNum) => {
        if (animationFrameLastPlayedRef.current !== frameNum) {
            console.log(now(), "Frame", frameNum, "delayed.")
            while (animationFrameLastPlayedRef.current !== frameNum) { 
                await new Promise(resolve => setTimeout(resolve, 20));
            }
        }
    };

    const asyncLaunchAnimationFrame = async (frameNum) => {
        try {
            // console.log(now(), "Fetching frame", frameNum);
            const response = await fetch(`${URL}/api/movie/frame/${gameId}/${frameNum}?player_num=${playerNum}`);
            const json = await response.json();
            // console.log(now(), "Fetched frame", frameNum);

            // Wait for previous frame to give us permission to go ahead.
            await waitForFrame(frameNum - 1);

            // console.log(now(), "Showing frame", frameNum);
            if (!json.data) {
                console.error("No data in frame", frameNum);
                return;
            }
            switch (json.data.type) {
                case 'UnitMovement':
                    playMoveSound(moveSound, volume);
                    showMovementArrows(json.data.coords);
                    setGameState(json.game_state);
                    break;

                case 'UnitAttack':
                    if (json.data.attack_type === 'melee') {
                        playMeleeAttackSound(meleeAttackSound, volume);
                    } else if (json.data.attack_type === 'ranged') {
                        playRangedAttackSound(rangedAttackSound, volume);
                    } else if (json.data.attack_type === 'gunpowder_melee') {
                        playGunpowderMeleeAttackSound(gunpowderMeleeAttackSound, volume);
                    } else if (json.data.attack_type === 'gunpowder_ranged') {
                        playGunpowderRangedAttackSound(gunpowderRangedAttackSound, volume);
                    }
                    showSingleMovementArrow(json.data.start_coords, json.data.end_coords, 'attack');
                    setGameState(json.game_state);
                    break;
                default:
                    console.error("Unknown animation type", json.data.type);
            }
            // Wait MIN_ANIMATION_DELAY before saying we're done with this frame.
            // So it definitely displays for at least that long.
            await new Promise(resolve => setTimeout(resolve, MIN_ANIMATION_DELAY));
            console.log(now(), ": Animation done frame", frameNum)
            animationFrameLastPlayedRef.current = frameNum;
        } catch (error) {
            console.error('Error fetching movie frame:', error);
        }
    }

    const finalAnimationFrame = async (lastFrameToAwait) => {
        await waitForFrame(lastFrameToAwait);
        console.log("Animations took", (Date.now() - animationsLastStartedAtRef.current) / 1000, "seconds");
        const finalGameState = animationFinalStateRef.current;
        setGameState(finalGameState);
        refreshSelectedCity(finalGameState);
        const { myCiv } = getMyInfo(finalGameState);
        sciencePopupIfNeeded(myCiv);
        greatPersonPopupIfNeeded(myCiv);
    }

    const triggerAnimationsInner = async () => {
        animationsLastStartedAtRef.current = Date.now();
        animationFrameLastPlayedRef.current = 0;

        for (let frameNum = 1; frameNum <= animationTotalFrames; frameNum++) {
            // console.log(now(), "Playing frame", frameNum);
            // Check if any other process has cancelled the animations by changing the engine state to something else.
            if (engineStateRef.current !== EngineStates.ANIMATING) {
                console.log("Canceling animation");
                finalAnimationFrame(frameNum - 1);
                return;
            }
            asyncLaunchAnimationFrame(frameNum);
            await new Promise(resolve => setTimeout(resolve, animationActiveDelay));
        }
        console.log(now(), ": Final animation frame.");
        finalAnimationFrame(animationTotalFrames).then(() => {
            transitionEngineState(EngineStates.PLAYING, EngineStates.ANIMATING);
        });
    }

    useEffect(() => {
        if (engineState === EngineStates.ANIMATING) {
            triggerAnimationsInner();
        }
    }, [engineState])

    const triggerAnimations = async (finalGameState) => {
        if (engineState === EngineStates.ANIMATING) {
            console.error("Already animating, but tried to start another animation!")
            return;
        }
        // Record the game state to go back to after animations.
        animationFinalStateRef.current = finalGameState;
        // Just need to set the engineState.
        // And the useEffect will notice and do the real work.
        transitionEngineState(EngineStates.ANIMATING);
    }

    const cancelAnimations = () => {
        console.log("Manually cancelling animations")
        setEngineState(EngineStates.PLAYING, EngineStates.ANIMATING);
    }

    const greatPersonPopupIfNeeded = (civ) => {
        if (civ?.great_people_choices?.length > 0) {
            setGreatPersonChoiceDialogOpen(true);
        }
    }

    const sciencePopupIfNeeded = (civ) => {
        if (civ?.researching_tech_name === null) {
            setTechChoiceDialogOpen(true);
        }
    }

    const LineOnHexes = ({from, to, jitterAmnt, className, color}) => {
        const fromHexRef = hexRefs?.current[from].current;
        const toHexRef = hexRefs?.current[to].current ;

        if (!fromHexRef || !toHexRef) {return;}
        const fromHexClientRect = fromHexRef.getBoundingClientRect();
        const toHexClientRect = toHexRef.getBoundingClientRect();

        const dx = toHexClientRect.left - fromHexClientRect.left;
        const dy = toHexClientRect.top - fromHexClientRect.top;
        const angleRads = Math.atan2(dy, dx);
        const jitteredFrom = {
            left: fromHexClientRect.left + jitterAmnt * Math.sin(angleRads),
            top: fromHexClientRect.top - jitterAmnt * Math.cos(angleRads),
        }
        const Jittereddx = toHexClientRect.left - jitteredFrom.left;
        const Jittereddy = toHexClientRect.top - jitteredFrom.top;
        const JitteredAngleDegs = Math.atan2(Jittereddy, Jittereddx) * (180 / Math.PI);

        const distance = Math.sqrt(Jittereddx * Jittereddx + Jittereddy * Jittereddy);
        return <div className={`map-line ${className}`} style={{
            left: `${jitteredFrom.left + window.scrollX - 2}px`,
            top: `${jitteredFrom.top + window.scrollY - 2}px`,
            width: `${distance}px`, // Set the length of the arrow
            transform: `rotate(${JitteredAngleDegs}deg)`,
            transformOrigin: "0 50%",
            backgroundColor: color,
        }}>
        </div>

    }

    const FlagArrow = ({hex}) => {
        const unit = hex.units[0]
        const destCoords = unit.closest_target
        if (!destCoords) {return;}
        const jitterAmnt = 20 * (Math.sin(hex.q * 13 + hex.r * 23 + hex.s * 31));
        return <LineOnHexes from={`${hex.q},${hex.r},${hex.s}`} to={destCoords} jitterAmnt={jitterAmnt} className='flag-arrow' color='#111c'/>
    }

    const FlagArrows = ({hexagons, myCiv, civsById}) => {
        if (!showFlagArrows) { return; }
        return (
            <div className="flag-arrows-container">
                {hexagons.filter(hex => hex.units?.length && civsById?.[hex.units?.[0]?.civ_id]?.name === myCiv?.name)
                    .map((hex, index) => <FlagArrow key={index} hex={hex} />)}
            </div>
        );
    }

    const PuppetArrow = ({city}) => {
        // Note this lives in an svg.
        const destinationCoords = city.territory_parent_coords;
        const myCoords = city.hex;
        const destRef = hexRefs?.current[destinationCoords].current;
        const myRef = hexRefs?.current[myCoords].current;
        const svgElement = document.querySelector('svg.grid');

        if (!destRef || !myRef || !svgElement) {return;}
    
        /////////////////////////////////
        // Some GPT4 magic I don't understand
        function screenToSVG(x, y, svgEl) {
            let pt = svgEl.createSVGPoint();
            pt.x = x;
            pt.y = y;
            return pt.matrixTransform(svgEl.getScreenCTM().inverse());
        }
        // Get the bounding rectangle of the reference in screen coordinates
        const myRect = myRef.getBoundingClientRect();
        const destRect = destRef.getBoundingClientRect();
        // Calculate the center position in screen coordinates
        const myCenterX = myRect.left + myRect.width / 2;
        const myCenterY = myRect.top + myRect.height / 2;
        const destCenterX = destRect.left + destRect.width / 2;
        const destCenterY = destRect.top + destRect.height / 2;
        // Convert screen coordinates to SVG coordinates
        const mySVGPoint = screenToSVG(myCenterX, myCenterY, svgElement);
        const destSVGPoint = screenToSVG(destCenterX, destCenterY, svgElement);
        /////////////////////////////////

        const civ = civsById[city.civ_id]
        const civTemplate = templates.CIVS[civ.name]
        return <line x1={mySVGPoint.x} y1={mySVGPoint.y} x2={destSVGPoint.x} y2={destSVGPoint.y} 
            stroke={civTemplate.secondary_color} strokeWidth=".5" strokeOpacity={0.9}
            />
    }

    // Add event listeners for flag arrows when the component mounts
    useEffect(() => {
        // Event handler for keydown event for the flag arrows
        const handleKeyDown = (event) => {
            if (event.key === 'f' || event.key === 'F') {
                if (engineState !== EngineStates.PLAYING) {return;}
                console.log("Showing flag arrows")
                setShowFlagArrows(true);
            }
        };

        // Event handler for keydown event for the flag arrows
        const handleKeyUp = (event) => {
            if (event.key === 'f' || event.key === 'F') {
                flagArrowsTimeoutRef.current = setTimeout(() => setShowFlagArrows(false), 200);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);

        // Remove event listeners on cleanup
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('keyup', handleKeyUp);
        };
    }, [engineState]);

    const isFriendlyCity = (city) => {
        if (declineOptionsView) {
            return city?.is_decline_view_option;
        }
        if (engineState === EngineStates.GAME_OVER) {
            return true;
        }
        if (playerNum !== null && playerNum !== undefined) {
            return civsByIdRef.current?.[city.civ_id]?.game_player?.player_num === playerNum

        }
        return false;
    }

    const handleMouseOverCity = (city) => {
        setHoveredCity(city);
    };

    const handleClickCity = (city) => {
        if (engineState !== EngineStates.PLAYING && engineState !== EngineStates.GAME_OVER) {return;}
        if (city.id === selectedCity?.id) {
            setSelectedCity(null);
        }
        else {
            if (isFriendlyCity(city)) {
                playCitySound(medievalCitySound, modernCitySound, myCiv?.advancement_level >= 7);
                setSelectedCity(city);
            }
        }
    };

    const handleFoundCapital = () => {
        if (gameState.special_mode_by_player_num[playerNum] === 'starting_location') {
            const data = {
                player_num: playerNum,
                city_id: selectedCity.id,
            }
            fetch(`${URL}/api/starting_location/${gameId}`, {
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
        } else if (declineOptionsView) {
            const data = {
                player_num: playerNum,
                turn_num: gameStateRef.current.turn_num,
                player_input: {
                    coords: selectedCity.hex,
                    move_type: 'choose_decline_option',
                },
            }
            fetch(playerApiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
            }).then(response => response.json())
                .then(data => {
                    const myNewCiv = data.game_state.civs_by_id?.[data.game_state.game_player_by_player_num[playerNum].civ_id];
                    const success = myNewCiv?.name === civsByIdRef.current[selectedCity.civ_id].name;
                    if (data.game_state && success) {
                        setGameState(data.game_state);
                        setNonDeclineViewGameState(data.game_state);  // Clear the old cached non-decline game state.
                        refreshSelectedCity(data.game_state);
                        setDeclineOptionsView(false);
                        setTechListDialogOpen(true);
                    } else if (data.game_state && !success) {
                        setDeclineFailedDialogOpen(true);
                    } else {
                        console.error("No data.game_state found in response.")
                    }
                });

        }
    }


    const City = ({ city, isHovered, isSelected, isUnitInHex, everControlled }) => {
        const civTemplate = templates.CIVS[civsById?.[city.civ_id]?.name]
        
        const primaryColor = civTemplate?.primary_color;
        const secondaryColor = civTemplate?.secondary_color;
    
        const friendly = isFriendlyCity(city);
        const puppet = city.territory_parent_coords;
    
        const finalPrimaryColor = primaryColor;
        const finalSecondaryColor = secondaryColor;
        const colors = 
            {'wood': '#e0b096',
            'food': '#ccffaa',
            'metal': '#bbbbbb',
            'science': '#b0e0e6'}
        const focusColor = friendly ? colors[city.focus] : finalPrimaryColor;
        let buildingText;
        let buildingIconUnit;
        if (city.buildings_queue.length === 0) {
            buildingText = "??";
            buildingIconUnit = null;
        } else if (unitTemplatesByBuildingName[city.buildings_queue[0]]) {
            buildingText = "";
            buildingIconUnit = unitTemplatesByBuildingName[city.buildings_queue[0]].name;
        } else {
            buildingText = city.buildings_queue[0].slice(0, 2);
            buildingIconUnit = null;
        }
        const buildingImage = buildingIconUnit && `/images/${lowercaseAndReplaceSpacesWithUnderscores(buildingIconUnit)}.svg`; 
 
        const unitText = !city.infinite_queue_unit && "??";
        const unitIconUnit = city.infinite_queue_unit;    
        const unitImage = unitIconUnit && `/images/${lowercaseAndReplaceSpacesWithUnderscores(unitIconUnit)}.svg`;


        const cityBoxCanvas = {'width': 8, 'height': 4};
        const cityBoxPanel = {'width': (puppet ? 5 : 6), 'height': 2};
        const cityCircleRadius = 0.75;

        const cityBoxPanelBottomY = cityBoxCanvas.height / 2 + cityBoxPanel.height / 2
        const cityCirclesY = (cityBoxCanvas.height - cityBoxPanel.height) / 2
        const cityCirclesTextY = cityCirclesY + 0.05;
        return (
            <>
                {isHovered && <circle cx="0" cy={`${isUnitInHex ? -1 : 0}`} r="2.25" fill="none" stroke="white" strokeWidth="0.2"/>}
                {isSelected && <circle cx="0" cy={`${isUnitInHex ? -1 : 0}`} r="2.25" fill="none" stroke="black" strokeWidth="0.2"/>}
                {city.under_siege_by_civ && <svg width="6" height="6" viewBox="0 0 6 6" x={-3} y={isUnitInHex ? -4 : -3}>
                        <image href="/images/fire.svg" x="0" y="0" height="6" width="6" />
                    </svg>
                }
                <svg width={cityBoxCanvas.width} height={cityBoxCanvas.height} viewBox={`0 0 ${cityBoxCanvas.width} ${cityBoxCanvas.height}`} x={-cityBoxCanvas.width / 2} y={-3.5} onMouseEnter={() => handleMouseOverCity(city)} onClick={() => handleClickCity(city)} style={{...(friendly ? {cursor : 'pointer'} : {})}}>
                    {/* Background rectangle */}
                    <rect width={cityBoxPanel.width} height={cityBoxPanel.height} x={(cityBoxCanvas.width - cityBoxPanel.width) / 2} y={(cityBoxCanvas.height - cityBoxPanel.height) / 2} fill={finalPrimaryColor} stroke={finalSecondaryColor} strokeWidth={0.2} {...(puppet ? {rx: "1", ry: "1"} : {})}/>
                    {/* Pointer triangle. make the fill and the stroke separately so the fill can cover the border of the main box without the stroke looking dumb */}
                    <path d={`M3.3,${cityBoxPanelBottomY-0.12} L4,${cityBoxPanelBottomY + 1} L4.7,${cityBoxPanelBottomY-0.12}`} style={{opacity: 1.0, fill: finalPrimaryColor, stroke: "none", strokeWidth: 0.2}} />
                    <path d={`M3.3,${cityBoxPanelBottomY} L4,${cityBoxPanelBottomY + 1} L4.7,${cityBoxPanelBottomY}`} style={{strokeOpacity: 1.0, stroke: finalSecondaryColor, strokeWidth: 0.2}} />
                    <text x="50%" y="2.3" dominantBaseline="middle" textAnchor="middle" style={{fontSize: "0.8px"}}>
                        {city.name}
                    </text>

                    {/* Populatoin */}
                    <circle cx="50%" cy={cityCirclesY} r={cityCircleRadius} fill={focusColor} stroke={finalSecondaryColor} strokeWidth="0.1"/>
                    <image opacity={.7} href={workerIcon} x="3.5" y="0.4" height="1" width="1" />
                    <text x="50%" y={cityCirclesTextY} dominantBaseline="middle" textAnchor="middle" style={{fontSize: "1.2px"}}>
                        {city.population}
                    </text>              

                    {friendly && puppet === null &&
                        <>
                            {/* Wood */}
                            <circle cx="1.7" cy={cityCirclesY} r={cityCircleRadius} fill={colors.wood} stroke={finalSecondaryColor} strokeWidth="0.1"/>
                            <image href={buildingImage} x={1.2} y={0.45} height="1" width="1" />
                            <text x="1.7" y={cityCirclesTextY} dominantBaseline="middle" textAnchor="middle" style={{fontSize: "0.8px"}}>
                                {buildingText}
                            </text>    

                            {/* Metal */}
                            <circle cx="6.3" cy={cityCirclesY} r={cityCircleRadius} fill={colors.metal} stroke={finalSecondaryColor} strokeWidth="0.1"/>
                            <image href={unitImage} x={5.8} y={0.45} height="1" width="1" />
                            <text x="6.3" y={cityCirclesTextY} dominantBaseline="middle" textAnchor="middle" style={{fontSize: "0.8px"}}>
                                {unitText}
                            </text>    
                        </>
                    }
                    {!everControlled && 
                        <image href={vpImage} x={5.75} y={1.1} height="1" />
                    }
                    
                </svg>
                {declineOptionsView && city.is_decline_view_option && <>
                    <image href={vitalityImg} x="-1.8" y="-1" height="3.6" width="3.6" />
                    <text x="0" y="0.4" dominantBaseline="middle" textAnchor="middle" style={{fontSize: "1.2px"}}>
                        {Math.floor(city.revolting_starting_vitality * 100)}%
                    </text>
                    </>
                }
            </>
        );
    };

    const Camp = ({ camp, isUnitInHex }) => {
        const primaryColor = 'red';
        const secondaryColor = 'black';
    
        return (
            <>
                {camp.under_siege_by_civ && <svg width="5" height="5" viewBox="0 0 5 5" x={-2.5} y={isUnitInHex ? -3.5 : -2.5}>
                        <image href="/images/fire.svg" x="0" y="0" height="5" width="5" />
                    </svg>
                }
                <svg width="3" height="3" viewBox="0 0 3 3" x={-1.5} y={isUnitInHex ? -2.5 : -1.5} onMouseEnter={() => handleMouseOverCity(camp)}>
                    <polygon points="1.5,0 3,3 0,3" fill={primaryColor} stroke={secondaryColor} strokeWidth={0.5} />
                </svg>
            </>
        );
    };

    const Unit = ({ unit, isCityInHex }) => {
        const unitCivTemplate = templates.CIVS[civsById?.[unit.civ_id]?.name]

        const primaryColor = unitCivTemplate?.primary_color;
        const secondaryColor = unitCivTemplate?.secondary_color;
        const unitImage = `/images/${lowercaseAndReplaceSpacesWithUnderscores(unit.name)}.svg`; // Path to the unit SVG image
    
        const scale = isCityInHex ? 0.95 : 1.4;
        let healthPercentage = (unit.health / 100) % 1; // Calculate health as a percentage
        if (healthPercentage === 0) {
            healthPercentage = 1;
        }

        const finalPrimaryColor = primaryColor;
        const finalSecondaryColor = secondaryColor;

        return (
            <svg width={`${4*scale}`} height={`${4*scale}`} viewBox={`0 0 ${4*scale} ${4*scale}`} x={-2*scale} y={-2*scale + (isCityInHex ? 1 : 0)}>
                <circle opacity={unit.done_attacking ? 0.5 : 1.0} cx={`${2*scale}`} cy={`${2*scale}`} r={`${scale}`} fill={finalPrimaryColor} stroke={finalSecondaryColor} strokeWidth={0.3} />
                <image opacity={unit.done_attacking ? 0.5 : 1.0} href={unitImage} x={`${scale}`} y={`${scale}`} height={`${2*scale}`} width={`${2*scale}`} />
                <rect x={`${scale}`} y={`${3.4*scale}`} width={`${2*scale}`} height={`${0.2*scale}`} fill="#ff0000" /> {/* Total health bar */}
                <rect x={`${scale}`} y={`${3.4*scale}`} width={`${2*scale*healthPercentage}`} height={`${0.2*scale}`} fill="#00ff00" /> {/* Current health bar */}
                {unit.stack_size > 1 && <circle cx={`${2*scale + 0.8*scale}`} cy={`${3.5*scale - 0.8*scale}`} r={`${scale/2}`} fill="white" stroke="black" strokeWidth={0.1} style={{ zIndex: 99999 }} />}
                {unit.stack_size > 1 && <text x={`${2.8*scale}`} y={`${2.8*scale}`} style={{ fontSize: `${scale}px`, textAnchor: "middle", dominantBaseline: "middle", zIndex: 99999 }}>{unit.stack_size}</text>}
            </svg>
        );
    };

    const TargetMarker = ({ purple }) => {
        return (
            <svg width="3" height="3" viewBox="0 0 3 3" x={-1.5} y={-1.5}>
                <image href={purple ? "/images/purple_flag.svg" : "/images/flag.svg"} x="0" y="0" height="3" width="3" />
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
            'foundable': '#44AA44',
            'unfoundable': '#FF4444',
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
        setHoveredHex(null);
    };

    const handleMouseOverHex = (hex) => {
        setHoveredHex(hex);
        let hoveredCivPicked = false;
        if (hex.city) {
            const cityCiv = civsByIdRef.current[hex?.city?.civ_id]
            setHoveredCiv(cityCiv);
            setHoveredGamePlayer(civsByIdRef.current[hex?.city?.civ_id]?.game_player?.username);
            setHoveredCity(hex.city)
            hoveredCivPicked = true;
        }
        else {
            setHoveredCity(null);
        }
        if (hex?.units?.length > 0) {
            const unit = hex?.units?.[0];
            const civ = civsByIdRef.current[unit?.civ_id]
            setHoveredUnit(unit);
            setHoveredCiv(civ);
            setHoveredGamePlayer(civsByIdRef.current[hex?.units?.[0]?.civ_id]?.game_player?.username);
            hoveredCivPicked = true;
        }
        else {
            setHoveredUnit(null);
        }
        if (!hoveredCivPicked) {
            setHoveredCiv(null);
            setHoveredGamePlayer(null);
        }
    };

    const hexesAreEqual = (hex1, hex2) => {
        return hex1?.q === hex2?.q && hex1?.r === hex2?.r && hex1?.s === hex2?.s;
    }

    const handleClickHex = (hex, event) => {
        if (foundingCity) {
            if (!hex?.is_foundable_by_civ?.[myCivId]) {
                return;
            }
            const playerInput = {
                'move_type': 'found_city',
                'city_id': generateUniqueId(),
                'coords': `${hex.q},${hex.r},${hex.s}`,
            }
            submitPlayerInput(playerInput).then(() => setFoundingCity(false));
        }
        else {
            setHoveredCity(null);
        }   
    };

    const handleSelectGreatPerson = (greatPerson) => {
        const playerInput = {
            'move_type': 'select_great_person',
            'great_person_name': greatPerson.name,
        }
        submitPlayerInput(playerInput).then(() => setGreatPersonChoiceDialogOpen(false));
    }

    const totalHexYields = (yields) => {
        return Object.values(yields).reduce((a, b) => a + b, 0);
    }

    const displayGameState = (gameState) => {
        // return <Typography>{JSON.stringify(gameState)}</Typography>
        const hexagons = Object.values(gameState.hexes).sort((a, b) => {
            // This sorts them so ones higher on teh screen come first.
            // So that city banners can extend outside their hexagon upwards and overlap correctly.
            return a.r - b.r + 0.1 * (a.q - b.q);
        });

        const canFoundCity = hexagons.some(hex => hex.is_foundable_by_civ?.[myCivId]) && myCiv?.city_power > 100;

        return (
            <>
                <div className="basic-example">
                    <HexGrid width={3000} height={3000} viewBox="-70 -70 140 140"
                    style={{backgroundColor: declineOptionsView ? '#FF6666' : foundingCity ? '#99FF99' : '#4488FF'}}>
                    <Layout size={{ x: 3, y: 3 }}>
                        {hexagons.map((hex, i) => {
                            return (
                                <Hexagon key={i} q={hex.q} r={hex.r} s={hex.s} 
                                        cellStyle={foundingCity ? 
                                                hexStyle(hex?.is_foundable_by_civ?.[myCivId] ? 'foundable' : 'unfoundable', !hex.yields) 
                                                : 
                                                (hex.yields && totalHexYields(hex.yields) > 0) ? hexStyle(hex.terrain, false) : hexStyle(hex.terrain, true)} 
                                    >
                                    <circle 
                                        cx="0" 
                                        cy="0" 
                                        r="0.01" 
                                        fill="none" 
                                        stroke="black" 
                                        strokeWidth="0.2" 
                                        ref={hexRefs.current[`${hex.q},${hex.r},${hex.s}`]}
                                        style={{visibility: 'hidden'}}
                                    />
                                    {hex.yields ? <YieldImages yields={hex.yields} /> : null}
                                </Hexagon>
                            );
                        })}
                        {hexagons.filter(hex => hex.city && hex.city.territory_parent_coords).map((hex, i) => <PuppetArrow key={i} city={hex.city}/>)}
                        {hexagons.map((hex, i) => {
                            return (
                                <Hexagon key={i} q={hex.q} r={hex.r} s={hex.s} cellStyle={{
                                    fillOpacity: 0,
                                    strokeOpacity: 0,
                                    }}
                                    onClick={(e) => handleClickHex(hex, e)} 
                                    onMouseOver={() => handleMouseOverHex(hex)}
                                    onMouseLeave={() => handleMouseLeaveHex(hex)}>
                                    {hex.city && <City 
                                        city={hex.city}
                                        isHovered={hex?.city?.id === hoveredCity?.id && isFriendlyCity(hex.city)}
                                        isSelected={hex?.city?.id === selectedCity?.id}  
                                        isUnitInHex={hex?.units?.length > 0}
                                        everControlled={hex?.city?.ever_controlled_by_civ_ids[myCivId]}
                                    />}
                                    {hex.camp && <Camp
                                        camp={hex.camp}
                                        isUnitInHex={hex?.units?.length > 0}
                                    />}
                                    {hex?.units?.length > 0 && <Unit
                                        unit={hex.units[0]}
                                        isCityInHex={hex?.city || hex?.camp}
                                    />}
                                    {!declineOptionsView && target1 && hex?.q === target1?.q && hex?.r === target1?.r && hex?.s === target1?.s && <TargetMarker />}
                                    {!declineOptionsView && target2 && hex?.q === target2?.q && hex?.r === target2?.r && hex?.s === target2?.s && <TargetMarker purple />}
                                </Hexagon>
                            );
                        })}
                    </Layout>         
                    </HexGrid>
                    {<Grid container direction="row" spacing={2} style={{position: 'fixed', right: '10px', bottom: '10px'}}>
                            <Grid item>
                                <Button onClick={() => setRulesDialogOpen(!rulesDialogOpen)} variant="contained" style={{backgroundColor: '#444444', position: 'fixed', left: '130px', bottom: '10px'}}>
                                    Rules
                                </Button>
                            </Grid>
                            <Grid item>
                                <Button onClick={() => setSettingsDialogOpen(!settingsDialogOpen)} variant="contained" style={{backgroundColor: '#444444', position: 'fixed', left: '10px', bottom: '10px'}}>
                                    Settings
                                </Button>
                            </Grid>
                        </Grid>}
                    {hoveredCiv && <CivDisplay civ={hoveredCiv} templates={templates} hoveredGamePlayer={hoveredGamePlayer}/>}
                    {hoveredHex && (
                        <HexDisplay hoveredHex={hoveredHex} templates={templates} />
                    )}
                    {<LowerRightDisplay 
                        gameState={gameState}
                        gameId={gameId}
                        playerNum={playerNum}
                        timerStatus={timerStatus}
                        nextForcedRollAt={nextForcedRollAt}
                        turnEndedByPlayerNum={turnEndedByPlayerNum}
                        isHoveredHex={!!hoveredHex}
                        handleClickEndTurn={handleClickEndTurn}
                        handleClickUnendTurn={handleClickUnendTurn}
                        overtimeUnendTurnDisabled={overtimeDeclineCivs && overtimeDeclineCivs.length > 0 ? !overtimeDeclineCivs.includes(playerNum) : false}
                        triggerAnimations={triggerAnimations}
                        engineState={engineState}
                        animationFrameLastPlayedRef={animationFrameLastPlayedRef}
                        animationTotalFrames={animationTotalFrames}
                        cancelAnimations={cancelAnimations}
                    />}
                    {<UpperRightDisplay 
                        setHoveredUnit={setHoveredUnit} 
                        setHoveredBuilding={setHoveredBuilding} 
                        setHoveredTech={setHoveredTech}
                        setHoveredCiv={setHoveredCiv}
                        setTechChoiceDialogOpen={setTechChoiceDialogOpen}
                        toggleFoundingCity={toggleFoundingCity}
                        canFoundCity={canFoundCity}
                        isFoundingCity={foundingCity}
                        templates={templates}
                        myCiv={myCiv} 
                        myCities={myCities}
                        myGamePlayer={myGamePlayer} 
                        mainGameState={mainGameState}
                        centerMap={centerMap}
                        isFriendlyCity={selectedCity && isFriendlyCity(selectedCity)}
                        setTechListDialogOpen={setTechListDialogOpen}
                        setSelectedCity={setSelectedCity}
                        disableUI={engineState !== EngineStates.PLAYING}
                        turnNum={gameState?.turn_num}
                        setDeclineOptionsView={setDeclineOptionsView}
                        declineViewGameState={declineViewGameState}
                        declineOptionsView={declineOptionsView}
                        civsById={civsById}
                    />}
                    {selectedCity && <CityDetailWindow 
                        gameState={gameState}
                        myTerritoryCapitals={myTerritoryCapitals}
                        myCivTemplate={templates.CIVS[selectedCity.civ?.name || civsById?.[selectedCity.civ_id]?.name]}
                        myCiv={myCiv}
                        declinePreviewMode={!myCiv || selectedCity.civ_id !== myCivId}
                        puppet={selectedCity.territory_parent_coords}
                        playerNum={playerNum}
                        playerApiUrl={playerApiUrl}
                        setGameState={setGameState}
                        refreshSelectedCity={refreshSelectedCity}
                        selectedCityBuildingChoices={selectedCityBuildingChoices} 
                        selectedCityBuildingQueue={selectedCityBuildingQueue}
                        selectedCityBuildings={selectedCityBuildings}
                        selectedCityUnitChoices={selectedCityUnitChoices}
                        selectedCity={selectedCity} 
                        unitTemplatesByBuildingName={unitTemplatesByBuildingName}
                        templates={templates}
                        descriptions={descriptions}
                        setHoveredUnit={setHoveredUnit}
                        setHoveredBuilding={setHoveredBuilding}
                        setSelectedCity={setSelectedCity}
                        />}
                    <div style={{position: 'fixed', top: '10px', left: '50%', transform: 'translate(-50%, 0%)'}}>                             
                        {hoveredBuilding && (
                            <BuildingDisplay buildingName={hoveredBuilding} unitTemplatesByBuildingName={unitTemplatesByBuildingName} templates={templates} />
                        )}
                        {hoveredUnit && (
                            <UnitDisplay unit={hoveredUnit} />
                        )}
                        {hoveredTech && (
                            <TechDisplay tech={hoveredTech} civ={myCiv} templates={templates}  unitTemplatesByBuildingName={unitTemplatesByBuildingName} gameState={gameState}/>
                        )}
                        {!hoveredBuilding && !hoveredUnit && !hoveredTech && <div className='turn-num-card'>
                            <Typography variant="h4">
                                Turn {gameState?.turn_num}
                            </Typography>
                            <Typography variant="h5">
                                Age {romanNumeral(gameState.advancement_level)}
                            </Typography>
                        </div>}
                    </div>
                    {myCiv && <FlagArrows myCiv={myCiv} hexagons={hexagons} civsById={civsById}/>}
                    {<div style={{
                        position: 'fixed', 
                        bottom: '10px', 
                        left: '50%', 
                        transform: 'translate(-50%, 0%)', 
                        display: 'flex', // Enable flexbox
                        flexDirection: 'row',
                        whiteSpace: 'nowrap', // Prevent wrapping                    
                    }}>
                        {engineState === EngineStates.PLAYING && selectedCity && 
                            (declineOptionsView || gameState?.special_mode_by_player_num[playerNum] === 'starting_location') && 
                            <ChooseCapitalButton 
                                playerNum={playerNum}
                                isOvertime={timerStatus === "OVERTIME"}
                                myGamePlayer={myGamePlayer}
                                selectedCity={selectedCity}
                                nonDeclineViewGameState={nonDeclineViewGameState}
                                engineState={engineState}
                                handleFoundCapital={handleFoundCapital}
                                civsById={civsById}
                            />
                            }
                        {engineState === EngineStates.GAME_OVER && !gameOverDialogOpen && <Button
                            style={{
                                backgroundColor: "#ccccff",
                                color: "black",
                                marginLeft: '20px',
                                padding: '10px 20px', // Increase padding for larger button
                                fontSize: '1.5em', // Increase font size for larger text
                                marginBottom: '10px',
                            }} 
                            variant="contained"
                            onClick={() => setGameOverDialogOpen(true)}
                        >
                            See end game info
                        </Button>}
                        {engineState === EngineStates.PLAYING && !declineOptionsView && myCiv &&
                            <TaskBar 
                                myCiv={myCiv} myCities={myCities} myUnits={myUnits} 
                                canFoundCity={canFoundCity} setSelectedCity={setSelectedCity} setFoundingCity={setFoundingCity} 
                                setTechChoiceDialogOpen={setTechChoiceDialogOpen} techChoiceDialogOpen={techChoiceDialogOpen}
                                setGreatPersonChoiceDialogOpen={setGreatPersonChoiceDialogOpen} greatPersonChoiceDialogOpen={greatPersonChoiceDialogOpen}
                            />
                        }

                    </div>}

                </div>
                {techListDialogOpen && <TechListDialog
                    open={techListDialogOpen}
                    onClose={() => {setHoveredTech(null); setTechListDialogOpen(false)}}
                    setHoveredTech={setHoveredTech}
                    handleClickTech={handleClickTech}
                    templates={templates}
                    myCiv={myCiv}
                    gameState={gameState}
                />}
                {greatPersonChoiceDialogOpen && <GreatPersonChoiceDialog
                    open={greatPersonChoiceDialogOpen}
                    onClose={() => setGreatPersonChoiceDialogOpen(false)}
                    greatPersonChoices={myCiv.great_people_choices}
                    handleSelectGreatPerson={handleSelectGreatPerson}
                    setHoveredTech={setHoveredTech}
                    setHoveredUnit={setHoveredUnit}
                    templates={templates}
                />}
                {gameOverDialogOpen && <GameOverDialog
                    open={gameOverDialogOpen}
                    onClose={() => setGameOverDialogOpen(false)}
                    gameState={gameState}
                />}
            </>
        );
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

    const fetchGameStatus = () => {
        fetch(`${URL}/api/game_status/${gameId}`)
            .then(response => response.json())
            .then(data => {
                console.log('fetched!')
                if (data.game_started) {
                    // game is running, let's go get the game state.
                    fetchTurnStartGameState(false);
                } else {
                    // Game is in lobby state.
                    console.log("Updating players in the game", data.players);
                    setPlayersInGame(data.players);
                    setTurnTimer(!data.turn_timer ? -1 : data.turn_timer);
                }
            });
    
    }

    const fetchTurnStartGameState = (playAnimations) => {
        fetchDeclineViewGameState();
        fetch(`${URL}/api/movie/last_frame/${gameId}?player_num=${playerNum}`)
            .then(response => response.json())
            .then(data => {
                console.log("Turn started: ", data.game_state.turn_num);
                fetchTurnTimerStatus(data.game_state.turn_num);
                setAnimationTotalFrames(data.num_frames);
                const budgetedAnimationTime = Math.min(30, data.game_state.turn_num) * 1000;
                // Give 5 seconds for the backend computation
                const animationTime = Math.max(budgetedAnimationTime - 5000, 5000);
                const animationDelay = Math.min(MAX_ANIMATION_DELAY, animationTime / data.num_frames)
                console.log("Attempting to play animation with", data.num_frames,  "frames in", animationTime/1000, "secs; turn has left", Math.floor(nextForcedRollAt - Date.now()/1000), " secs. Playing one frame per", animationDelay, "ms");
                setAnimationActiveDelay(animationDelay);

                if (playAnimations) {
                    triggerAnimations(data.game_state);
                } else {
                    setGameState(data.game_state);
                    const { myCiv } = getMyInfo(data.game_state);
                    sciencePopupIfNeeded(myCiv);
                }
            })
            .catch(error => {
                console.error('Error fetching turn start game state:', error);
            });
    }

    const receiveDeclineEviction = () => {
        fetchGameStatus();
        console.log("!!!!!!!!!!!!!!Eviction!!!!!!!!!!!!!!!")
        setDeclinePreemptedDialogOpen(true);
    }

    const fetchTurnTimerStatus = async (turn_num) => {
        fetch(`${URL}/api/turn_timer_status/${gameId}/${turn_num}`).then(response => response.json()).then(data => {
            setNextForcedRollAt(data.next_forced_roll_at);
            setTurnEndedByPlayerNum(data.turn_ended_by_player_num);
            setTimerStatus(data.status);
            setOvertimeDeclineCivs(data.overtime_decline_civs);
        });
    }

    useEffect(() => {
        console.log("Setting up socket");
        socket.emit('join', { room: gameId, username: username });
        fetchGameStatus();
        socket.on('update', (data) => {
          console.log('update received')
          if (gameStateExistsRef.current) {
            // Turn has rolled within a game.
            setDeclineOptionsView(false);
            fetchTurnStartGameState(true);
          }
          else {
            // Get here for updates before the game has launched (i.e. adding a player to the lobby)
            // And the "game has launched" update
            console.log("fetchGameState from update.")
            fetchGameStatus();
          }
        })
        socket.on('mute_timer', (data) => {
            console.log("mute timer turn ", data.turn_num);
            setTimerStatus("PAUSED");
        })
        socket.on('decline_evicted', (data) => {
            if (data.player_num === playerNum) {
                receiveDeclineEviction();
            }
        })
        socket.on('overtime', (data) => {
            console.log("overtime", data);
            // Set engine state to PLAYING, just in case we accidentally got a start_turn_roll state before the decline processed.
            setEngineState(EngineStates.PLAYING);
            fetchTurnTimerStatus(data.turn_num);
        })
        socket.on('turn_end_change', (data) => {
            setTurnEndedByPlayerNum({...turnEndedByPlayerNumRef.current, [data.player_num]: data.turn_ended});
        })
        socket.on('start_turn_roll', (data) => {
            console.log("start turn roll")
            setEngineState(EngineStates.ROLLING);
        })
        return () => {
            console.log("Destroying socket listeners.")
            socket.off('update');
            socket.off('mute_timer');
            socket.off('turn_end_change');
            socket.off('start_turn_roll');
            socket.off('decline_evicted');
            socket.off('overtime');
        }
    }, [socket])

    // if (!username) {
    //     return (
    //         <div>
    //             <TextField 
    //                 label="Username"
    //                 value={username}
    //                 onChange={(e) => setUsername}
    //             />
    //         </div>
    //     )
    // }

    const handleAddBotPlayer = () => {
        const data = {
        }

        fetch(`${URL}/api/add_bot_to_game/${gameId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        })
    }

    if (!templates) {
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
                <Grid item container direction="column" spacing={2}>
                    <Grid item>
                        <Select
                            value={turnTimer}
                            onChange={(e) => handleChangeTurnTimer(e.target.value)}
                            variant="outlined"
                        >
                            <MenuItem value={5}>5 seconds per turn</MenuItem>
                            <MenuItem value={10}>10 seconds per turn</MenuItem>
                            <MenuItem value={15}>15 seconds per turn</MenuItem>
                            <MenuItem value={20}>20 seconds per turn</MenuItem>
                            <MenuItem value={30}>30 seconds per turn</MenuItem>
                            <MenuItem value={45}>45 seconds per turn</MenuItem>
                            <MenuItem value={60}>60 seconds per turn</MenuItem>
                            <MenuItem value={90}>90 seconds per turn</MenuItem>
                            <MenuItem value={120}>2 minutes per turn</MenuItem>
                            <MenuItem value={-1}>No timer</MenuItem>                            
                        </Select>
                    </Grid>
                    <Grid item>
                        <Button onClick={handleAddBotPlayer} variant="contained" style={{backgroundColor: '#880088'}}>Add Bot Player</Button>
                    </Grid>
                    <Grid item>
                        <Button onClick={launchGame} variant="contained" style={{backgroundColor: '#008800'}}>Launch Game</Button>
                    </Grid>
                </Grid>
            )}
            {techChoiceDialogOpen && (
                <div className="tech-choices-container">
                    <DialogTitle>
                        <Typography variant="h5" component="div" style={{ flexGrow: 1, textAlign: 'center' }}>
                            Choose Technology
                        </Typography>
                        <IconButton
                            aria-label="close"
                            onClick={() => setTechChoiceDialogOpen(false)}
                            style={{
                                position: 'absolute',
                                right: 8,
                                top: 8,
                                color: (theme) => theme.palette.grey[500],
                            }}
                            color="primary"
                        >
                            Minimize
                        </IconButton>
                    </DialogTitle>
                    <div className="tech-choices-content">
                        {techChoices.map((tech, index) => {
                            const techTemplate = templates.TECHS[tech];
                            return <TechDisplay key={index} tech={techTemplate} civ={myCiv} templates={templates} unitTemplatesByBuildingName={unitTemplatesByBuildingName} gameState={gameState} onClick={() => handleClickTech(techTemplate)} />
                        })}

                    </div>
                </div>
            )}
            {settingsDialogOpen && (
                <SettingsDialog
                    open={settingsDialogOpen}
                    onClose={() => setSettingsDialogOpen(false)}
                    volume={volume}
                    setVolume={setVolume}
                />
            )}
            {rulesDialogOpen && (
                <RulesDialog
                    open={rulesDialogOpen}
                    onClose={() => setRulesDialogOpen(false)}
                    gameConstants={gameConstants}
                />
            )}
            {declinePreemptedDialogOpen && <DeclinePreemptedDialog open={declinePreemptedDialogOpen} onClose={() => setDeclinePreemptedDialogOpen(false)}/>}
            {declineFailedDialogOpen && <DeclineFailedDialog open={declineFailedDialogOpen} onClose={() => setDeclineFailedDialogOpen(false)}/>}
        </div>
    )
}