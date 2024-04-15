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

const getBuildingType = ( buildingName, templates ) => {
    // TODO this is a mess
    const b = templates.BUILDINGS[buildingName]
    if (b && b.is_national_wonder) {
        return 'national-wonder'
    } else if (b) {
        return 'economic'
    } else if (templates.WONDERS[buildingName]) {
        return 'wonder'
    } else {
        return 'military'
    }
}



export const BriefBuildingDisplay = ({ buildingName, cost, clickable, style, templates, unitTemplatesByBuildingName, onClick, setHoveredBuilding, descriptions, disabledMsg }) => {
    const building = unitTemplatesByBuildingName?.[buildingName] || templates.BUILDINGS[buildingName];

    const type = getBuildingType(buildingName, templates)

    const description = descriptions?.[buildingName];

    let descriptionStr = null;

    if (description?.type === 'yield' && !(description.value_for_ai > description.value)) {
        descriptionStr = ` (+${description.value})`;
    }

    return (
        <div 
            className={`brief-building-card ${type} ${disabledMsg && 'disabled'} ${clickable ? 'clickable' : ''}`} 
            onClick={onClick}
            onMouseEnter={() => setHoveredBuilding(buildingName)} // set on mouse enter
            onMouseLeave={() => setHoveredBuilding(null)} // clear on mouse leave
            style={style}
        >
            <span className="building-name">{`${buildingName}${descriptionStr !== null ? descriptionStr : ''}`}</span>
            {cost && <span className="building-cost">{cost} wood</span>}
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