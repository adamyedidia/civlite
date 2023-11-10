import React from 'react';
import './UnitDisplay.css'; // Assuming you have a separate CSS file for styling

const UnitDisplay = ({ unit }) => {
    return (
        <div className="unit-card">
            <h2>{unit.name}</h2>
            {/* <p>Type: {unit.type}</p> */}
            <p>Building: {unit.building_name}</p>
            <p>Metal Cost: {unit.metal_cost}</p>
            <p>Wood Cost: {unit.wood_cost}</p>
            <p>Strength: {unit.strength}</p>
            <p>Movement: {unit.movement}</p>
            <p>Range: {unit.range}</p>
            {unit.ranged ? <p>Ranged</p> : null}
            {unit.mounted ? <p>Mounted</p> : null}
            {unit.abilities.map((ability) => {
                <p>{ability.description}</p>
            })}
        </div>
    );
};

export default UnitDisplay;