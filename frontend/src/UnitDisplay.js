import React from 'react';
import './UnitDisplay.css'; // Assuming you have a separate CSS file for styling
import { lowercaseAndReplaceSpacesWithUnderscores } from './lowercaseAndReplaceSpacesWithUnderscores.js';

export const BriefUnitDisplayTitle = ({ title }) => {
    return (
        <div 
            className="unit-title-card" 
        >
            <span className="unit-name">{title}</span>
        </div>        
    );
}

export const BriefUnitDisplay = ({ unitName, templates, onClick, setHoveredUnit }) => {
    const unit = templates.UNITS[unitName]

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

export const IconUnitDisplay = ({ unitName, templates, style, onClick, setHoveredUnit }) => {
    const unit = templates.UNITS[unitName];
    const unitImage = `/images/${lowercaseAndReplaceSpacesWithUnderscores(unit.name)}.svg`; // Path to the unit SVG image
    return (
        <div 
            className="unit-icon" 
            onClick={onClick}
            onMouseEnter={() => setHoveredUnit && setHoveredUnit(unit)} // set on mouse enter
            onMouseLeave={() => setHoveredUnit && setHoveredUnit(null)} // clear on mouse leave
            style={{ ...style, backgroundImage: `url(${unitImage})`}}
        />
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
            {unit?.building_name && <p>Building: {unit?.building_name || unit?.template?.building_name} (costs {unit?.wood_cost || unit?.template?.wood_cost} wood)</p>}
            <p>Strength: {unit?.strength || unit?.template?.strength}</p>
            <p>Movement: {unit?.movement || unit?.template?.movement}</p>
            <p>Range: {unit?.range || unit?.template?.range}</p>
            <p>{unit?.tags?.join(', ') || unit?.template?.tags?.join(', ')}</p>
            {unitAbilities?.map((ability) => (
                <p key={ability.name}>{ability.description}</p>
            ))}
        </div>
    );
};

export default UnitDisplay;