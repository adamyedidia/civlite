import React from 'react';
import UnitDisplay from './UnitDisplay'; // Adjust the path as needed
import './TechDisplay.css'; // Assuming you have a separate CSS file for styling
import BuildingDisplay from './BuildingDisplay';
import { romanNumeral } from './TechListDialog';

export const TechNameWithStars = (tech, gameState) => {
    return `${tech.name}${Array.from({length: gameState.tech_bonuses_remaining[tech.name]}, () => '*').join('')}`
}

const TechDisplay = ({ tech, civ, templates, unitTemplatesByBuildingName, gameState, onClick }) => {
    if (tech.name == "Renaissance") {
        tech.cost = civ.renaissance_cost
    }

    const breakthroughs_left = gameState.tech_bonuses_remaining[tech.name]

    return (
        <div 
            className="tech-card" 
            onClick={onClick}
        >
            <h2>{romanNumeral(tech.advancement_level)}{tech && `. ${TechNameWithStars(tech, gameState)}`}</h2>
            <p>Cost: {breakthroughs_left > 0 ? `*${tech.breakthrough_cost}* science (${tech.cost} base)` : `${tech.cost} science`}</p>
            <div className="unlocked-units">
                {tech.unlocks_units && tech.unlocks_units.map((unitName, index) => (
                    <UnitDisplay key={index} unit={templates.UNITS[unitName]} />
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
            {tech.breakthrough_effect && <div style={{opacity: breakthroughs_left > 0 ? 1 : 0.3}}>
                <p>Breakthrough: {tech.breakthrough_effect}</p>
            </div>}
            {tech.name == "Renaissance" && <>
                <p>Re-enable all discarded technologies</p>
                <p>Gain 25 VPs</p>
            </>
            }
        </div>
    );
};

export default TechDisplay;