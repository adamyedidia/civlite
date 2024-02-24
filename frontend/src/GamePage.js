import React, {useState, useEffect} from 'react';

import { HexGrid, Layout, Hexagon, Text, Pattern, Path, Hex, GridGenerator } from 'react-hexgrid';
import './arrow.css';
import './GamePage.css';
import { Typography } from '@mui/material';
import { css } from '@emotion/react';
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
    TextField,
    Select,
    MenuItem,
} from '@mui/material';
import CivDisplay from './CivDisplay';
import TechDisplay from './TechDisplay';
import HexDisplay, { YieldImages } from './HexDisplay';
import BuildingDisplay from './BuildingDisplay';
import UnitDisplay from './UnitDisplay';
import CityDetailWindow from './CityDetailWindow';
import UpperRightDisplay from './UpperRightDisplay';
import moveSound from './sounds/movement.mp3';
import meleeAttackSound from './sounds/melee_attack.mp3';
import rangedAttackSound from './sounds/ranged_attack.mp3';
import gunpowderMeleeAttackSound from './sounds/gunpowder_melee.mp3';
import gunpowderRangedAttackSound from './sounds/gunpowder_ranged.mp3';
import SettingsDialog from './SettingsDialog';
import TurnEndedDisplay from './TurnEndedDisplay';
import { lowercaseAndReplaceSpacesWithUnderscores } from './lowercaseAndReplaceSpacesWithUnderscores';

const coordsToObject = (coords) => {
    if (!coords) {
        return null;
    }
    const [q, r, s] = coords.split(',').map(coord => parseInt(coord));
    return {q: q, r: r, s: s};
}

const ANIMATION_DELAY = 400;

let userHasInteracted = false;

window.addEventListener('click', () => {
    userHasInteracted = true;
});

function ConfirmEnterDeclineDialog({open, onClose, onConfirm}) {
    const handleConfirm = () => {
        onConfirm();
        onClose();
    }

    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>Confirm Enter Decline</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    Are you sure you want to enter decline? You will stop controlling your current civilization,
                    and will be offered a choice of new civilizations to control.
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Cancel
                </Button>
                <Button onClick={handleConfirm} color="primary">
                    Confirm
                </Button>
            </DialogActions>
        </Dialog>
    )
}

function TechListDialog({open, onClose, setHoveredTech, myCiv, techTemplates}) {
    if (!myCiv || !techTemplates) return null;
    
    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>Researched Technologies</DialogTitle>
            <DialogContent>
                {Object.keys(myCiv.techs)?.map((tech, index) => (
                    <Typography onMouseEnter={() => setHoveredTech(techTemplates[tech])} onMouseLeave={() => setHoveredTech(null)} key={index}>{tech}</Typography>
                ))}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose} color="primary">
                    Close
                </Button>
            </DialogActions>
        </Dialog>
    )

}

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
                    Every unit in the game (except Warriors and Scouts) require a building a production building before you can build them in the city. Wood is used to build buildings.
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
                    Whatever city you choose will be your new capital. Your new civilization will start with a high vitality (200% + 10% per turn since the start of the game). You'll also start with some technologies, corresponding
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

