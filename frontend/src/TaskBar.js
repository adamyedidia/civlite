import React from 'react';
import './TaskBar.css';

import { Tooltip } from '@mui/material';
import TradeHubIcon from './TradeHubIcon';

import cityImg from './images/city.png';
import scienceImg from './images/science.png';
import greatPersonImg from './images/greatperson.png';
import phoenixImg from './images/phoenix.png';
import ideologyImg from './images/ideology.png';

// For images in the public/images directory, use the public URL path
const flag1Img = `${process.env.PUBLIC_URL}/images/flag.svg`;
const flag2Img = `${process.env.PUBLIC_URL}/images/purple_flag.svg`;
const TaskIcon = ({icon, content, onClick, tooltip, nobounce, iconOpacity}) => {
    return <Tooltip title={tooltip}>
        <div className={`task-icon ${onClick ? 'clickable' : ''} ${nobounce ? '' : 'bounce'}`} onClick={onClick} style={{opacity: iconOpacity}}>
            {icon ? <img src={icon} style={{opacity: iconOpacity}} /> : content}
        </div>
    </Tooltip>
}


export const TaskBar = ({myCiv, myGamePlayer, myCities, myUnits, canFoundCity, setSelectedCity, setFoundingCity, setTechChoiceDialogOpen, techChoiceDialogOpen, setGreatPersonChoiceDialogOpen, greatPersonChoiceDialogOpen, setIdeologyTreeOpen, ideologyTreeOpen}) => {
    const a7Tenet = myGamePlayer.a7_tenet_yield;
    const anyUnhappyCities = myCities?.some(city => city.unhappiness > 0 || city.projected_income['unhappiness'] > 0);
    
    // Generate the list of unhappy cities as a JSX element
    const unhappyCitiesList = (
        <ul>
            {myCities?.filter(city => city.unhappiness > 0 || city.projected_income['unhappiness'] > 0)
                .map(city => (
                    <li key={city.name} onClick={() => setSelectedCity(city)}>{city.name}</li> // Ensure each <li> has a unique key
                ))}
        </ul>
    );

    return <div className="task-bar">
            {myCiv?.has_tenet_choice && !ideologyTreeOpen && <TaskIcon icon={ideologyImg} onClick={() => {setIdeologyTreeOpen(true)}} tooltip="Choose tenet" />}
            {myCiv?.great_people_choices.length > 0 && !greatPersonChoiceDialogOpen && <TaskIcon icon={greatPersonImg} tooltip="Select Great Person" onClick={() => {setGreatPersonChoiceDialogOpen(true)}}/>}
            {!myCiv?.researching_tech_name && !techChoiceDialogOpen && <TaskIcon icon={scienceImg} onClick={() => {setTechChoiceDialogOpen(true)}} tooltip="Choose research" />}
            {canFoundCity && myCiv?.city_power > 100 && <TaskIcon icon={cityImg} onClick={() => {setFoundingCity(true)}} tooltip="Found city" />}
            {!myCiv?.trade_hub_id && anyUnhappyCities && !a7Tenet && myCiv.city_power > 0 && <TaskIcon content={<TradeHubIcon myGamePlayer={myGamePlayer}/>}
                tooltip={<div>Select trade hub (in city window). Unhappy cities: {unhappyCitiesList}</div>}
            />}
            {!myCiv.trade_hub_id && a7Tenet && myCiv.city_power > 0 && <TaskIcon content={<TradeHubIcon myGamePlayer={myGamePlayer}/>}
                tooltip="Select trade hub (in city window)."
            />}
            {/* {!myCiv?.target1 && myUnits.length > 0 && <TaskIcon icon={flag1Img} tooltip="Select primary flag" />}
            {!myCiv?.target2 && myUnits.length > 1 && <TaskIcon icon={flag2Img} tooltip="Select secondary flag" />} */}
            {myCities?.filter(city => city.projected_on_decline_leaderboard).map((city, index) => 
                <TaskIcon key={index} icon={phoenixImg} tooltip={city.civ_to_revolt_into ? `${city.name} on decline choices` : `${city.name} will enter decline options`} nobounce iconOpacity={city.civ_to_revolt_into ? 1 : 0.5}/>)
            }
        </div>
    }

export default TaskBar;

