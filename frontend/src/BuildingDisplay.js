import React from 'react';
import UnitDisplay from './UnitDisplay';
import './BuildingDisplay.css';
import woodImg from './images/wood.png';
import foodImg from './images/food.png';
import scienceImg from './images/science.png';
import metalImg from './images/metal.png';
import cityImg from './images/city.png';
import { WithTooltip } from './WithTooltip';
import { IconUnitDisplay } from './UnitDisplay';

const SingleYieldDisplay = ({ yield_value, img }) => {
    const rounded_val = Number.isInteger(yield_value) ? yield_value : yield_value.toFixed(0);
    return (
        <div className="single-yield-display">
            {rounded_val}<img src={img} alt=""/>
        </div>
    );
};

export const YieldsDisplay = ({ yields }) => {
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

export const BriefBuildingDisplay = ({ buildingName, faded, hideCost, wonderCostsByAge, clickable, style, templates, unitTemplatesByBuildingName, onClick, setHoveredBuilding, setHoveredWonder, setHoveredUnit, descriptions, yields, payoffTime }) => {
    let building_type = '';
    let building;
    if (templates.BUILDINGS?.[buildingName]) {
        building_type = 'BUILDING';
        building = templates.BUILDINGS[buildingName];
    } else if (templates.WONDERS?.[buildingName]) {
        building_type = 'WONDER';
        building = templates.WONDERS[buildingName];
    } else if (templates.UNITS?.[buildingName]) {
        building_type = 'UNIT';
        building = templates.UNITS[buildingName];
    } else if (unitTemplatesByBuildingName?.[buildingName]) {
        building_type = 'UNIT';
        building = unitTemplatesByBuildingName[buildingName];
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
            onMouseEnter={() => building_type == 'WONDER' ? setHoveredWonder(building) : building_type == 'UNIT' ? setHoveredUnit(building) : setHoveredBuilding(buildingName)} // set on mouse enter
            onMouseLeave={() => building_type == 'WONDER' ? setHoveredWonder(null) : building_type == 'UNIT' ? setHoveredUnit(null) : setHoveredBuilding(null)} // clear on mouse leave
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
    } else if (templates.UNITS?.[buildingName]) {
        building_type = 'UNIT';
        building = templates.UNITS[buildingName];
    } else if (unitTemplatesByBuildingName?.[buildingName]) {
        building_type = 'UNIT';
        building = unitTemplatesByBuildingName[buildingName];
    }
    const building_class = building_type == 'WONDER' ? 'wonder' : building_type == 'UNIT' ? 'military' : building?.type == "urban" ? 'urban' : 'rural';

    return (
        building_type == 'UNIT' ? 
            <div className="building-card" onClick={onClick}>
                {buildingName}
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

export const ExpandButton = ({ expandSufficientPower, handleClickDevelop }) => {
    return (
        <div className={`existing-building-card expand ${expandSufficientPower ? 'sufficient-power' : 'insufficient-power'}`} onClick={() => handleClickDevelop('rural')}>
            <div>Expand</div>
            <div className="price-label">50 <img src={cityImg} alt="" height="16px"/></div>
        </div>
    );
};

export const ExistingBuildingDisplay = ({ buildingName, templates, emptyType, setHoveredBuilding, yields, handleClickDevelop,
    militarizeBtn, urbanizeBtn, canAffordDevelop
}) => {
    const building = templates.BUILDINGS?.[buildingName];
    const developButtons = militarizeBtn || urbanizeBtn;
    return (
        <div className={`existing-building-card ${emptyType || building?.type}`} onMouseEnter={() => setHoveredBuilding(buildingName)} onMouseLeave={() => setHoveredBuilding(null)}>
            <div className="building-name">{buildingName || ""}</div>
            {yields?.[buildingName] && 
                <YieldsDisplay yields={yields[buildingName]} />
            }
            {developButtons && <>
                <div className="develop-btns">
                <div className={`develop-btn unit ${canAffordDevelop ? 'enabled' : 'disabled'} ${militarizeBtn ? '' : 'hidden'}`}
                onClick={() => handleClickDevelop('unit')}>
                    <div>Militarize</div>
                    <div>(100 <img src={cityImg} alt="" height="14px" width="auto"/>)</div>
                </div>
                <div className={`develop-btn urban ${canAffordDevelop ? 'enabled' : 'disabled'} ${urbanizeBtn ? '' : 'hidden'}`}
                onClick={() => handleClickDevelop('urban')}>
                    <div>Urbanize</div>
                    <div>(100 <img src={cityImg} alt="" height="14px" width="auto"/>)</div>
                </div>
                </div>
            </>}
        </div>
    );
};

export const ExistingMilitaryBuildingDisplay = ({ unitBuilding, templates, handleSetInfiniteQueue, setHoveredUnit}) => {
    const unitName = unitBuilding?.template_name;
    const unit = templates.UNITS?.[unitName];
    const display_num = unitBuilding?.projected_unit_count > 3 ? 1 : unitBuilding?.projected_unit_count;
    return (
        <div className={`existing-building-card military ${unitBuilding?.delete_queued ? 'delete-queued' : ''} ${unitBuilding?.active ? 'infinite-queue' : ''} ${handleSetInfiniteQueue ? 'enabled' : 'disabled'}`} 
            onMouseEnter={() => setHoveredUnit(unit)} onMouseLeave={() => setHoveredUnit(null)}
            onClick={handleSetInfiniteQueue ? () => handleSetInfiniteQueue(unitName) : null}
        >
            {unitName && <div className="building-name">{unit.building_name || ""}</div>}
            {unitName && unitBuilding.active && <div className="build-num">
                {Array.from(({length: display_num})).map((_, index) => 
                <IconUnitDisplay
                    key={index}
                    unitName={unitName} 
                    templates={templates} 
                    setHoveredUnit={setHoveredUnit} 
                    size={30}
                />)}
                {unitBuilding.projected_unit_count > 3 ? `x${unitBuilding.projected_unit_count}` : ''}
                </div>
            }
            {unitName && <div style={{"display": "flex", "alignItems": "center", "justifyContent": "center", "fontSize": "16px", "position": "absolute", "bottom": "2px", "left": "4px"}}>
                    {Math.floor(unitBuilding.metal)} / {templates.UNITS[unitName].metal_cost}
                    <img src={metalImg} alt="" height="10px"/>
                </div>}
            {unitName && unitBuilding.active && <div style={{"display": "flex", "alignItems": "center", "justifyContent": "center", "fontSize": "16px", "position": "absolute", "bottom": "2px", "right": "4px"}}>
                {Math.floor(unitBuilding.production_rate * 100)}%
            </div>}
        </div>
    );
};

export default BuildingDisplay;