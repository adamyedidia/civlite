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

export const BriefBuildingDisplay = ({ buildingName, hideCost, clickable, style, templates, unitTemplatesByBuildingName, onClick, setHoveredBuilding, descriptions, disabledMsg }) => {
    const building = unitTemplatesByBuildingName?.[buildingName] || templates.BUILDINGS[buildingName];

    const description = descriptions?.[buildingName];

    let descriptionStr = null;

    if (description?.type === 'yield') {
        descriptionStr = ` (+${description.value})`;
    }

    return (
        <div 
            className={`brief-building-card ${building?.is_wonder ? 'wonder' : building?.is_national_wonder ? 'national-wonder' : unitTemplatesByBuildingName?.[buildingName] ? 'military' : 'economic'} ${disabledMsg && 'disabled'} ${clickable ? 'clickable' : ''}`} 
            onClick={onClick}
            onMouseEnter={() => setHoveredBuilding(buildingName)} // set on mouse enter
            onMouseLeave={() => setHoveredBuilding(null)} // clear on mouse leave
            style={style}
        >
            <span className="building-name">{`${building?.building_name || building?.name}${descriptionStr !== null ? descriptionStr : ''}`}</span>
            {!hideCost && <span className="building-cost">{building?.wood_cost || building?.cost} wood</span>}
        </div>
    );
};

const BuildingDisplay = ({ buildingName, templates, unitTemplatesByBuildingName, disabledMsg, onClick }) => {
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
            <div className={`building-card ${disabledMsg ? 'wonder-disabled' : ''}`} onClick={onClick}>
                {disabledMsg && <p className='wonder-disabled-msg'>{disabledMsg}</p>}
                <h2>{templates.BUILDINGS[buildingName]?.name}</h2>
                <p>Cost: {templates.BUILDINGS[buildingName]?.cost} wood</p>
                {templates.BUILDINGS[buildingName]?.vp_reward && <p>VP reward: {templates.BUILDINGS[buildingName]?.vp_reward}</p>}
                {templates.BUILDINGS[buildingName]?.is_wonder && <p>Wonder</p>}
                {templates.BUILDINGS[buildingName]?.is_national_wonder && <p>National Wonder</p>}
                <ul>
                    {templates.BUILDINGS[buildingName]?.abilities.map((ability, index) => (
                        <li key={index}>{ability.description}</li>
                    ))}
                </ul>
            </div>
    );
};

export default BuildingDisplay;