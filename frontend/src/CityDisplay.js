import React from 'react';
import './CityDisplay.css'; // You will need to create this CSS file

const CityDisplay = ({ city, setHoveredUnit, setHoveredBuilding }) => {


    const handleMouseEnter = (item, itemType) => {
        if (itemType === 'unit') {
            setHoveredUnit(item);
        }
        else {
            setHoveredBuilding(item);
        }
    };

    const handleMouseLeave = () => {
        setHoveredUnit(null);
        setHoveredBuilding(null);
    };

    const renderQueue = (queue, title, itemType) => (
        <>
            <h4>{title}</h4>
            <ul>
                {queue.map((item, index) => (
                    <li key={index}
                        onMouseEnter={() => handleMouseEnter(item, itemType)}
                        onMouseLeave={handleMouseLeave}>
                        {item.name || item}
                    </li>
                ))}
            </ul>
        </>
    );

    return (
        <div className="city-display">
            <h3>{city.name} (Population: {city.population})</h3>
            {renderQueue(city.units_queue, 'Units Queue', 'unit')}
            {renderQueue(city.buildings_queue, 'Buildings Queue', 'building')}
            {renderQueue(city.buildings, 'Buildings', 'building')}
        </div>
    );
};

export default CityDisplay;