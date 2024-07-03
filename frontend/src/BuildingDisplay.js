import React from 'react';
import UnitDisplay from './UnitDisplay';
import './BuildingDisplay.css';
import woodImg from './images/wood.png';
import foodImg from './images/food.png';
import scienceImg from './images/science.png';
import metalImg from './images/metal.png';
import { WithTooltip } from './WithTooltip';

const SingleYieldDisplay = ({ yield_value, img }) => {
    const rounded_val = Number.isInteger(yield_value) ? yield_value : yield_value.toFixed(0);
    return (
        <div className="single-yield-display">
            {rounded_val}<img src={img} alt=""/>
        </div>
    );
};

const YieldsDisplay = ({ yields }) => {
    return (
        <div className="yields-display">
            {yields.food > 0 && <SingleYieldDisplay yield_value={yields.food} img={foodImg} />}
            {yields.science > 0 && <SingleYieldDisplay yield_value={yields.science} img={scienceImg} />}
            {yields.wood > 0 && <SingleYieldDisplay yield_value={yields.wood} img={woodImg} />}
            {yields.metal > 0 && <SingleYieldDisplay yield_value={yields.metal} img={metalImg} />}
        </div>
    );
};

export const BriefBuildingDisplayTitle = ({ title }) => {
    return (
        <div 
            className="building-title-card" 
        >
            <span className="building-name">{title}</span>
        </div>        
    );
}

export const BriefBuildingDisplay = ({ buildingName, faded, buildingObj, hideCost, wonderCostsByAge, clickable, style, templates, unitTemplatesByBuildingName, onClick, setHoveredBuilding, setHoveredWonder, descriptions, yields, payoffTime }) => {
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
    let descriptionObj = "";
    const displayYields = yields && (yields?.food || yields?.science || yields?.wood || yields?.metal);
    if (displayYields) {
        descriptionObj = <div style={{display: 'inline-block'}}><YieldsDisplay yields={yields} /></div>
    }
    else if (description?.type === 'yield' && !(description.value_for_ai > description.value)) {
        const rounded_val = Number.isInteger(description.value) ? description.value : description.value.toFixed(1);
        descriptionObj = `+${rounded_val}`;
    }

    const building_class = building_type == 'WONDER' ? 'wonder' : building_type == 'UNIT' ? 'military' : building?.type == "urban" ? 'urban' : 'rural';
    const cost = !hideCost && (building_type == 'UNIT' ? building.wood_cost : building_type == 'BUILDING' ? building.cost : building_type == 'WONDER' ? wonderCostsByAge[building.age] : null);
    return (
        <div 
            className={`brief-building-card ${building_class} ${clickable ? 'clickable' : ''} ${faded ? 'faded' : ''}`} 
            onClick={onClick}
            onMouseEnter={() => building_type == 'WONDER' ? setHoveredWonder(building) : setHoveredBuilding(buildingName)} // set on mouse enter
            onMouseLeave={() => building_type == 'WONDER' ? setHoveredWonder(null) : setHoveredBuilding(null)} // clear on mouse leave
            style={style}
        >
            <span className="building-name">
                <WithTooltip alignBottom={true} tooltip={payoffTime ? <><div>With vitality decay, a {buildingName} will take {payoffTime} turns to pay back building cost.</div> <div>Assumes resources equally valuable & building income doesn't change.</div></> : null}>
                {building?.building_name || building?.name}
                {descriptionObj ? <span> ({descriptionObj}) </span>: ""}
                {payoffTime && displayYields ? <span> ({payoffTime}⏱) </span> : ""}
                </WithTooltip>
            </span>
            {!hideCost && <span className="building-cost">{cost} <img src={woodImg} alt="" width="16" height="16" /></span>}
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
    const building_class = building_type == 'WONDER' ? 'wonder' : building_type == 'UNIT' ? 'military' : building?.type == "urban" ? 'urban' : 'rural';

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

export const ExistingBuildingDisplay = ({ buildingName, templates, onClick, emptyType, setHoveredBuilding, yields }) => {
    const building = templates.BUILDINGS?.[buildingName];
    return (
        <div className={`existing-building-card ${emptyType || building?.type}`} onClick={onClick} onMouseEnter={() => setHoveredBuilding(buildingName)} onMouseLeave={() => setHoveredBuilding(null)}>
            <div className="building-name">{buildingName || ""}</div>
            {yields?.[buildingName] && 
                <YieldsDisplay yields={yields[buildingName]} />
            }
        </div>
    );
};

export default BuildingDisplay;