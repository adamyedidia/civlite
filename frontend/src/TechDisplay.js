import React from 'react';
import UnitDisplay from './UnitDisplay'; // Adjust the path as needed
import './TechDisplay.css'; // Assuming you have a separate CSS file for styling
import BuildingDisplay from './BuildingDisplay';
import { romanNumeral } from "./romanNumeral";
import scienceImg from './images/science.png';
import fountainImg from './images/fountain.svg';
import { TextOnIcon } from './TextOnIcon';
import vpImg from './images/crown.png';
import { DetailedNumberTooltipContent } from './DetailedNumber';

const TechDisplay = ({ tech, civ, templates, unitTemplatesByBuildingName, gameState, onClick, fountainIcon }) => {
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
            <div className="upper-right-floaters">
                {civ && civ.vps_per_tech_level[tech.advancement_level] && <TextOnIcon 
                        image={vpImg}
                        tooltip={<DetailedNumberTooltipContent detailedNumber={civ.vps_per_tech_level[tech.advancement_level]} />}
                        offset={10}
                    >
                        {civ.vps_per_tech_level[tech.advancement_level].value}
                    </TextOnIcon>
                }
                {fountainIcon && <img src={fountainImg} className="fountain-icon"/>}
            </div>
        </div>
    );
};

export default TechDisplay;