import React, {  } from 'react';
import UnitDisplay from './UnitDisplay';
import './BuildingDisplay.css';
import woodImg from './images/wood.png';
import foodImg from './images/food.png';
import scienceImg from './images/science.png';
import metalImg from './images/metal.png';
import cityImg from './images/city.png';
import crownImg from './images/crown.png';
import { IconUnitDisplay } from './UnitDisplay';
import { ShrinkFontText } from './ShrinkFontText';
import { romanNumeral } from "./romanNumeral";
import { Tooltip } from '@mui/material';

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

export const BriefBuildingDisplay = ({ buildingName, faded, hideCost, clickable, style, templates, unitTemplatesByBuildingName, onClick, setHoveredBuilding, setHoveredWonder, setHoveredUnit, description, payoffTime, crowns }) => {
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
    let descriptionObj = "";
    const yields = description?.combined_display_yields;
    const displayYields = yields && (yields?.food || yields?.science || yields?.wood || yields?.metal);
    if (displayYields) {
        descriptionObj = <div style={{display: 'inline-block'}}><YieldsDisplay yields={yields} /></div>
    }

    const bldg_level = building.advancement_level;
    const building_class = building_type === 'WONDER' ? 'wonder' : building_type === 'UNIT' ? 'military' : building?.type === "urban" ? 'urban' : 'rural';
    const cost = !hideCost && (building_type === 'UNIT' ? building.wood_cost : building_type === 'BUILDING' ? building.cost : building_type === 'WONDER' ? building.cost : null);
    return (
        <div 
            className={`brief-building-card ${building_class} ${clickable ? 'clickable' : ''} ${faded ? 'faded' : ''}`} 
            onClick={clickable ? onClick : null}
            onMouseEnter={() => building_type === 'WONDER' ? setHoveredWonder(building) : building_type === 'UNIT' ? setHoveredUnit(building) : setHoveredBuilding(buildingName)} // set on mouse enter
            onMouseLeave={() => building_type === 'WONDER' ? setHoveredWonder(null) : building_type === 'UNIT' ? setHoveredUnit(null) : setHoveredBuilding(null)} // clear on mouse leave
            style={style}
        >
            <span className="building-name">
                <Tooltip title={payoffTime ? <><div>With vitality decay, a {buildingName} will take {payoffTime} turns to pay back building cost.</div> <div>Assumes resources equally valuable & building income doesn't change.</div></> : null}>
                {romanNumeral(bldg_level)}. {building?.building_name || building?.name}
                {descriptionObj ? <span> ({descriptionObj}) </span>: ""}
                {payoffTime && displayYields ? <span> ({payoffTime}⏱) </span> : ""}
                {crowns > 0 && <div style={{display: 'inline-block', marginLeft: '8px'}}><div style={{display: 'flex', gap: '4px'}}>
                    {[...Array(crowns)].map((_, index) =>  <img key={index} index={index} src={crownImg} alt="" width="16" height="16"/>)}
                </div></div>}
                </Tooltip>
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
    const building_class = building_type === 'WONDER' ? 'wonder' : building_type === 'UNIT' ? 'military' : building?.type === "urban" ? 'urban' : 'rural';

    return (
        building_type === 'UNIT' ? 
            <div className="building-card" onClick={onClick}>
                <h2>{building.building_name}</h2>
                <p>Cost: {building.wood_cost} wood</p>
                <div className="unlocked-units">
                    <UnitDisplay template={building} />
                </div>
            </div>
            :
            <div className={`building-card ${building_class}`} onClick={onClick}>
                <h2>{romanNumeral(building.advancement_level)}. {building.name}</h2>
                <p>Cost: {building.cost} wood</p>
                <ul>
                    {building.description.map((description, index) => (
                        <li key={index}>{description}</li>
                    ))}
                </ul>
            </div>
    );
};

export const ExpandButton = ({ cantExpandReason, handleClickDevelop, expandCost }) => {
    let content = (
        <div className={`existing-building-card expand ${cantExpandReason ? 'disabled' : 'enabled'}`} onClick={() => handleClickDevelop('rural')}>
            <div>Expand</div>
            <div className='price-label'>({expandCost} <img src={cityImg} alt="" height="16px"/>)</div>
        </div>
    );
    if (cantExpandReason) {
        content = <Tooltip title={cantExpandReason}>{content}</Tooltip>
    }
    return content
};

const DevelopButton = ({ cantDevelopReason, handleClickDevelop, developCost, hidden, text, type }) => {
    let content = (
        <>
            <div>{text}</div>
            <div>({developCost} <img src={cityImg} alt="" height="14px" width="auto"/>)</div>
        </>
    );
    if (cantDevelopReason) {
        content = <Tooltip title={cantDevelopReason}>{content}</Tooltip>
    }
    return         <div className={`develop-btn ${type} ${cantDevelopReason ? 'disabled' : 'enabled'} ${hidden ? 'hidden' : ''}`}
    onClick={() => handleClickDevelop(type)}>
        {content}
    </div>
}

export const ExistingBuildingDisplay = ({ buildingName, templates, emptyType, setHoveredBuilding, description, handleClickDevelop,
    militarizeBtn, urbanizeBtn, queuedBldg, urbanizeCost, militarizeCost, cityPower,
    cantMilitarizeReason, cantUrbanizeReason
}) => {
    const building = templates.BUILDINGS?.[buildingName];
    const developButtons = militarizeBtn || urbanizeBtn;
    const yields = description?.yields;  // TODO could display pre- and post-vitality yields differently.
    const buffed_units = description?.buffed_units;
    const other_effects = description?.other_strings;
    // TODO display other things from description.
    let emptyYields = {};
    switch (emptyType) {
        // TODO probably better for this to share a source fo truth with the python.
        case 'rural':
            emptyYields = {food: 1}
            break;
        case 'urban':
            emptyYields = {science: 2}
            break;
        case 'military':
            emptyYields = {metal: 2}
            break;
    }

    return (
        <div className={`existing-building-card ${emptyType || building?.type}`} onMouseEnter={() => setHoveredBuilding(buildingName)} onMouseLeave={() => setHoveredBuilding(null)}>
            {buildingName && <ShrinkFontText className="building-name" text={buildingName}/>}
            {queuedBldg && <div className="queued-bldg-name">
                {queuedBldg.template_name}
            </div>}
            {yields && 
                <YieldsDisplay yields={yields} />
            }
            {buffed_units && <div style={{display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'center'}}>
                {buffed_units.map((unit, index) => (
                    <IconUnitDisplay key={index} unitName={unit} templates={templates} size={30} />
                ))}
            </div>}
            {other_effects && <div style={{display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'center'}}>
                {other_effects.map((effect, index) => (
                    <div key={index}>{effect}</div>
                ))}
            </div>}
            {emptyYields && <div className="empty-yields"><YieldsDisplay yields={emptyYields} /></div>}
            {developButtons && <>
                <div className="develop-btns">
                <DevelopButton 
                    cantDevelopReason={cantMilitarizeReason}
                    handleClickDevelop={handleClickDevelop}
                    developCost={militarizeCost}
                    hidden={!militarizeBtn}
                    text="Militarize"
                    type="unit"
                />
                <DevelopButton 
                    cantDevelopReason={cantUrbanizeReason}
                    handleClickDevelop={handleClickDevelop}
                    developCost={urbanizeCost}
                    hidden={!urbanizeBtn}
                    text="Urbanize"
                    type="urban"
                />
                </div>
            </>}
        </div>
    );
};

export const ExistingMilitaryBuildingDisplay = ({ unitBuilding, queuedBldg, templates, handleSetInfiniteQueue, setHoveredUnit}) => {
    // TODO: this code is very duplicative with ExistingBuildingDisplay above.
    const unitName = unitBuilding?.template_name;
    const unit = templates.UNITS?.[unitName];
    const display_num = unitBuilding?.projected_unit_count > 3 ? 1 : unitBuilding?.projected_unit_count;

    return (
        <div className={`existing-building-card military ${unitBuilding?.delete_queued ? 'delete-queued' : ''} ${unitBuilding?.active ? 'infinite-queue' : ''} ${handleSetInfiniteQueue ? 'enabled' : 'disabled'}`} 
            onMouseEnter={() => setHoveredUnit(unit)} onMouseLeave={() => setHoveredUnit(null)}
            onClick={handleSetInfiniteQueue ? () => handleSetInfiniteQueue(unitName) : null}
        >
            {unitName && <ShrinkFontText className="building-name" text={unit.building_name || ""} />}
            {queuedBldg && <div className="queued-bldg-name">{templates.UNITS[queuedBldg.template_name].building_name || ""}</div>}
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
            {!unitName && <div className="empty-yields"><YieldsDisplay yields={{metal: 2}} /></div>}
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