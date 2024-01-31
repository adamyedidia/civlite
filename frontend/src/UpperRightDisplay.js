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

const UpperRightDisplay = ({ city, setHoveredUnit, setHoveredBuilding, myCiv }) => {

    return (
        <div className="upper-right-display">
            {city && <CityDisplay city={city} setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding} isFriendly={city?.civ?.id === myCiv?.id}/>}
            {myCiv?.tech_queue?.[0] && <BriefTechDisplay tech={myCiv?.tech_queue?.[0]} myCiv={myCiv} />}
            {myCiv && <CityPowerDisplay cityPower={myCiv.city_power} />}
            {myCiv && <CivVitalityDisplay civVitality={myCiv.vitality} />}
        </div>
    );
};

export default UpperRightDisplay;