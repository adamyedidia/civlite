import React from 'react';
import './TaskBar.css';

import { WithTooltip } from './WithTooltip';

import cityImg from './images/city.png';
import scienceImg from './images/science.png';
import tradeHubImg from './images/tradehub.png';

// For images in the public/images directory, use the public URL path
const flag1Img = `${process.env.PUBLIC_URL}/images/flag.svg`;
const flag2Img = `${process.env.PUBLIC_URL}/images/purple_flag.svg`;

const TaskIcon = ({icon, onClick, tooltip}) => {
    return <div className={`task-icon ${onClick ? 'clickable' : ''}`} onClick={onClick}>
        <WithTooltip tooltip={tooltip}>
            <img src={icon} />
        </WithTooltip>
    </div>
}


export const TaskBar = ({myCiv, myCities, myUnits, canFoundCity, setSelectedCity, setFoundingCity, setTechChoiceDialogOpen, techChoiceDialogOpen}) => {
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
        {canFoundCity && myCiv?.city_power > 100 && <TaskIcon icon={cityImg} onClick={() => {setFoundingCity(true)}} tooltip="Found city" />}
        {!myCiv?.researching_tech_name && !techChoiceDialogOpen && <TaskIcon icon={scienceImg} onClick={() => {setTechChoiceDialogOpen(true)}} tooltip="Choose research" />}
        {!myCiv?.trade_hub_id && anyUnhappyCities && <TaskIcon icon={tradeHubImg} 
            tooltip={<div>Select trade hub (in city window). Unhappy cities: {unhappyCitiesList}</div>}
        />}
        {!myCiv?.target1 && myUnits.length > 0 && <TaskIcon icon={flag1Img} tooltip="Select primary flag" />}
        {!myCiv?.target2 && myUnits.length > 1 && <TaskIcon icon={flag2Img} tooltip="Select secondary flag" />}
    </div>
}

export default TaskBar;

