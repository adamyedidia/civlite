import React from 'react';
import UnitDisplay from './UnitDisplay'; // Adjust the path as needed
import './TechDisplay.css'; // Assuming you have a separate CSS file for styling
import BuildingDisplay from './BuildingDisplay';
import { romanNumeral } from "./romanNumeral";
import scienceImg from './images/science.png';
import fountainImg from './images/fountain.svg';

const TechDisplay = ({ tech, civ, templates, unitTemplatesByBuildingName, gameState, onClick, fountainIcon }) => {
    if (tech.name == "Renaissance") {
        tech.cost = civ.renaissance_cost
    }

    return (
        <div 
            className="tech-card" 
            onClick={onClick}
        >
            <h2>{romanNumeral(tech.advancement_level)}. {tech.name}</h2>
            <p>Cost: {tech.cost} <img src={scienceImg} alt="" height="14" /></p>
            <div className="unlocked-units">
                {tech.unlocks_units && tech.unlocks_units.map((unitName, index) => (
                    <UnitDisplay key={index} template={templates.UNITS[unitName]} />
                ))}
            </div>
            <div className="unlocked-units">
                {tech.unlocks_buildings && tech.unlocks_buildings.map((buildingName, index) => (
                    <BuildingDisplay 
                        key={index} 
                        buildingName={buildingName} 
                        templates={templates} 
                        unitTemplatesByBuildingName={unitTemplatesByBuildingName} 
                        onClick={() => {}} 
                    />
                ))}
            </div>
            {tech.text && <p>{tech.text}</p>}
            {fountainIcon && <img src={fountainImg} className="fountain-icon"/>}
        </div>
    );
};

export default TechDisplay;