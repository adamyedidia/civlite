import React, { useState } from 'react';
import './CityDetailWindow.css';

import { Button, Select, MenuItem } from '@mui/material';

import { BriefBuildingDisplay, BriefBuildingDisplayTitle } from './BuildingDisplay';
import { IconUnitDisplay } from './UnitDisplay';
import foodImg from './images/food.png';
import woodImg from './images/wood.png';
import metalImg from './images/metal.png';
import scienceImg from './images/science.png';
import happyImg from './images/happyface.png';
import neutralImg from './images/neutralface.png';
import sadImg from './images/sadface.png';
import cityImg from './images/city.png';
import declineImg from './images/phoenix.png';
import tradeHubImg from './images/tradehub.png';
import eyeImg from './images/view.png';
import closedEyeImg from './images/hide.png';
import workerImg from './images/worker.png';
import { CityDetailPanel } from './CityDetailPanel.js';
import { TextOnIcon } from './TextOnIcon.js';
import ProgressBar from './ProgressBar.js';
import { WithTooltip } from './WithTooltip.js';

const UnitQueueOption = ({unitName, isCurrentIQUnit, canBuild, templates, setHoveredUnit, handleSetInfiniteQueue}) => {
    let content = <div className={`unit-choice ${isCurrentIQUnit ? 'infinite-queue' : ''} ${canBuild ? 'enabled' : 'disabled'}`}
        onClick={(event) => {
            if (!canBuild) return;
            // click to toggle infinite queue
            if (isCurrentIQUnit) {
                handleSetInfiniteQueue("")
            } else {
                handleSetInfiniteQueue(unitName);
            }
        }}>
        <IconUnitDisplay 
            unitName={unitName} 
            templates={templates} 
            setHoveredUnit={setHoveredUnit} 
            style={{borderRadius: '25%'}} 
        />
        {unitName && <div style={{"display": "flex", "alignItems": "center", "justifyContent": "center", "fontSize": "16px"}}>
            {templates.UNITS[unitName].metal_cost}
            <img src={metalImg} alt="" height="10px"/>
            </div>}
        </div>
    if (unitName) {
        content = <WithTooltip tooltip={canBuild ? "Toggle infinite queue." : "Cannot build units here."}>
            {content}
        </WithTooltip>
    }
    return content;
}

const queueBuildDepth = (resourcesAvailable, queue, getCostOfItem) => {
    let available = resourcesAvailable
    for (let index = 0; index < queue.length; index++) {
        const item = queue[index];
        const itemCost = getCostOfItem(item);
        available -= itemCost;
        if (available < 0) {
            return index - 1;
        }
    }
    return 9999
}

const MakeTerritory = ({myTerritoryCapitals, handleMakeTerritory, myCiv}) => {
    const [otherCitySelected, setOtherCitySelected] = useState(0);

    const roomForNewTerritory = myTerritoryCapitals.length < myCiv.max_territories;

    const enoughCityPower = myCiv.city_power >= 100;

    const submitClickIfValid = () => {
        if (roomForNewTerritory) {
            handleMakeTerritory(null);
            return
        }
        else if (otherCitySelected !== 0) {
            handleMakeTerritory(otherCitySelected);
        } else {
            document.querySelector('.make-territory-select').classList.add('flash-select');
            setTimeout(() => {
                document.querySelector('.make-territory-select').classList.remove('flash-select');
            }, 1000);
        }
    }

    return <div className='make-territory-area'>
        <WithTooltip tooltip={enoughCityPower ? "Make this city a territory instead of a puppet." : "Not enough City Power."}>
        <Button
            variant="contained"
            style = {{
                width: '180px',
                margin: '10px',
                padding: '20px 50px',
            }}
            onClick={submitClickIfValid}
            disabled={!enoughCityPower}
        >
            Make Territory
            <TextOnIcon image={cityImg} style={{marginLeft: '10px', minWidth: '50px', height: '50px', color: 'black', opacity: enoughCityPower ? 1.0 : 0.3}} offset={20}>
                -100
            </TextOnIcon>
        </Button>
        </WithTooltip>
        {!roomForNewTerritory && <Select
            value={otherCitySelected}
            onChange={(e) => setOtherCitySelected(e.target.value)}
            variant="standard"
            className="make-territory-select"
            disabled={!enoughCityPower}
        >
            <MenuItem value={0}>Instead of ... </MenuItem>
            {myTerritoryCapitals.map(city => <MenuItem key={city.id} value={city.id}>{city.name}</MenuItem>)}
        </Select>}
    </div>
}

