import React from 'react';
import './UnitDisplay.css'; // Assuming you have a separate CSS file for styling

export const BriefUnitDisplayTitle = ({ title }) => {
    return (
        <div 
            className="unit-title-card" 
        >
            <span className="unit-name">{title}</span>
        </div>        
    );
}

export const BriefUnitDisplay = ({ unitName, unitTemplates, onClick, setHoveredUnit }) => {
    const unit = unitTemplates[unitName]

    return (
        <div 
            className="brief-unit-card" 
            onClick={onClick}
            onMouseEnter={() => setHoveredUnit(unitName)} // set on mouse enter
            onMouseLeave={() => setHoveredUnit(null)} // clear on mouse leave
        >
            <span className="unit-name">{unit?.name}</span>
            <span className="unit-cost">{unit?.metal_cost} metal</span>
        </div>
    );
};

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