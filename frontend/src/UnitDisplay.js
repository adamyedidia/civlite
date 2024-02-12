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
            onMouseEnter={() => setHoveredUnit(unit)} // set on mouse enter
            onMouseLeave={() => setHoveredUnit(null)} // clear on mouse leave
        >
            <span className="unit-name">{unit?.name}</span>
            <span className="unit-cost">{unit?.metal_cost} metal</span>
        </div>
    );
};

const UnitDisplay = ({ unit, hover }) => {
    if (!unit) {
        return null;
    }

    const unitAbilities = unit?.abilities?.length > 0 ? unit.abilities : unit?.template?.abilities

    return (
        <div className="unit-card">
            <h2>{unit?.name || unit?.template?.name}</h2>
            {/* <p>Type: {unit.type}</p> */}
            <p>Costs {unit?.metal_cost || unit?.template?.metal_cost} metal</p>
            <p>Building: {unit?.building_name || unit?.template?.building_name} (costs {unit?.wood_cost || unit?.template?.wood_cost} wood)</p>
            <p>Strength: {unit?.strength || unit?.template?.strength}</p>
            <p>Movement: {unit?.movement || unit?.template?.movement}</p>
            <p>Range: {unit?.range || unit?.template?.range}</p>
            <p>{unit?.tags?.join(', ') || unit?.template?.tags?.join(', ')}</p>
            {unitAbilities?.map((ability) => (
                <p>{ability.description}</p>
            ))}
        </div>
    );
};

export default UnitDisplay;