import React from 'react';
import UnitDisplay from './UnitDisplay';
import './BuildingDisplay.css';

export const BriefBuildingDisplayTitle = ({ title }) => {
    return (
        <div 
            className="building-title-card" 
        >
            <span className="building-name">{title}</span>
        </div>        
    );
}

export const BriefBuildingDisplay = ({ buildingName, buildingTemplates, unitTemplatesByBuildingName, onClick, setHoveredBuilding }) => {
    console.log(unitTemplatesByBuildingName);
    const building = unitTemplatesByBuildingName[buildingName] || buildingTemplates[buildingName];

    console.log(building);

    return (
        <div 
            className="brief-building-card" 
            onClick={onClick}
            onMouseEnter={() => setHoveredBuilding(buildingName)} // set on mouse enter
            onMouseLeave={() => setHoveredBuilding(null)} // clear on mouse leave
        >
            <span className="building-name">{building?.building_name || building?.name}</span>
            <span className="building-cost">{building?.wood_cost || building?.cost} wood</span>
        </div>
    );
};

const BuildingDisplay = ({ buildingName, buildingTemplates, unitTemplatesByBuildingName, onClick }) => {
    console.log(buildingName);
    console.log(unitTemplatesByBuildingName[buildingName]);
    console.log(buildingTemplates[buildingName]);

    return (
        unitTemplatesByBuildingName[buildingName] ? 
            <div className="building-card" onClick={onClick}>
                <h2>{unitTemplatesByBuildingName[buildingName]?.building_name}</h2>
                <p>Cost: {unitTemplatesByBuildingName[buildingName]?.wood_cost} wood</p>
                <div className="unlocked-units">
                    <UnitDisplay unit={unitTemplatesByBuildingName[buildingName]} />
                </div>
            </div>
            :
            <div className="building-card" onClick={onClick}>
                <h2>{buildingTemplates[buildingName]?.name}</h2>
                <p>Cost: {buildingTemplates[buildingName]?.cost} wood</p>
                <ul>
                    {buildingTemplates[buildingName]?.abilities.map((ability, index) => (
                        <li key={index}>{ability.description}</li>
                    ))}
                </ul>                
            </div>

    );
};

export default BuildingDisplay;