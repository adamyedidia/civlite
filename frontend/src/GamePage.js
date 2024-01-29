import React, {useState, useEffect} from 'react';

import { HexGrid, Layout, Hexagon, Text, Pattern, Path, Hex, GridGenerator } from 'react-hexgrid';
import './arrow.css';
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

const coordsToObject = (coords) => {
    if (!coords) {
        return null;
    }
    const [q, r, s] = coords.split(',').map(coord => parseInt(coord));
    return {q: q, r: r, s: s};
}

const ANIMATION_DELAY = 500;

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

    const [lastSetPrimaryTarget, setLastSetPrimaryTarget] = useState(false);

    const myCivId = gameState?.game_player_by_player_num?.[playerNum]?.civ_id;
    const myCiv = gameState?.civs_by_id?.[myCivId];
    const target1 = coordsToObject(myCiv?.target1);
    const target2 = coordsToObject(myCiv?.target2);

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

    console.log(myCivId);

    console.log(myCiv);

    console.log(gameState);

    // const [selectedCityBuildingChoices, setSelectedCityBuildingChoices] = useState(null);


    const selectedCityBuildingChoices = selectedCity?.available_building_names;
    const selectedCityBuildingQueue = selectedCity?.buildings_queue;
    const selectedCityBuildings = selectedCity?.buildings?.map(building => building.name) || [];

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

        setHoveredBuilding(null);

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

        setHoveredBuilding(null);

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

    const showSingleMovementArrow = (fromHexCoords, toHexCoords) => {
        // console.log(hexRefs?.current?.[fromHexCoords]);
        // console.log(hexRefs?.current?.[fromHexCoords]?.current);
        // console.log(hexRefs?.current?.[fromHexCoords]?.current?.getBoundingClientRect());

        const fromHexClientRef = hexRefs?.current?.[fromHexCoords]?.current?.getBoundingClientRect();
        const toHexClientRef = hexRefs?.current?.[toHexCoords]?.current?.getBoundingClientRect();

        console.log(fromHexClientRef);
        console.log(toHexClientRef);

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

    //     attackingCharacterPos = characterRefs?.current?.[event.lane]?.[event.acting_player]?.[event.from_character_index]?.current?.getBoundingClientRect();
    //     if (['heal', 'friendlyAttack'].includes(arrowType)) {
    //         defendingCharacterPos = characterRefs?.current?.[event.lane]?.[event.acting_player]?.[event.to_character_index]?.current?.getBoundingClientRect();
    //     }
    //     else if (arrowType === 'switchLanes') {
    //         defendingCharacterPos = characterRefs?.current?.[event.to_lane]?.[event.acting_player]?.[event.to_character_index]?.current?.getBoundingClientRect();
    //     }
    //     else {
    //         defendingCharacterPos = characterRefs?.current?.[event.lane]?.[1 - event.acting_player]?.[event.to_character_index]?.current?.getBoundingClientRect();
    //     }


    //     if (!attackingCharacterPos) {
    //         log('Attacking character position not found!')
    //         return;
    //     }

    //     if (!defendingCharacterPos) {
    //         log('Defending character position not found!')
    //         return;
    //     }

    //     // slice off the "px"
    //     characterWidth = CHARACTER_BOX_WIDTH.slice(0, -2);
    //     characterHeight = CHARACTER_BOX_HEIGHT.slice(0, -2);

    //     const dx = defendingCharacterPos.left - attackingCharacterPos.left;
    //     const dy = defendingCharacterPos.top - attackingCharacterPos.top;
    //     const distance = Math.sqrt(dx * dx + dy * dy);

    //     // Create an arrow element and set its position and rotation
    //     const arrow = document.createElement('div');
    //     arrow.className = 'arrow';
    //     arrow.style.position = 'absolute'; // Make sure it's set to absolute
    //     arrow.style.left = `${attackingCharacterPos.left + window.scrollX + characterWidth / 2 + 9}px`;
    //     arrow.style.top = `${attackingCharacterPos.top + window.scrollY + characterHeight / 2}px`;
    //     arrow.style.width = `${distance}px`; // Set the length of the arrow

    //     const angle = Math.atan2(dy, dx) * (180 / Math.PI);
    //     arrow.style.transform = `rotate(${angle}deg)`;
    //     arrow.style.transformOrigin = "0 50%";
    //     if (arrowType === 'shackle') {
    //         arrow.classList.add("shackled");
    //     } else if (arrowType === 'heal') {
    //         arrow.classList.add("healed");
    //     } else if (arrowType === 'silence') {
    //         arrow.classList.add("silenced");
    //     } else if (['switchLanes', 'switchSides'].includes(arrowType)) {
    //         arrow.classList.add("switchLanes");
    //     }
    //     else {
    //         arrow.classList.remove("shackled");
    //         arrow.classList.remove("healed");
    //         arrow.classList.remove("silenced");
    //         arrow.classList.remove("switchLanes");
    //     }

    //     document.body.appendChild(arrow);

    //     setTimeout(() => {
    //         document.body.removeChild(arrow);
    //     }, animationDelay * 0.67);

    //     log('Animation successfully triggered!')
    // };


    const triggerAnimations = async (finalGameState, animationQueue, doNotNotifyBackendOnCompletion) => {
        console.log('Triggering animations!');
        console.log(animationQueue);

        for (let event of animationQueue) {
            console.log(event);

            const newState = event?.game_state;

            if (newState) {
                switch (event?.data?.type) {
                    case 'UnitMovement':
                        await new Promise((resolve) => setTimeout(resolve, ANIMATION_DELAY));
                        showMovementArrows(event.data.coords);
                        setGameState(newState);                    
                }
            }
        }

        await new Promise((resolve) => setTimeout(resolve, ANIMATION_DELAY));
        setGameState(finalGameState);        
    }

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
        if (city.id === selectedCity?.id) {
            setSelectedCity(null);
        }
        else {
            setSelectedCity(city);
        }
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

    const Camp = ({ camp, isUnitInHex }) => {
        const primaryColor = 'red';
        const secondaryColor = 'black';
    
        return (
            <>
                <svg width="3" height="3" viewBox="0 0 3 3" x={-1.5} y={isUnitInHex ? -2.5 : -1.5} onMouseEnter={() => handleMouseOverCity(camp)} onClick={() => handleClickCity(camp)}>
                    <polygon points="1.5,0 3,3 0,3" fill={primaryColor} stroke={secondaryColor} strokeWidth={0.5} />
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

    const TargetMarker = ({ }) => {
        return (
            <svg width="3" height="3" viewBox="0 0 3 3" x={-1.5} y={-1.5}>
                <image href="/images/flag.svg" x="0" y="0" height="3" width="3" />
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
        let hoveredCivPicked = false;
        if (hex.city) {
            setHoveredCiv(civTemplates[hex.city.civ.name]);
            setHoveredCity(hex.city)
            hoveredCivPicked = true;
        }
        else {
            setHoveredCity(null);
        }
        if (hex?.units?.length > 0) {
            setHoveredUnit(hex?.units?.[0]?.name);
            setHoveredCiv(civTemplates[hex?.units?.[0]?.civ.name]);
            hoveredCivPicked = true;
        }
        else {
            setHoveredUnit(null);
        }
        if (!hoveredCivPicked) {
            setHoveredCiv(null);
        }
    };

    const hexesAreEqual = (hex1, hex2) => {
        return hex1?.q === hex2?.q && hex1?.r === hex2?.r && hex1?.s === hex2?.s;
    }

    const handleClickHex = (hex) => {
        setHoveredCity(null);

        if (hexesAreEqual(hex, target1)) {
            removeTarget(false);
            return;
        }

        if (hexesAreEqual(hex, target2)) {
            removeTarget(true);
            return;
        }

        if ((!hex.city) || (hex?.city?.civ?.id !== myCivId)) {
            setTarget(hex, !target1 ? false : !target2 ? true : lastSetPrimaryTarget ? true : false);
        }
    };

    const setTarget = (hex, isSecondary) => {
        if (!myCivId) return;

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

    const removeTarget = (isSecondary) => {
        if (!myCivId) return;

        const playerInput = {
            'move_type': `remove_civ_${isSecondary ? "secondary" : "primary"}_target`,
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

    const displayGameState = (gameState) => {
        // return <Typography>{JSON.stringify(gameState)}</Typography>
        const hexagons = Object.values(gameState.hexes)
        return (
            <div className="basic-example">
                <HexGrid width={2000} height={2000}>
                <Layout size={{ x: 3, y: 3 }}>
                    {hexagons.map((hex, i) => {
                        // console.log(hex?.q, hex?.r, hex?.s)
                        // console.log(target1?.q, target1?.r, target1?.s)
                        // console.log(hex?.q === target1?.q, hex?.r === target1?.r, hex?.s === target1?.s)

                        return (
                            // <div 
                            //     onContextMenu={(e) => {
                            //         e.preventDefault(); // Prevent the browser's context menu from showing up
                            //         handleRightClickHex(hex); // Call your right-click handler
                            //     }}
                            // >
                                <Hexagon key={i} q={hex.q} r={hex.r} s={hex.s} 
                                        cellStyle={hex.yields ? hexStyle(hex.terrain, false) : hexStyle(hex.terrain, true)} 
                                        onClick={() => handleClickHex(hex)} 
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
                                        isHovered={hex?.city?.id === hoveredCity?.id}
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
                                    {target2 && hex?.q === target2?.q && hex?.r === target2?.r && hex?.s === target2?.s && <TargetMarker />}
                                </Hexagon>
                            // </div>
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
                    getMovie(false);
                }
                if (data.players) {
                    setPlayersInGame(data.players);
                }
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
                        setGameState(newGameState);
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
          getMovie(true);
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