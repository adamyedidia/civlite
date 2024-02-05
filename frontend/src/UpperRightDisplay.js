import React from 'react';
import './UpperRightDisplay.css';
import CityDisplay from './CityDisplay';
import { BriefTechDisplay } from './TechDisplay';

const CityPowerDisplay = ({ myCiv }) => {
    return (
        <div className="city-power-display">
            <p>City power: {myCiv?.city_power?.toFixed(1)} (+{myCiv?.projected_city_power_income?.toFixed(1)})</p>
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

const UpperRightDisplay = ({ city, isFriendlyCity, unitTemplates, setHoveredUnit, setHoveredBuilding, setHoveredTech, myCiv, myGamePlayer }) => {
    return (
        <div className="upper-right-display">
            {city && <CityDisplay city={city} setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding} isFriendly={isFriendlyCity} unitTemplates={unitTemplates}/>}
            {myCiv?.tech_queue?.[0] && <BriefTechDisplay tech={myCiv?.tech_queue?.[0]} myCiv={myCiv} setHoveredTech={setHoveredTech}/>}
            {myCiv && <CityPowerDisplay myCiv={myCiv} />}
            {myCiv && <CivVitalityDisplay civVitality={myCiv.vitality} />}
            {myGamePlayer && <ScoreDisplay myGamePlayer={myGamePlayer} />}
        </div>
    );
};

export default UpperRightDisplay;