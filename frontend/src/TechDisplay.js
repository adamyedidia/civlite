import React from 'react';
import UnitDisplay from './UnitDisplay'; // Adjust the path as needed
import './TechDisplay.css'; // Assuming you have a separate CSS file for styling
import BuildingDisplay from './BuildingDisplay';
import { Button } from '@mui/material';

export const BriefTechDisplay = ({ tech, myCiv, setHoveredTech, techTemplates, setTechListDialogOpen }) => {
    return (
        <div className="brief-tech-card"
            onMouseEnter={tech ? () => setHoveredTech(techTemplates[tech.name]) : () => {}}
            onMouseLeave={() => setHoveredTech(null)}        
        >
            {tech && <p>Researching {tech.name}</p>}
            {myCiv && <p>You currently have: {myCiv?.science?.toFixed(1)} (+{myCiv?.projected_science_income?.toFixed(1)}) science</p>}
            {tech && <p>Cost: {tech.cost} science</p>}
            <Button 
                variant="contained" 
                color="primary"
                onClick={() => setTechListDialogOpen(true)}
            >
                View researched techs
            </Button>
        </div>
    );
};

// const BuildingDisplay = ({ buildingName, buildingTemplates, unitTemplatesByBuildingName, onClick }) => {

const TechDisplay = ({ tech, unitTemplates, buildingTemplates, unitTemplatesByBuildingName, gameState, onClick }) => {
    return (
        <div 
            className="tech-card" 
            onClick={onClick}
        >
            <h2>{tech.name}</h2>
            <p>Cost: {tech.cost} science</p>
            <div className="unlocked-units">
                {tech.unlocks_units && tech.unlocks_units.map((unitName, index) => (
                    <UnitDisplay key={index} unit={unitTemplates[unitName]} />
                ))}
            </div>
            <div className="unlocked-units">
                {tech.unlocks_buildings && tech.unlocks_buildings.map((buildingName, index) => (
                    <BuildingDisplay 
                        key={index} 
                        buildingName={buildingName} 
                        buildingTemplates={buildingTemplates} 
                        unitTemplatesByBuildingName={unitTemplatesByBuildingName} 
                        disabledMsg={gameState.wonders_built_to_civ_id.hasOwnProperty(buildingName) ? `==  Built by ${gameState.civs_by_id[gameState.wonders_built_to_civ_id[buildingName]].name}  ==` : ""} 
                        onClick={() => {}} 
                    />
                ))}
            </div>
        </div>
    );
};

export default TechDisplay;