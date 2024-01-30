import React from 'react';
import UnitDisplay from './UnitDisplay'; // Adjust the path as needed
import './TechDisplay.css'; // Assuming you have a separate CSS file for styling

export const BriefTechDisplay = ({ tech }) => {
    return (
        <div className="brief-tech-card">
            <p>Researching {tech.name}</p>
            <p>Cost: {tech.cost} science</p>
        </div>
    );
};

const TechDisplay = ({ tech, unitTemplates, onClick }) => {
    return (
        <div className="tech-card" onClick={onClick}>
            <h2>{tech.name}</h2>
            <p>Cost: {tech.cost} science</p>
            <div className="unlocked-units">
                {tech.unlocks_units && tech.unlocks_units.map((unitName, index) => (
                    <UnitDisplay key={index} unit={unitTemplates[unitName]} />
                ))}
            </div>
        </div>
    );
};

export default TechDisplay;