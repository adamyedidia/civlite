import React from 'react';
import './CityDisplay.css'; // You will need to create this CSS file

const CityDisplay = ({ city, setHoveredUnit, setHoveredBuilding, isFriendly }) => {
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
            {isFriendly && renderQueue(city.units_queue, 'Units Queue', 'unit')}
            {isFriendly && renderQueue(city.buildings_queue, 'Buildings Queue', 'building')}
            {isFriendly && renderQueue(city.buildings, 'Buildings', 'building')}
            {isFriendly && <ul>
                <li>Food: {city.food.toFixed(1)} (+{city.projected_food_income.toFixed(1)}) / {city.growth_cost}</li>
                <li>Wood: {city.wood.toFixed(1)} (+{city.projected_wood_income.toFixed(1)})</li>
                <li>Metal: {city.metal.toFixed(1)} (+{city.projected_metal_income.toFixed(1)})</li>
            </ul>}
        </div>
    );
};

export default CityDisplay;