import React from 'react';
import UnitDisplay from './UnitDisplay';
import './BuildingDisplay.css';

const BuildingDisplay = ({ buildingName, buildingTemplates, unitTemplates, onClick }) => {
    console.log(buildingName);
    console.log(unitTemplates[buildingName]);

    return (
        unitTemplates[buildingName] ? 
            <div className="building-card" onClick={onClick}>
                <h2>{unitTemplates[buildingName]?.building_name}</h2>
                <p>Cost: {unitTemplates[buildingName]?.wood_cost} wood</p>
                <div className="unlocked-units">
                    <UnitDisplay unit={unitTemplates[buildingName]} />
                </div>
            </div>
            :
            <div className="building-card" onClick={onClick}>
                <h2>{buildingTemplates[buildingName]?.building_name}</h2>
                <p>Cost: {buildingTemplates[buildingName]?.cost} wood</p>
            </div>

    );
};

export default BuildingDisplay;