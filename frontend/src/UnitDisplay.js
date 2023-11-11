import React from 'react';
import './UnitDisplay.css'; // Assuming you have a separate CSS file for styling

const UnitDisplay = ({ unit, hover }) => {
    return (
        <div className="unit-card">
            <h2>{unit.name}</h2>
            {/* <p>Type: {unit.type}</p> */}
            <p>Costs {unit.metal_cost} metal</p>
            <p>Building: {unit.building_name} (costs {unit.wood_cost} wood)</p>
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