const generateUniqueId = () => {
    return Math.random().toString(36).substring(2);
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
    const [playersInGame, setPlayersInGame] = useState(null);
    const [turnNum, setTurnNum] = useState(1);
    const [frameNum, setFrameNum] = useState(0);

    const [civTemplates, setCivTemplates] = useState({});
    const [unitTemplates, setUnitTemplates] = useState(null);
    const [techTemplates, setTechTemplates] = useState(null);
    const [buildingTemplates, setBuildingTemplates] = useState(null);
    const [volume, setVolume] = useState(100);
    const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);

    const unitTemplatesByBuildingName = {};
    Object.values(unitTemplates || {}).forEach(unitTemplate => {
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
    const [selectedCity, setSelectedCity] = useState(null);

    const [techChoices, setTechChoices] = useState(null);

    const [lastSetPrimaryTarget, setLastSetPrimaryTarget] = useState(false);

    const [animating, setAnimating] = useState(false);

    const [animationRunIdUseState, setAnimationRunIdUseState] = useState(null);

    const [foundingCity, setFoundingCity] = useState(false);

    const [confirmEnterDecline, setConfirmEnterDecline] = useState(false);

    const [techListDialogOpen, setTechListDialogOpen] = useState(false);

    const animationRunIdRef = React.useRef(null);

    const [gameConstants, setGameConstants] = useState(null);

    const [rulesDialogOpen, setRulesDialogOpen] = useState(false);

    const [turnTimer, setTurnTimer] = useState(-1);
    const [timerMutedOnTurn, setTimerMutedOnTurn] = useState(null);

    const [turnEndedByPlayerNum, setTurnEndedByPlayerNum] = useState({});

    const gameStateExistsRef = React.useRef(false);
    const firstRenderRef = React.useRef(true);

    const myGamePlayer = gameState?.game_player_by_player_num?.[playerNum];
    const myCivId = gameState?.game_player_by_player_num?.[playerNum]?.civ_id;
    const myCiv = gameState?.civs_by_id?.[myCivId];
    const target1 = coordsToObject(myCiv?.target1);
    const target2 = coordsToObject(myCiv?.target2);

    const myCivIdRef = React.useRef(myCivId);
    const hoveredHexRef = React.useRef(hoveredHex);
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
        playerNumRef.current = playerNum;
    }, [playerNum]);

    useEffect(() => {
        gameStateRef.current = gameState;
    }, [gameState]);

    useEffect(() => {
        turnEndedByPlayerNumRef.current = turnEndedByPlayerNum;
    }, [turnEndedByPlayerNum]);

    // console.log(selectedCity);

    // console.log(hoveredHex);

    console.log(gameState);

    useEffect(() => {
        // When the user presses escape
        const handleKeyDown = (event) => {
            if (event.key === 'Escape') {
                setSelectedCity(null);
                setFoundingCity(false);
            }
        };
    
        // Add event listener
        window.addEventListener('keydown', handleKeyDown);
    
        // Remove event listener on cleanup
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []); // Empty dependency array ensures this effect runs only once after the initial render

    const handleContextMenu = (e) => {
        if (hoveredHexRef.current || !process.env.REACT_APP_LOCAL) {
            e.preventDefault();
        } 

        if (hoveredHexRef.current) {
            setHoveredCity(null);

            if (hexesAreEqual(hoveredHexRef.current, target1Ref.current)) {
                removeTarget(false);
                return;
            }

            if (hexesAreEqual(hoveredHexRef.current, target2Ref.current)) {
                removeTarget(true);
                return;
            }

            setTarget(hoveredHexRef.current, !target1Ref.current ? false : !target2Ref.current ? true : lastSetPrimaryTargetRef.current ? true : false);
        }
    }

    useEffect(() => {

        document.addEventListener('contextmenu', handleContextMenu);

        return () => {
            document.removeEventListener('contextmenu', handleContextMenu);
        };
    }, []);

    useEffect(() => {
        animationRunIdRef.current = animationRunIdUseState;
    }, [animationRunIdUseState]);

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
            audio.volume = 0.2 * volumeRef.current / 100;
            audio.play();
        } catch (error) {
            console.error('Error playing sound:', error);
        }
    }

    function playSpawnSound(spawnSound) {
        if (!userHasInteracted) return;

        try {
            let audio = new Audio(spawnSound);
            audio.volume = 0.5 * volumeRef.current / 100;
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
                return description1?.value - description2?.value;
            }
        });
    }
    else {
        selectedCityBuildingChoices = unsortedSelectedCityBuildingChoices;
    }

    const selectedCityBuildingQueue = selectedCity?.buildings_queue;
    const selectedCityBuildings = selectedCity?.buildings?.map(building => building.name);

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
            setHoveredTech(null);
        }
    }, [!!hoveredBuilding])

    useEffect(() => {
        if (!!hoveredUnit) {
            setHoveredBuilding(null);
            setHoveredTech(null);
        }
    }, [!!hoveredUnit])

    useEffect(() => {
        if (!!hoveredTech) {
            setHoveredBuilding(null);
            setHoveredUnit(null);
        }
    }, [!!hoveredTech])

    const toggleFoundingCity = () => {
        setFoundingCity(!foundingCity);
    }

    useEffect(() => {
        if (!animating && myCiv?.tech_queue?.length === 0 && !gameState?.special_mode_by_player_num?.[playerNum]) {

            fetch(`${URL}/api/tech_choices/${gameId}?player_num=${playerNum}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                },
            }).then(response => response.json())
                .then(data => {
                    if (data.tech_choices) {
                        setTechChoices(data.tech_choices);
                    }
                });
        }
    }, [animating, myCiv?.tech_queue?.length])

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
                getMovie(false);
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
        }).then(response => response.json())
            .then(data => {
                if (data.game_state) {
                    // setGameState(data.game_state);
                }
                getMovie(false);
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
        
        fetch(`${URL}/api/game_constants`)
            .then(response => response.json())
            .then(data => setGameConstants(data));
    }, [])


    // useEffect(() => {
    //     if (selectedCity?.id) {
    //         fetch(`${URL}/api/building_choices/${gameId}/${selectedCity?.id}`).then(response => response.json()).then(data => {
    //             setSelectedCityBuildingChoices(data.building_choices);
    //         });
    //     }
    // }, [selectedCity?.id])

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
        }, ANIMATION_DELAY * 0.67);
    }

    const showMovementArrows = (coords) => {
        if (!coords || coords.length < 2) {
            return;
        }

        for (let i = 0; i < coords.length - 1; i++) {
            showSingleMovementArrow(coords[i], coords[i + 1]);
        }
    }

    const triggerAnimations = async (finalGameState, animationQueue, doNotNotifyBackendOnCompletion) => {
        const animationRunId = generateUniqueId();

        console.log(`animating! ${animationRunId}`);
        console.log(animationQueue)

        if (animating) {
            return;
        }

        setAnimationRunIdUseState(animationRunId);

        setAnimating(true);

        const cases = ['UnitMovement', 'UnitAttack'];
        const filteredAnimationQueue = animationQueue.filter((animationEvent) => cases.includes(animationEvent?.data?.type));        


        for (let event of animationQueue) {
            console.log(event);

            const newState = event?.game_state;

            if (newState) {
                switch (event?.data?.type) {
                    case 'UnitMovement':
                        await new Promise((resolve) => setTimeout(resolve, ANIMATION_DELAY));
                        playMoveSound(moveSound, volume);
                        showMovementArrows(event.data.coords);
                        setGameState(newState);         
                        break;           
                    case 'UnitAttack':
                        await new Promise((resolve) => setTimeout(resolve, ANIMATION_DELAY));
                        if (event.data.attack_type === 'melee') {
                            playMeleeAttackSound(meleeAttackSound, volume);
                        } else if (event.data.attack_type === 'ranged') {
                            playRangedAttackSound(rangedAttackSound, volume);
                        } else if (event.data.attack_type === 'gunpowder_melee') {
                            playGunpowderMeleeAttackSound(gunpowderMeleeAttackSound, volume);
                        } else if (event.data.attack_type === 'gunpowder_ranged') {
                            playGunpowderRangedAttackSound(gunpowderRangedAttackSound, volume);
                        }
                        showSingleMovementArrow(event.data.start_coords, event.data.end_coords, 'attack');
                        setGameState(newState);
                        break;
                    // case 'UnitSpawn':
                    //     await new Promise((resolve) => setTimeout(resolve, ANIMATION_DELAY));
                    //     playSpawnSound(spawnSound, volume);
                    //     setGameState(newState);
                    //     break;
                    
                }

                if ((animationRunId !== animationRunIdRef.current) && (filteredAnimationQueue.length > 1)) {
                    return;
                }                            
            }
        }

        await new Promise((resolve) => setTimeout(resolve, ANIMATION_DELAY));
        setGameState(finalGameState);
        setTurnEndedByPlayerNum(finalGameState?.turn_ended_by_player_num || {});

        setAnimating(false);
    }

    const isFriendlyCityHex = (hex) => {
        return isFriendlyCity(hex?.city);
    }

    const isFriendlyCity = (city) => {
        // if (gameState?.special_mode_by_player_num[playerNum]) {
        //     return true;
        // }
        if (playerNum !== null && playerNum !== undefined) {
            return city?.civ?.game_player?.player_num === playerNum
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
        if (city.id === selectedCity?.id) {
            setSelectedCity(null);
        }
        else {
            if (isFriendlyCity(city)) {
                setSelectedCity(city);
            }
        }
    };

    const handleFoundCapital = () => {
        if (gameState.special_mode_by_player_num[playerNum] == 'starting_location') {
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
                    setTechChoices(data.tech_choices);
                    if (data.game_state) {
                        setGameState(data.game_state);
                        refreshSelectedCity(data.game_state);
                    }
                });
        } else if (gameState.special_mode_by_player_num[playerNum] == 'choose_decline_option') {
            const data = {
                player_num: playerNum,
                player_input: {
                    city_id: selectedCity.id,
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
                    if (data.game_state) {
                        setGameState(data.game_state);
                        refreshSelectedCity(data.game_state);
                    }
                });

        }
    }


    const City = ({ city, isHovered, isSelected, isUnitInHex }) => {
        const primaryColor = civTemplates[city.civ.name]?.primary_color;
        const secondaryColor = civTemplates[city.civ.name]?.secondary_color;
        const population = city.population;
    
        const pointer = isFriendlyCity(city);
    
        // Function to darken color
        const darkenColor = (color) => {
            let f = parseInt(color.slice(1), 16),
                t = 0 | ((1 << 8) + f - (f >> 2) & 0xFFFFFF),
                newColor = "#" + t.toString(16).toUpperCase();
            return newColor;
        };
    
        // Darken colors if city is in decline
        // const finalPrimaryColor = city.civ.in_decline ? darkenColor(primaryColor) : primaryColor;
        // const finalSecondaryColor = city.civ.in_decline ? darkenColor(secondaryColor) : secondaryColor;

        const finalPrimaryColor = primaryColor;
        const finalSecondaryColor = secondaryColor;
    
        return (
            <>
                {isHovered && <circle cx="0" cy={`${isUnitInHex ? -1 : 0}`} r="2.25" fill="none" stroke="white" strokeWidth="0.2"/>}
                {isSelected && <circle cx="0" cy={`${isUnitInHex ? -1 : 0}`} r="2.25" fill="none" stroke="black" strokeWidth="0.2"/>}
                {city.under_siege_by_civ && <svg width="6" height="6" viewBox="0 0 6 6" x={-3} y={isUnitInHex ? -4 : -3}>
                        <image href="/images/fire.svg" x="0" y="0" height="6" width="6" />
                    </svg>
                }
                <svg width="3" height="3" viewBox="0 0 3 3" x={-1.5} y={isUnitInHex ? -2.5 : -1.5} onMouseEnter={() => handleMouseOverCity(city)} onClick={() => handleClickCity(city)} style={{...(pointer ? {cursor : 'pointer'} : {})}}>
                    <rect width="3" height="3" fill={finalPrimaryColor} stroke={finalSecondaryColor} strokeWidth={0.5} />
                    <text x="50%" y="56%" dominantBaseline="middle" textAnchor="middle" fontSize="0.1" fill="white">
                        {population}
                    </text>
                </svg>
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
        const primaryColor = civTemplates[unit.civ.name]?.primary_color;
        const secondaryColor = civTemplates[unit.civ.name]?.secondary_color;
        const unitImage = `/images/${lowercaseAndReplaceSpacesWithUnderscores(unit.name)}.svg`; // Path to the unit SVG image
    
        const scale = isCityInHex ? 0.95 : 1.4;
        const healthPercentage = unit.health / 100; // Calculate health as a percentage
    
        // Function to darken color
        const darkenColor = (color) => {
            let f = parseInt(color.slice(1), 16),
                t = 0 | ((1 << 8) + f - (f >> 2) & 0xFFFFFF),
                newColor = "#" + t.toString(16).toUpperCase();
            return newColor;
        };
    
        // Darken colors if unit's civ is in decline
        // const finalPrimaryColor = unit.civ.in_decline ? darkenColor(primaryColor) : primaryColor;
        // const finalSecondaryColor = unit.civ.in_decline ? darkenColor(secondaryColor) : secondaryColor;
    
        const finalPrimaryColor = primaryColor;
        const finalSecondaryColor = secondaryColor;

        return (
            <svg width={`${4*scale}`} height={`${4*scale}`} viewBox={`0 0 ${4*scale} ${4*scale}`} x={-2*scale} y={-2*scale + (isCityInHex ? 1 : 0)}>
                <circle cx={`${2*scale}`} cy={`${2*scale}`} r={`${scale}`} fill={finalPrimaryColor} stroke={finalSecondaryColor} strokeWidth={0.5} />
                <image href={unitImage} x={`${scale}`} y={`${scale}`} height={`${2*scale}`} width={`${2*scale}`} />
                <rect x={`${scale}`} y={`${3.4*scale}`} width={`${2*scale}`} height={`${0.2*scale}`} fill="#ff0000" /> {/* Total health bar */}
                <rect x={`${scale}`} y={`${3.4*scale}`} width={`${2*scale*healthPercentage}`} height={`${0.2*scale}`} fill="#00ff00" /> {/* Current health bar */}
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
            setHoveredCiv(civTemplates[hex.city.civ.name]);
            setHoveredGamePlayer(hex?.city?.civ?.game_player?.username);
            setHoveredCity(hex.city)
            hoveredCivPicked = true;
        }
        else {
            setHoveredCity(null);
        }
        if (hex?.units?.length > 0) {
            setHoveredUnit(hex?.units?.[0]);
            setHoveredCiv(civTemplates[hex?.units?.[0]?.civ.name]);
            setHoveredGamePlayer(hex?.units?.[0]?.civ?.game_player?.username);
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

            const data = {
                player_num: playerNum,
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
                        setFoundingCity(false);
                    }
                });
        }
        else {
            setHoveredCity(null);
        }   
    };

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

        const data = {
            player_num: playerNumRef.current,
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

    const removeTarget = (isSecondary) => {
        if (!myCivIdRef.current) return;

        const playerInput = {
            'move_type': `remove_civ_${isSecondary ? "secondary" : "primary"}_target`,
        }

        const data = {
            player_num: playerNumRef.current,
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

    const handleEnterDecline = () => {
        if (!myCivId) return;

        const playerInput = {
            'player_num': playerNum,
            'move_type': 'enter_decline',
        }

        const data = {
            player_num: playerNum,
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
                    setTechChoices(null);
                    // refreshSelectedCity(data.game_state);
                }
            });        
    }

    const displayGameState = (gameState) => {
        // return <Typography>{JSON.stringify(gameState)}</Typography>
        const hexagons = Object.values(gameState.hexes)

        const canFoundCity = hexagons.some(hex => hex.is_foundable_by_civ?.[myCivId]);

        return !gameState?.game_over ? (
            <>
                <div className="basic-example">
                    <HexGrid width={3000} height={3000} viewBox="-70 -70 140 140">
                    <Layout size={{ x: 3, y: 3 }}>
                        {hexagons.map((hex, i) => {
                            return (
                                // <div 
                                //     onContextMenu={(e) => {
                                //         e.preventDefault(); // Prevent the browser's context menu from showing up
                                //         handleRightClickHex(hex); // Call your right-click handler
                                //     }}
                                // >
                                    <Hexagon key={i} q={hex.q} r={hex.r} s={hex.s} 
                                            cellStyle={foundingCity ? 
                                                    hexStyle(hex?.is_foundable_by_civ?.[myCivId] ? 'foundable' : 'unfoundable', !hex.yields) 
                                                    : 
                                                    hex.yields ? hexStyle(hex.terrain, false) : hexStyle(hex.terrain, true)} 
                                            onClick={(e) => handleClickHex(hex, e)} 
                                            onMouseOver={() => handleMouseOverHex(hex)}
                                            onMouseLeave={() => handleMouseLeaveHex(hex)}
                                            // ref={hexRefs.current[`${hex.q},${hex.r},${hex.s}`]}
                                        >
                                        {/* <div 
                                            ref={hexRefs.current[`${hex.q},${hex.r},${hex.s}`]} 
                                            style={{
                                                position: 'absolute',
                                                top: '50%',
                                                left: '50%',
                                                transform: 'translate(-50%, -50%)',
                                                width: '100px',
                                                height: '100px',
                                                zIndex: '10000',
                                                backgroundColor: 'red',
                                                // visibility: 'hidden',
                                            }}
                                        /> */}
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
                                        {hex.city && <City 
                                            city={hex.city}
                                            isHovered={hex?.city?.id === hoveredCity?.id && isFriendlyCity(hex.city)}
                                            isSelected={hex?.city?.id === selectedCity?.id}  
                                            isUnitInHex={hex?.units?.length > 0}                              
                                        />}
                                        {hex.camp && <Camp
                                            camp={hex.camp}
                                            isUnitInHex={hex?.units?.length > 0}
                                        />}
                                        {hex?.units?.length > 0 && <Unit
                                            unit={hex.units[0]}
                                            isCityInHex={hex?.city || hex?.camp}
                                        />}
                                        {target1 && hex?.q === target1?.q && hex?.r === target1?.r && hex?.s === target1?.s && <TargetMarker />}
                                        {target2 && hex?.q === target2?.q && hex?.r === target2?.r && hex?.s === target2?.s && <TargetMarker purple />}
                                    </Hexagon>
                                // </div>
                            );
                        })}
                    </Layout>         
                    </HexGrid>
                    {!hoveredCiv && <Grid container direction="row" spacing={2} style={{position: 'fixed', right: '10px', bottom: '10px'}}>
                            <Grid item>
                                <Button onClick={() => setRulesDialogOpen(!rulesDialogOpen)} variant="contained" style={{backgroundColor: '#444444', position: 'fixed', right: '130px', bottom: '10px'}}>
                                    Rules
                                </Button>
                            </Grid>
                            <Grid item>
                                <Button onClick={() => setSettingsDialogOpen(!settingsDialogOpen)} variant="contained" style={{backgroundColor: '#444444', position: 'fixed', right: '10px', bottom: '10px'}}>
                                    Settings
                                </Button>
                            </Grid>
                        </Grid>}
                    {hoveredCiv && <CivDisplay civ={hoveredCiv} hoveredGamePlayer={hoveredGamePlayer}/>}
                    {hoveredHex && (
                        <HexDisplay hoveredHex={hoveredHex} unitTemplates={unitTemplates} />
                    )}
                    {gameState && <TurnEndedDisplay 
                        gamePlayerByPlayerNum={gameState?.game_player_by_player_num}
                        turnEndedByPlayerNum={turnEndedByPlayerNum}
                        animating={animating}
                        isHoveredHex={!!hoveredHex}
                    />}
                    {<UpperRightDisplay 
                        city={selectedCity || hoveredCity} 
                        setHoveredUnit={setHoveredUnit} 
                        setHoveredBuilding={setHoveredBuilding} 
                        setHoveredTech={setHoveredTech}
                        toggleFoundingCity={toggleFoundingCity}
                        canFoundCity={canFoundCity}
                        isFoundingCity={foundingCity}
                        techTemplates={techTemplates}
                        civTemplates={civTemplates}
                        myCiv={myCiv} 
                        myGamePlayer={myGamePlayer} 
                        isFriendlyCity={selectedCity && isFriendlyCity(selectedCity)}
                        unitTemplates={unitTemplates}
                        announcements={gameState?.announcements}
                        setTechListDialogOpen={setTechListDialogOpen}
                        turnNum={turnNum}
                        nextForcedRollAt={gameState?.next_forced_roll_at}
                        gameId={gameId}
                        timerMuted={timerMutedOnTurn === turnNum}
                    />}
                    {selectedCity && <CityDetailWindow 
                        gameState={gameState}
                        myCivTemplate={civTemplates[selectedCity.civ.name]}
                        declinePreviewMode={!myCiv || selectedCity.civ.name != myCiv.name}
                        playerNum={playerNum}
                        playerApiUrl={playerApiUrl}
                        setGameState={setGameState}
                        refreshSelectedCity={refreshSelectedCity}
                        selectedCityBuildingChoices={selectedCityBuildingChoices} 
                        selectedCityBuildingQueue={selectedCityBuildingQueue}
                        selectedCityBuildings={selectedCityBuildings}
                        selectedCityUnitChoices={selectedCityUnitChoices}
                        selectedCityUnitQueue={selectedCityUnitQueue}
                        selectedCity={selectedCity} 
                        unitTemplatesByBuildingName={unitTemplatesByBuildingName}
                        buildingTemplates={buildingTemplates}
                        unitTemplates={unitTemplates}
                        descriptions={descriptions}
                        setHoveredUnit={setHoveredUnit}
                        setHoveredBuilding={setHoveredBuilding}
                        setSelectedCity={setSelectedCity}
                        />}
                    <div style={{position: 'fixed', top: '10px', left: '50%', transform: 'translate(-50%, 0%)'}}>                             
                        {hoveredBuilding && (
                            <BuildingDisplay buildingName={hoveredBuilding} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} />
                        )}
                        {hoveredUnit && (
                            <UnitDisplay unit={hoveredUnit} />
                        )}
                        {hoveredTech && (
                            <TechDisplay tech={hoveredTech} unitTemplates={unitTemplates} buildingTemplates={buildingTemplates} unitTemplatesByBuildingName={unitTemplatesByBuildingName} gameState={gameState}/>
                        )}
                        {!hoveredBuilding && !hoveredUnit && !hoveredTech && <div className='turn-num-card'>
                            <Typography variant="h4">
                                Turn {gameState?.turn_num}
                            </Typography>
                        </div>}
                    </div>
                    {!animating && <div style={{
                        position: 'fixed', 
                        bottom: '10px', 
                        left: '50%', 
                        transform: 'translate(-50%, 0%)', 
                        flexDirection: 'row',
                        display: 'flex', // Enable flexbox
                        flexDirection: 'row',
                        whiteSpace: 'nowrap', // Prevent wrapping                    
                    }}>
                        {!gameState?.special_mode_by_player_num?.[playerNum] && <Button 
                            style={{
                                backgroundColor: "#cccc88",
                                color: "black",
                                marginLeft: '20px',
                                padding: '10px 20px', // Increase padding for larger button
                                fontSize: '1.5em', // Increase font size for larger text
                                marginBottom: '10px',
                            }} 
                            variant="contained"
                            onClick={gameState?.turn_ended_by_player_num?.[playerNum] ? handleClickUnendTurn : handleClickEndTurn}
                            disabled={animating}
                        >
                            {gameState?.turn_ended_by_player_num?.[playerNum] ? "Unend turn" : "End turn"}
                        </Button>}
                        {!gameState?.special_mode_by_player_num?.[playerNum] && <Button
                            style={{
                                backgroundColor: "#BBAABB",
                                color: "black",
                                marginLeft: '20px',
                                padding: '10px 20px', // Increase padding for larger button
                                fontSize: '1.5em', // Increase font size for larger text
                                marginBottom: '10px',
                            }} 
                            variant="contained"
                            onClick={() => setConfirmEnterDecline(true)}
                            disabled={animating}
                        >
                            Enter decline
                        </Button>}
                        {!gameState?.special_mode_by_player_num?.[playerNum] && <Button
                            style={{
                                backgroundColor: "#ffcccc",
                                color: "black",
                                marginLeft: '20px',
                                padding: '10px 20px', // Increase padding for larger button
                                fontSize: '1.5em', // Increase font size for larger text
                                marginBottom: '10px',
                            }} 
                            variant="contained"
                            onClick={() => getMovie(true)}
                            disabled={animating}
                        >
                            Replay animations
                        </Button>}
                        {gameState?.special_mode_by_player_num?.[playerNum] && selectedCity && <Button
                            style={{
                                backgroundColor: "#ccffaa",
                                color: "black",
                                marginLeft: '20px',
                                padding: '10px 20px', // Increase padding for larger button
                                fontSize: '1.5em', // Increase font size for larger text
                                marginBottom: '10px',
                            }} 
                            variant="contained"
                            onClick={() => handleFoundCapital()}
                            disabled={animating}
                        >
                            Make {selectedCity.name} my capital
                        </Button>}
                    </div>}
                </div>
                {confirmEnterDecline && <ConfirmEnterDeclineDialog
                    open={confirmEnterDecline}
                    onClose={() => setConfirmEnterDecline(false)}
                    onConfirm={() => handleEnterDecline()}
                />}
                {techListDialogOpen && <TechListDialog
                    open={techListDialogOpen}
                    onClose={() => setTechListDialogOpen(false)}
                    setHoveredTech={setHoveredTech}
                    techTemplates={techTemplates}
                    myCiv={myCiv}
                />}
            </>
        ) : (
            <>
                <Grid container direction="column" spacing={2}>
                    <Grid item>
                        <Typography variant="h2">Game over</Typography>
                    </Grid>
                    {Object.values(gameState?.game_player_by_player_num).map((gamePlayer) => {
                        return (
                            <Grid item key={gamePlayer.player_num}>
                                <Typography variant="h5">{gamePlayer.username}</Typography>
                                <Typography>Score: {gamePlayer.score}</Typography>
                            </Grid>
                        )
                    })}
                </Grid>
            </>
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
                    getMovie(false);
                }
                if (data.players) {
                    setPlayersInGame(data.players);
                }
                console.log('fetched!')
                setTurnTimer(!data.turn_timer ? -1 : data.turn_timer);
            });
    
    }

    const getMovie = (playAnimations) => {
        fetch(`${URL}/api/movie/${gameId}?player_num=${playerNum}`)
            .then(response => response.json())
            .then(data => {
                if (data.animation_frames) {
                    let newGameState = data.animation_frames[data.animation_frames.length - 1].game_state;
                    
                    setFrameNum(data.animation_frames.length - 1);

                    if (playAnimations) {
                        triggerAnimations(newGameState, data.animation_frames, true);
                    }
                    else {
                        if (turnNum !== 1 && data.turn_num !== turnNum) {
                        } else {
                            setGameState(newGameState);
                        }
                    }

                    setSelectedCity(null);
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
          if (gameStateExistsRef.current) {
            getMovie(true);
          }
          else {
            fetchGameState();
          }
        })
        socket.on('mute_timer', (data) => {
            setTimerMutedOnTurn(data.turn_num);
        })
        socket.on('turn_end_change', (data) => {
            setTurnEndedByPlayerNum({...turnEndedByPlayerNumRef.current, [data.player_num]: data.turn_ended});
        })
    }, [])

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
            {techChoices && (
                <div className="tech-choices-container">
                    {techChoices.map((tech, index) => (
                        <TechDisplay key={index} tech={tech} unitTemplates={unitTemplates} buildingTemplates={buildingTemplates} unitTemplatesByBuildingName={unitTemplatesByBuildingName} gameState={gameState} onClick={() => handleClickTech(tech)} />
                    ))}
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
        </div>
    )
}