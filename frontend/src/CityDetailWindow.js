import React, { useState } from 'react';
import './CityDetailWindow.css';

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



import workerImg from './images/worker.png';
import { CityDetailPanel } from './CityDetailPanel.js';
import { TextOnIcon } from './TextOnIcon.js';
import ProgressBar from './ProgressBar.js';
import { WithTooltip } from './WithTooltip.js';

const UnitQueueOption = ({unitName, isCurrentIQUnit, canBuild, templates, setHoveredUnit, handleSetInfiniteQueue}) => {
    return <WithTooltip tooltip={canBuild ? "&#x1F5B1; Toggle infinite queue." : "Cannot build units here."}>
    <div className={`unit-choice ${isCurrentIQUnit ? 'infinite-queue' : ''} ${canBuild ? 'enabled' : 'disabled'}`}
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
        <div style={{"display": "flex", "alignItems": "center", "justifyContent": "center", "fontSize": "16px"}}>
            {templates.UNITS[unitName].metal_cost}
            <img src={metalImg} height="10px"/>
        </div>
    </div>
    </WithTooltip>;
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

const CityDetailWindow = ({ gameState, myCivTemplate, declinePreviewMode, puppet, playerNum, playerApiUrl, setGameState, refreshSelectedCity,
    selectedCityBuildingChoices, selectedCityBuildingQueue, selectedCityBuildings, 
    selectedCityUnitChoices, selectedCity,
    unitTemplatesByBuildingName, templates, descriptions,
    setHoveredUnit, setHoveredBuilding, setSelectedCity
     }) => {

    const canBuild = !declinePreviewMode && !puppet;
    const [isBuildingListExpanded, setIsBuildingListExpanded] = useState(declinePreviewMode);


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

    const handleClickFocus = (focus) => {
        if (declinePreviewMode) return;
        submitPlayerInput('choose_focus', {'focus': focus,});
    }

    const handleClickTradeHub = () => {
        if (declinePreviewMode) return;
        submitPlayerInput('trade_hub', {});
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
    const happinessIcon = (incomeExceedsDemand && selectedCity.unhappiness == 0) ? happyImg : (!incomeExceedsDemand && selectedCity.unhappiness == 0) ? neutralImg : sadImg;
    const unhappinessBarsMaxWidth = 180;
    const unhappinessBarsWidthPerUnit = Math.min(10, unhappinessBarsMaxWidth/foodDemanded, unhappinessBarsMaxWidth/projectedIncome['food']);
    
    const metalAvailable = selectedCity.metal + projectedIncome['metal'];
    const woodAvailable = selectedCity.wood + projectedIncome['wood'];

    const unitQueueNumber = selectedCity.infinite_queue_unit ? Math.floor(metalAvailable / templates.UNITS[selectedCity.infinite_queue_unit].metal_cost) : 0;
    const bldgQueueMaxIndexFinishing = queueBuildDepth(woodAvailable, selectedCityBuildingQueue, (item) => templates.BUILDINGS[item] ? templates.BUILDINGS[item].cost : unitTemplatesByBuildingName[item].wood_cost);

    return (
        <div className="city-detail-window" 
            style={{borderColor: myCivTemplate?.secondary_color}}>
            <div className="city-detail-header" style={{backgroundColor: `${myCivTemplate?.primary_color}e0`}}>
                <h1 style={{ margin: '0', display: 'flex', alignItems: 'center' }}>
                    <TextOnIcon image={workerImg}>{selectedCity.population}</TextOnIcon>
                </h1>
                <h1 style={{ margin: '0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    {selectedCity.name}
                    {declinePreviewMode ? " (preview)" : ""}
                </h1>
                <button className="city-detail-close-button" onClick={handleClickClose}>X</button>
            </div>
            <div className="city-detail-columns">
            <div className="city-detail-column">
                <CityDetailPanel title="wood" icon={woodImg} selectedCity={selectedCity} total_tooltip="available to spend this turn." handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                    {selectedCityBuildingChoices && canBuild && (<>
                        <div className="building-choices-container">
                            <BriefBuildingDisplayTitle title="Building Choices" />
                            {selectedCityBuildingChoices.map((buildingName, index) => (
                                <BriefBuildingDisplay key={index} buildingName={buildingName} clickable={true}unitTemplatesByBuildingName={unitTemplatesByBuildingName} templates={templates} setHoveredBuilding={setHoveredBuilding} onClick={() => handleClickBuildingChoice(buildingName)} descriptions={descriptions} />
                            ))}
                        </div>
                        <div className="building-choices-placeholder"/>
                    </>)}
                    {selectedCityBuildingQueue && canBuild &&  (
                        <div className="building-queue-container">
                            <BriefBuildingDisplayTitle title="Building Queue" />
                            {selectedCityBuildingQueue.map((buildingName, index) => (
                                <div key={index} className={index > bldgQueueMaxIndexFinishing ? "queue-not-building" : "queue-building"} >
                                    <BriefBuildingDisplay buildingName={buildingName} clickable={true} unitTemplatesByBuildingName={unitTemplatesByBuildingName} templates={templates} setHoveredBuilding={setHoveredBuilding} onClick={() => handleCancelBuilding(buildingName)} descriptions={descriptions}/>
                                </div>
                            ))}
                        </div>
                    )}               
                    {selectedCityBuildings && (
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
                                    {selectedCityBuildings.map((buildingName, index) => (
                                        <BriefBuildingDisplay key={index} buildingName={buildingName} clickable={false} unitTemplatesByBuildingName={unitTemplatesByBuildingName} templates={templates} setHoveredBuilding={setHoveredBuilding} descriptions={descriptions}/>
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
                                <img src={happinessIcon} height="30px"/>
                                <WithTooltip tooltip={`${selectedCity.unhappiness.toFixed(2)} unhappiness`}><>
                                <span className="unhappiness-value">{Math.ceil(selectedCity.unhappiness)}</span>
                                </></WithTooltip>
                                <div style={{visibility: selectedCity.civ_to_revolt_into ? "visible" : "hidden"}}>
                                <WithTooltip tooltip="This city is a revolt option for other players!">
                                    <img src={declineImg} height="30px"/>
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
                                    className={selectedCity.is_trade_hub ? "active" : "not-active"}
                                    />
                            </div>
                            </WithTooltip>
                        </div>
                        <div className="unhappiness-income-area">
                            <WithTooltip tooltip={projectedIncome['food'] >= foodDemanded ? 
                                `income exceeds demand; city produces city power ${projectedIncome['city-power'].toFixed(2)}` : 
                                `demand exceds income; city is gaining unhappiness ${projectedIncome['unhappiness'].toFixed(2)}`}
                            >
                                <div className="unhappiness-income-value">
                                    +{projectedIncome['city-power'] > 0 ? Math.floor(projectedIncome['city-power']) : Math.floor(projectedIncome['unhappiness'])}
                                    <img src={projectedIncome['city-power'] > 0 ? cityImg : sadImg} height="30px"/>
                                </div>
                            </WithTooltip>
                            <WithTooltip tooltip={`${selectedCity.capital ? "Capital city citizens expect 1 food per 2 population." : "Citizens expect 2 food per population."} ${selectedCity.name}'s income is ${projectedIncome['food'].toFixed(2)}.`}>
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
                <CityDetailPanel title="metal" icon={metalImg} selectedCity={selectedCity} total_tooltip="available to spend this turn." handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                    {selectedCityUnitChoices && (
                        <div className="unit-choices-container">
                            {selectedCityUnitChoices.map((unitName, index) => (
                                <UnitQueueOption key={index} unitName={unitName} canBuild={canBuild}
                                    isCurrentIQUnit={canBuild && selectedCity.infinite_queue_unit === unitName} 
                                    templates={templates} setHoveredUnit={setHoveredUnit} handleSetInfiniteQueue={handleSetInfiniteQueue}/>
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