const CityDetailWindow = ({ gameState, myCivTemplate, myCiv, myTerritoryCapitals, declinePreviewMode, puppet, playerNum, playerApiUrl, setGameState, refreshSelectedCity,
    selectedCityBuildingChoices, selectedCityBuildingQueue, 
    selectedCityUnitChoices, selectedCity,
    unitTemplatesByBuildingName, templates, descriptions,
    setHoveredUnit, setHoveredBuilding, setHoveredWonder, setSelectedCity, centerMap
     }) => {

    const canBuild = !declinePreviewMode && !puppet;
    const [isBuildingListExpanded, setIsBuildingListExpanded] = useState(declinePreviewMode);
    const [showHiddenBuildings, setShowHiddenBuildings] = useState(false);

    const handleClickClose = () => {
        setSelectedCity(null);
    }

    const submitPlayerInput = (moveType, playerInput) => {
        const data = {
            player_num: playerNum,
            turn_num: gameState.turn_num,
            player_input: playerInput,
        }
        playerInput['move_type'] = moveType;
        playerInput['city_id'] = selectedCity.id;

        fetch(playerApiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
        }).then(response => response.json())
            .then(data => {
                if (data.game_state) {
                    setGameState(data.game_state);
                    refreshSelectedCity(data.game_state);
                }
            });
    }

    const handleClickBuildingChoice = (buildingName) => {
        if (!canBuild) return;
        setHoveredBuilding(null);
        submitPlayerInput('choose_building', {'building_name': (buildingName),});
    }

    const handleCancelBuilding = (buildingName) => {
        if (!canBuild) return;
        setHoveredBuilding(null);
        submitPlayerInput('cancel_building', {'building_name': (buildingName),});
    }

    const handleSetInfiniteQueue = (unitName) => {
        if (!canBuild) return;
        submitPlayerInput('select_infinite_queue', {'unit_name': (unitName),});
    }

    const handleMakeTerritory = (otherCityId) => {
        if (declinePreviewMode) return;
        submitPlayerInput('make_territory', {'other_city_id': otherCityId});
    }

    const handleClickFocus = (focus, doubleClick) => {
        if (declinePreviewMode) return;
        submitPlayerInput('choose_focus', {'focus': focus, 'with_puppets': doubleClick});
    }

    const handleClickTradeHub = () => {
        if (declinePreviewMode) return;
        submitPlayerInput('trade_hub', {});
    }

    const handleHideBuilding = (buildingName, newHidden) => {
        if (!canBuild) return;
        console.log('discarding building', buildingName);
        submitPlayerInput('hide_building', {'building_name': buildingName, 'hidden': newHidden});
    }

    const CycleCities = (direction) => {
        let newCity;
        if (puppet) {
            newCity = gameState.cities_by_id[selectedCity.territory_parent_id];
        } else {
            const cycleCities = declinePreviewMode ? Object.values(gameState?.cities_by_id || {}).filter(city => city.is_decline_view_option) : myTerritoryCapitals;
            const cityIndex = cycleCities.findIndex(city => city.id === selectedCity.id);
            const newIndex = (cityIndex + (direction ? 1 : -1) + cycleCities.length) % cycleCities.length;
            newCity = cycleCities[newIndex];
        }
        if (newCity) {
            setSelectedCity(newCity);
            centerMap(newCity.hex);
        } else {
            console.log("Error, no city found!")
        }
    }

    // A bit silly that we calculate the amount available of each resource here
    // And then recalculate each one in the CityDetailPanel.
    const projectedIncome = selectedCity.projected_income || {
        food: 0,
        wood: 0,
        metal: 0,
        science: 0
    };

    if (!selectedCity || !projectedIncome) {
        return null;
    }

    const foodProgressStored = selectedCity.food / selectedCity.growth_cost;
    const foodProgressProduced = projectedIncome['food'] / selectedCity.growth_cost;
    const foodProgressStoredDisplay = Math.min(100, Math.floor(foodProgressStored * 100));
    const foodProgressProducedDisplay = Math.floor(Math.min(100, (foodProgressStored + foodProgressProduced) * 100) - foodProgressStoredDisplay);

    const foodDemanded = selectedCity.food_demand;
    const incomeExceedsDemand = projectedIncome['food'] >= foodDemanded;
    const happinessIcon = (incomeExceedsDemand && selectedCity.unhappiness === 0) ? happyImg : (!incomeExceedsDemand && selectedCity.unhappiness === 0) ? neutralImg : sadImg;
    const unhappinessBarsMaxWidth = 180;
    const unhappinessBarsWidthPerUnit = Math.min(10, unhappinessBarsMaxWidth/foodDemanded, unhappinessBarsMaxWidth/projectedIncome['food']);
    const numPuppets = Object.keys(selectedCity?.projected_income_puppets?.["wood"] || {}).length;
    const foodDemandTooltip = <><p>Food Demand {foodDemanded}:</p> <ul> 
        <li>{(gameState.turn_num - selectedCity.founded_turn)} from age (1/turn since founding turn {selectedCity.founded_turn})</li> 
        {selectedCity.capital ? <li>Capital's age food demand reduced by 75%</li> : ""}
        {selectedCity.territory_parent_coords ? <li>+2 in puppet city</li> : ""}
        {numPuppets > 0 ? <li>-{2 * numPuppets} from puppets (-2/puppet) </li> : ""}
        </ul> </>

    const metalAvailable = selectedCity.metal + projectedIncome['metal'];
    const woodAvailable = selectedCity.wood + projectedIncome['wood'];

    const unitQueueNumber = selectedCity.infinite_queue_unit ? Math.floor(metalAvailable / templates.UNITS[selectedCity.infinite_queue_unit].metal_cost) : 0;
    const bldgQueueMaxIndexFinishing = queueBuildDepth(woodAvailable, selectedCityBuildingQueue, (item) => templates.BUILDINGS[item] ? templates.BUILDINGS[item].cost : templates.WONDERS[item] ? gameState.wonder_cost_by_age[templates.WONDERS[item].age] : unitTemplatesByBuildingName[item] ? unitTemplatesByBuildingName[item].wood_cost : 0);

    return (
        <div className="city-detail-window" 
            style={{borderColor: myCivTemplate?.secondary_color}}>
            <div className="city-detail-header" style={{backgroundColor: `${myCivTemplate?.primary_color}e0`}}>
                <h1 style={{ margin: '0', display: 'flex', alignItems: 'center' }}>
                    <TextOnIcon image={workerImg}>{selectedCity.population}</TextOnIcon>
                </h1>
                <h1 style={{ margin: '0', display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '60%' }}>
                    <span 
                        role="img" 
                        aria-label="Previous City" 
                        className="city-navigation-icon" 
                        onClick={() => CycleCities(false)}
                    >
                        {puppet ? "⇧" : "◀"}
                    </span>
                    <span style={{ textAlign: 'center' }}>
                    {selectedCity.name}
                    {declinePreviewMode ? " (preview)" : ""}
                    </span>
                    <span 
                        role="img" 
                        aria-label="Previous City" 
                        className="city-navigation-icon" 
                        onClick={() => CycleCities(true)}
                    >
                    {puppet ? "⇧" : "▶"}
                    </span>
                </h1>
                <button className="city-detail-close-button" onClick={handleClickClose}>X</button>
            </div>
            <div className="city-detail-columns">
            <div className="city-detail-column">
                {puppet && 
                    <MakeTerritory myCiv={myCiv} myTerritoryCapitals={myTerritoryCapitals} handleMakeTerritory={handleMakeTerritory}/>                    
                }
                <CityDetailPanel title="wood" icon={woodImg} hideStored={!canBuild} selectedCity={selectedCity} total_tooltip="available to spend this turn." handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                    {selectedCityBuildingChoices && canBuild && (<>
                        <div className="building-choices-container">
                            <div className='building-choices-row'>
                                <img src={showHiddenBuildings ? eyeImg : closedEyeImg} alt="" className={selectedCity.hidden_building_names.length > 0 ? "clickable" : ""} height="20px" onClick={() => setShowHiddenBuildings(!showHiddenBuildings)} style={{
                                    border: '2px solid black',
                                    borderRadius: '50%',
                                    opacity: selectedCity.hidden_building_names.length > 0 ? 1.0 : 0.25,
                                }}/>
                                <BriefBuildingDisplayTitle title="Building Choices" />
                            </div>
                            {selectedCityBuildingChoices.map((buildingName, index) => {
                                const hidden = selectedCity.hidden_building_names.includes(buildingName)
                                if (!showHiddenBuildings && hidden) {
                                    return null;
                                }
                                const inOtherQueue = myCiv.buildings_in_all_queues.includes(buildingName);
                                return <div key={index} className={`building-choices-row ${hidden ? 'hidden' : ''}`}>
                                    <img src={hidden ? closedEyeImg : eyeImg} alt="" height="20px" className="clickable" onClick={() => handleHideBuilding(buildingName, !hidden)} style={{
                                        border: '2px solid black',
                                        borderRadius: '50%',
                                    }}/>
                                    <BriefBuildingDisplay 
                                        buildingName={buildingName}
                                        faded={inOtherQueue}
                                        wonderCostsByAge={gameState.wonder_cost_by_age}
                                        clickable={true}
                                        unitTemplatesByBuildingName={unitTemplatesByBuildingName} templates={templates}
                                        setHoveredBuilding={setHoveredBuilding} setHoveredWonder={setHoveredWonder}
                                        onClick={() => handleClickBuildingChoice(buildingName)}
                                        descriptions={descriptions} />
                                </div>
                            })}
                        </div>
                        <div className="building-choices-placeholder"/>

                    </>)}
                    {selectedCityBuildingQueue && canBuild &&  (
                        <div className="building-queue-container">
                            <BriefBuildingDisplayTitle title="Building Queue" />
                            {selectedCityBuildingQueue.map((buildingName, index) => (
                                <div key={index} className={index > bldgQueueMaxIndexFinishing ? "queue-not-building" : "queue-building"} >
                                    <BriefBuildingDisplay buildingName={buildingName} clickable={true} wonderCostsByAge={gameState.wonder_cost_by_age} unitTemplatesByBuildingName={unitTemplatesByBuildingName} templates={templates} setHoveredBuilding={setHoveredBuilding} setHoveredWonder={setHoveredWonder} onClick={() => handleCancelBuilding(buildingName)} descriptions={descriptions}/>
                                </div>
                            ))}
                        </div>
                    )}               
                    {selectedCity?.buildings && (
                        <div>
                            {canBuild ? <button 
                                className="collapse-expand-button" 
                                onClick={() => setIsBuildingListExpanded(!isBuildingListExpanded)} 
                            >
                                <BriefBuildingDisplayTitle title={`${isBuildingListExpanded ? '▼' : '▶'} Existing buildings`} />
                            </button> 
                            : 
                                <BriefBuildingDisplayTitle title="Existing buildings" />
                            }

                            {(isBuildingListExpanded || !canBuild) && (
                                <div className="existing-buildings-container">
                                    {selectedCity?.buildings.map((building, index) => (
                                        (!unitTemplatesByBuildingName[building.building_name] && !building.ruined && 
                                        <BriefBuildingDisplay key={index} buildingName={building.building_name} buildingObj={building} clickable={false} hideCost={true} unitTemplatesByBuildingName={unitTemplatesByBuildingName} templates={templates} setHoveredBuilding={setHoveredBuilding} setHoveredWonder={setHoveredWonder} descriptions={descriptions}/>)
                                    ))}
                                </div>
                            )}
                        </div>
                    )}
                </CityDetailPanel>
            </div>
            <div className="city-detail-column">
                <CityDetailPanel title='food' icon={foodImg} selectedCity={selectedCity} hideStored='true' total_tooltip="produced this turn.z" handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                    <div className='growth-area'>
                        <TextOnIcon image={workerImg}>
                            +
                        </TextOnIcon>
                        <ProgressBar darkPercent={foodProgressStoredDisplay} lightPercent={foodProgressProducedDisplay} barText={`${Math.floor(selectedCity.food)} + ${Math.floor(projectedIncome['food'])} / ${selectedCity.growth_cost}`}/>
                    </div>
                    <div className="food-divider-line"/>
                    {!declinePreviewMode && <div className="unhappiness-area">
                        <div className="unhappiness-area-top-row">
                            <div className="unhappiness-current">
                                <img src={happinessIcon} alt="" height="30px"/>
                                <WithTooltip tooltip={`${selectedCity.unhappiness.toFixed(2)} unhappiness`}><>
                                <span className="unhappiness-value">{Math.ceil(selectedCity.unhappiness)}</span>
                                </></WithTooltip>
                                <div style={{visibility: selectedCity.civ_to_revolt_into ? "visible" : "hidden"}}>
                                <WithTooltip tooltip="This city is a revolt option for other players!">
                                    <img src={declineImg} alt="" height="30px"/>
                                </WithTooltip>
                                </div>
                            </div>
                            <WithTooltip tooltip={selectedCity.is_trade_hub ? 
                                `Trade hub consumes 20 city power to remove 10 unhappiness per turn (if above 10). Click to cancel.` : 
                                `Make this city your trade hub (20 city power -> 10 unhappiness)`}>
                            <div className="trade-hub"
                                onClick = {handleClickTradeHub}>
                                    <img 
                                    src={tradeHubImg}
                                    alt=""
                                    className={selectedCity.is_trade_hub ? "active" : "not-active"}
                                    />
                            </div>
                            </WithTooltip>
                        </div>
                        <div className="unhappiness-income-area">
                            <WithTooltip tooltip={projectedIncome['food'] >= foodDemanded ? 
                                `income exceeds demand; city produces city power ${projectedIncome['city_power'].toFixed(2)}` : 
                                `demand exceds income; city is gaining unhappiness ${projectedIncome['unhappiness'].toFixed(2)}`}
                            >
                                <div className="unhappiness-income-value">
                                    +{projectedIncome['city_power'] > 0 ? Math.floor(projectedIncome['city_power']) : Math.floor(projectedIncome['unhappiness'])}
                                    <img src={projectedIncome['city_power'] > 0 ? cityImg : sadImg}  alt="" height="30px"/>
                                </div>
                            </WithTooltip>
                            <WithTooltip tooltip={foodDemandTooltip}>
                            <table className="unhappiness-bars"><tbody>
                                <tr>
                                    <td className="label">
                                        {Math.floor(projectedIncome['food'])}
                                    </td>
                                    <td>
                                        <div className="bar income" style={{width: `${Math.floor(projectedIncome['food'] * unhappinessBarsWidthPerUnit)}px`}}>
                                            {Array.from({ length: Math.floor(projectedIncome['food'])}).map((_, idx) => (
                                                <div key={idx} className='bar-tick' style={{marginLeft: `${unhappinessBarsWidthPerUnit - 0.5}px`, marginRight: "-0.5px"}}></div>  // The -0.5 is the width of the tick
                                            ))}
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td className="label">
                                        {foodDemanded}
                                    </td>
                                    <td>
                                        <div className="bar demand" style={{width: `${Math.floor(foodDemanded * unhappinessBarsWidthPerUnit)}px`}}>
                                            {Array.from({ length: Math.floor(foodDemanded) }).map((_, idx) => (
                                                <div key={idx} className='bar-tick' style={{marginLeft: `${unhappinessBarsWidthPerUnit - 0.5}px`}}></div>  // The -0.5 is the width of the tick
                                            ))}
                                        </div>
                                    </td>
                                </tr>
                            </tbody></table>
                            </WithTooltip>
                        </div>
                    </div>}
                </CityDetailPanel>
                <CityDetailPanel title='science' icon={scienceImg} selectedCity={selectedCity} hideStored='true' total_tooltip="produced by this city." handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                </CityDetailPanel>
                <CityDetailPanel title="metal" icon={metalImg} hideStored={!canBuild} selectedCity={selectedCity} total_tooltip="available to spend this turn." handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                    {selectedCityUnitChoices && (
                        <div className="unit-choices-container">
                            {selectedCityUnitChoices.map((unitName, index) => (
                                <UnitQueueOption key={index} unitName={unitName} canBuild={canBuild}
                                    isCurrentIQUnit={canBuild && selectedCity.infinite_queue_unit === unitName} 
                                    templates={templates} setHoveredUnit={setHoveredUnit} handleSetInfiniteQueue={handleSetInfiniteQueue}/>
                            ))}
                        {Array.from({ length: 3 - selectedCityUnitChoices.length }).map((_, index) => (
                            <UnitQueueOption key={`empty-${index}`} unitName={null} canBuild={false} isCurrentIQUnit={false}/>
                        ))}
                        </div>
                    )}
                    {canBuild && <div>
                        <h2> Producing This Turn </h2>
                        <div className="unit-queue-container">
                            {Array.from({ length: unitQueueNumber }).map((_, index) => (
                                <div key={index} >
                                    <IconUnitDisplay unitName={selectedCity.infinite_queue_unit} templates={templates} setHoveredUnit={setHoveredUnit}/>
                                </div>
                            ))}
                        </div>
                    </div>}
                </CityDetailPanel>
            </div>
            </div>
        </div>
    );
};

export default CityDetailWindow;