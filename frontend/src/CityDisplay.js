import React from 'react';
import './CityDisplay.css'; // You will need to create this CSS file

const CityDisplay = ({ city, unitTemplates, setHoveredUnit, setHoveredBuilding, isFriendly }) => {
    return (
        <div className="city-display">
            <h3>{city.name} (Population: {city.population})</h3>
        </div>
    );
};

export default CityDisplay;