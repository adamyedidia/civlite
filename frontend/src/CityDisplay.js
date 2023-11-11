import React from 'react';
import './CityDisplay.css'; // You will need to create this CSS file

const CityDisplay = ({ city, setHoveredUnit }) => {
    const handleMouseEnter = (item) => {
        setHoveredUnit(item);
    };

    const handleMouseLeave = () => {
        setHoveredUnit(null);
    };

    const renderQueue = (queue, title) => (
        <>
            <h4>{title}</h4>
            <ul>
                {queue.map((item, index) => (
                    <li key={index}
                        onMouseEnter={() => handleMouseEnter(item)}
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
            {renderQueue(city.units_queue, 'Units Queue')}
            {renderQueue(city.buildings_queue, 'Buildings Queue')}
            {renderQueue(city.buildings, 'Buildings')}
        </div>
    );
};

export default CityDisplay;