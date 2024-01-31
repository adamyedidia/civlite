import React from 'react';
import './UpperRightDisplay.css';
import CityDisplay from './CityDisplay';
import { BriefTechDisplay } from './TechDisplay';

const CityPowerDisplay = ({ cityPower }) => {
    return (
        <div className="city-power-display">
            <p>City power: {cityPower.toFixed(1)}</p>
        </div>
    );
};

const CivVitalityDisplay = ({ civVitality }) => {
    const percentage = (civVitality * 100).toFixed(1);
    return (
        <div className="civ-vitality-display">
            <p>Civ vitality: {percentage}%</p>
        </div>
    );
}

const ScoreDisplay = ({ myGamePlayer }) => {
    const score = myGamePlayer?.score;
    return (
        <div className="score-display">
            <p>You have {score} VPs</p>
        </div>
    );
}

const UpperRightDisplay = ({ city, setHoveredUnit, setHoveredBuilding, myCiv, myGamePlayer }) => {

    return (
        <div className="upper-right-display">
            {city && <CityDisplay city={city} setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding} isFriendly={city?.civ?.id === myCiv?.id}/>}
            {myCiv?.tech_queue?.[0] && <BriefTechDisplay tech={myCiv?.tech_queue?.[0]} myCiv={myCiv} />}
            {myCiv && <CityPowerDisplay cityPower={myCiv.city_power} />}
            {myCiv && <CivVitalityDisplay civVitality={myCiv.vitality} />}
            {myGamePlayer && <ScoreDisplay myGamePlayer={myGamePlayer} />}
        </div>
    );
};

export default UpperRightDisplay;