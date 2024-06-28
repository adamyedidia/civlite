import React from 'react';
import UnitDisplay from './UnitDisplay';
import './BuildingDisplay.css';
import woodImage from './images/wood.png';

export const BriefBuildingDisplayTitle = ({ title }) => {
    return (
        <div 
            className="building-title-card" 
        >
            <span className="building-name">{title}</span>
        </div>        
    );
}

export const BriefBuildingDisplay = ({ buildingName, faded, buildingObj, hideCost, wonderCostsByAge, clickable, style, templates, unitTemplatesByBuildingName, onClick, setHoveredBuilding, setHoveredWonder, descriptions }) => {
    let building_type = '';
    let building;
    if (templates.BUILDINGS?.[buildingName]) {
        building_type = 'BUILDING';
        building = templates.BUILDINGS?.[buildingName];
    } else if (templates.WONDERS?.[buildingName]) {
        building_type = 'WONDER';
        building = templates.WONDERS?.[buildingName];
    } else if (unitTemplatesByBuildingName?.[buildingName]) {
        building_type = 'UNIT';
        building = unitTemplatesByBuildingName?.[buildingName];
    }
    const description = descriptions?.[buildingName];

    let descriptionStr = null;

    if (description?.type === 'yield' && !(description.value_for_ai > description.value)) {
        descriptionStr = ` (+${description.value})`;
    }

    const building_class = building_type == 'WONDER' ? 'wonder' : building_type == 'UNIT' ? 'military' : building?.exclusion_group ? 'core-economic' : 'economic';
    const cost = !hideCost && (building_type == 'UNIT' ? building.wood_cost : building_type == 'BUILDING' ? building.cost : building_type == 'WONDER' ? wonderCostsByAge[building.age] : null);
    return (
        <div 
            className={`brief-building-card ${building_class} ${clickable ? 'clickable' : ''} ${faded ? 'faded' : ''}`} 
            onClick={onClick}
            onMouseEnter={() => building_type == 'WONDER' ? setHoveredWonder(building) : setHoveredBuilding(buildingName)} // set on mouse enter
            onMouseLeave={() => building_type == 'WONDER' ? setHoveredWonder(null) : setHoveredBuilding(null)} // clear on mouse leave
            style={style}
        >
            <span className="building-name">{`${building?.building_name || building?.name}${descriptionStr !== null ? descriptionStr : ''}${buildingObj?.ruined ? ' (Ruins)' : ''}`}</span>
            {!hideCost && <span className="building-cost">{cost} <img src={woodImage} alt="" width="16" height="16" /></span>}
        </div>
    );
};

const BuildingDisplay = ({ buildingName, templates, unitTemplatesByBuildingName, onClick }) => {
    let building_type = '';
    let building;
    if (templates.BUILDINGS?.[buildingName]) {
        building_type = 'BUILDING';
        building = templates.BUILDINGS?.[buildingName];
    } else if (templates.WONDERS?.[buildingName]) {
        building_type = 'WONDER';
        building = templates.WONDERS?.[buildingName];
    } else if (unitTemplatesByBuildingName?.[buildingName]) {
        building_type = 'UNIT';
        building = unitTemplatesByBuildingName?.[buildingName];
    }
    const building_class = building_type == 'WONDER' ? 'wonder' : building_type == 'UNIT' ? 'military' : building?.exclusion_group ? 'core-economic' : 'economic';

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
            <div className={`building-card ${building_class}`} onClick={onClick}>
                <h2>{templates.BUILDINGS[buildingName]?.name}</h2>
                <p>Cost: {templates.BUILDINGS[buildingName]?.cost} wood</p>
                {templates.BUILDINGS[buildingName]?.vp_reward && <p>VP reward: {templates.BUILDINGS[buildingName]?.vp_reward}</p>}
                <ul>
                    {templates.BUILDINGS[buildingName]?.description.map((description, index) => (
                        <li key={index}>{description}</li>
                    ))}
                </ul>
            </div>
    );
};

export default BuildingDisplay;