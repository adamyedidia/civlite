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



import workerImg from './images/worker.png';
import { CityDetailPanel } from './CityDetailPanel.js';
import { TextOnIcon } from './TextOnIcon.js';
import ProgressBar from './ProgressBar.js';

const UnitQueueOption = ({unitName, isCurrentIQUnit, unitTemplates, setHoveredUnit, handleSetInfiniteQueue}) => {
    const tooltipRef = React.useRef(null);

    const showTooltip = () => {
        if (tooltipRef.current) {
            tooltipRef.current.style.visibility = 'visible';
            tooltipRef.current.style.opacity = '1';
        }
    };

    const hideTooltip = () => {
        if (tooltipRef.current) {
            tooltipRef.current.style.visibility = 'hidden';
            tooltipRef.current.style.opacity = '0';
        }
    };

    return (<div className={`unit-choice ${isCurrentIQUnit ? 'infinite-queue' : ''}`}
        onMouseOver={showTooltip} onMouseOut={hideTooltip} onClick={(event) => {
            // click to toggle infinite queue
            if (isCurrentIQUnit) {
                handleSetInfiniteQueue("")
            } else {
                handleSetInfiniteQueue(unitName);
            }
        }}>
        <IconUnitDisplay 
            unitName={unitName} 
            unitTemplates={unitTemplates} 
            setHoveredUnit={setHoveredUnit} 
            style={{borderRadius: '25%'}} 
        />
        <div style={{"display": "flex", "alignItems": "center", "justifyContent": "center", "fontSize": "16px"}}>
            {unitTemplates[unitName].metal_cost}
            <img src={metalImg} height="10px"/>
        </div>
        <div ref={tooltipRef} className="tooltip">
            <p>&#x1F5B1; Toggle infinite queue.</p>
        </div>
    </div>
    );
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

const CityDetailWindow = ({ gameState, myCivTemplate, declinePreviewMode, playerNum, playerApiUrl, setGameState, refreshSelectedCity,
    selectedCityBuildingChoices, selectedCityBuildingQueue, selectedCityBuildings, 
    selectedCityUnitChoices, selectedCity,
    unitTemplatesByBuildingName, buildingTemplates, unitTemplates, descriptions,
    setHoveredUnit, setHoveredBuilding, setSelectedCity
     }) => {

    const [isBuildingListExpanded, setIsBuildingListExpanded] = useState(declinePreviewMode);


    const handleClickClose = () => {
        setSelectedCity(null);
    }

    const handleClickBuildingChoice = (buildingName) => {
        if (declinePreviewMode) return;
        const playerInput = {
            'building_name': (buildingName),
            'move_type': 'choose_building',
            'city_id': selectedCity.id,
        }

        const data = {
            player_num: playerNum,
            player_input: playerInput,
        }

        setHoveredBuilding(null);

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

    const handleCancelBuilding = (buildingName) => {
        if (declinePreviewMode) return;
        const playerInput = {
            'building_name': (buildingName),
            'move_type': 'cancel_building',
            'city_id': selectedCity.id,
        }

        const data = {
            player_num: playerNum,
            player_input: playerInput,
        }

        setHoveredBuilding(null);

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

    const handleSetInfiniteQueue = (unitName) => {
        if (declinePreviewMode) return;
        const playerInput = {
            'unit_name': (unitName),
            'move_type': 'select_infinite_queue',
            'city_id': selectedCity.id,
        }

        const data = {
            player_num: playerNum,
            player_input: playerInput,
        }

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

    const handleClickFocus = (focus) => {
        if (declinePreviewMode) return;
        const playerInput = {
            'city_id': selectedCity.id,
            'focus': focus,
            'move_type': 'choose_focus',
        }

        const data = {
            player_num: playerNum,
            player_input: playerInput,
        }
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

    const foodDemanded = 2 * selectedCity.population;  // TODO(keep this in sync with backend)
    const incomeExceedsDemand = projectedIncome['food'] >= foodDemanded;
    const happinessIcon = (incomeExceedsDemand && selectedCity.unhappiness == 0) ? happyImg : (!incomeExceedsDemand && selectedCity.unhappiness == 0) ? neutralImg : sadImg;
    const unhappinessBarsMaxWidth = 180;
    const unhappinessBarsWidthPerUnit = Math.min(10, unhappinessBarsMaxWidth/foodDemanded, unhappinessBarsMaxWidth/projectedIncome['food']);
    
    const metalAvailable = selectedCity.metal + projectedIncome['metal'];
    const woodAvailable = selectedCity.wood + projectedIncome['wood'];

    const unitQueueNumber = selectedCity.infinite_queue_unit ? Math.floor(metalAvailable / unitTemplates[selectedCity.infinite_queue_unit].metal_cost) : 0;
    const bldgQueueMaxIndexFinishing = queueBuildDepth(woodAvailable, selectedCityBuildingQueue, (item) => buildingTemplates[item] ? buildingTemplates[item].cost : unitTemplatesByBuildingName[item].wood_cost);

    return (
        <div className="city-detail-window" 
            style={{borderColor: myCivTemplate.secondary_color}}>
            <div className="city-detail-header" style={{backgroundColor: `${myCivTemplate.primary_color}e0`}}>
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
                    {selectedCityBuildingChoices && !declinePreviewMode && (<>
                        <div className="building-choices-container">
                            <BriefBuildingDisplayTitle title="Building Choices" />
                            {selectedCityBuildingChoices.map((buildingName, index) => (
                                <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} onClick={() => handleClickBuildingChoice(buildingName)} descriptions={descriptions} />
                            ))}
                        </div>
                        <div className="building-choices-placeholder"/>
                    </>)}
                    {selectedCityBuildingQueue && !declinePreviewMode &&  (
                        <div className="building-queue-container">
                            <BriefBuildingDisplayTitle title="Building Queue" />
                            {selectedCityBuildingQueue.map((buildingName, index) => (
                                <div key={index} className={index > bldgQueueMaxIndexFinishing ? "queue-not-building" : "queue-building"} >
                                    <BriefBuildingDisplay buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} onClick={() => handleCancelBuilding(buildingName)} descriptions={descriptions}/>
                                </div>
                            ))}
                        </div>
                    )}               
                    {selectedCityBuildings && (
                        <div>
                            <button 
                                className="collapse-expand-button" 
                                onClick={() => setIsBuildingListExpanded(!isBuildingListExpanded)} 
                            >
                                <BriefBuildingDisplayTitle title={`${isBuildingListExpanded ? '▼' : '▶'} Existing buildings`} />
                            </button>
                            {isBuildingListExpanded && (
                                <div className="existing-buildings-container">
                                    {selectedCityBuildings.map((buildingName, index) => (
                                        <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} descriptions={descriptions}/>
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
                        <div className="unhappiness-current">
                            <img src={happinessIcon} height="30px"/>
                            <span className="unhappiness-value">{selectedCity.unhappiness}</span>
                            <img src={declineImg} height="30px" style={{visibility: selectedCity.civ_to_revolt_into ? "visible" : "hidden"}}/>
                        </div>
                        <div className="unhappiness-income-area">
                            <div className="unhappiness-income-value">
                                +{Math.floor(Math.abs(projectedIncome['food'] - foodDemanded))}
                                <img src={projectedIncome['food'] >= foodDemanded ? cityImg : sadImg} height="30px"/>
                            </div>
                            <table className="unhappiness-bars"><tbody>
                                <tr>
                                    <td>
                                        {Math.floor(projectedIncome['food'])} Income
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
                                <td>
                                        {foodDemanded} Demand
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
                        </div>
                    </div>}
                </CityDetailPanel>
                <CityDetailPanel title='science' icon={scienceImg} selectedCity={selectedCity} hideStored='true' total_tooltip="produced by this city." handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                </CityDetailPanel>
                <CityDetailPanel title="metal" icon={metalImg} selectedCity={selectedCity} total_tooltip="available to spend this turn." handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                    {selectedCityUnitChoices && (
                        <div className="unit-choices-container">
                            {selectedCityUnitChoices.map((unitName, index) => (
                                <UnitQueueOption key={index} unitName={unitName} isCurrentIQUnit={!declinePreviewMode && selectedCity.infinite_queue_unit === unitName} unitTemplates={unitTemplates} setHoveredUnit={setHoveredUnit} handleSetInfiniteQueue={handleSetInfiniteQueue}/>
                            ))}
                        </div>
                    )}
                    {!declinePreviewMode && <div>
                        <h2> Producing This Turn </h2>
                        <div className="unit-queue-container">
                            {Array.from({ length: unitQueueNumber }).map((_, index) => (
                                <div key={index} >
                                    <IconUnitDisplay unitName={selectedCity.infinite_queue_unit} unitTemplates={unitTemplates} setHoveredUnit={setHoveredUnit}/>
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