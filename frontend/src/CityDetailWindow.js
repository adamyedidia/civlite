import React, { useState } from 'react';
import './CityDetailWindow.css';

import { Button, Select, MenuItem } from '@mui/material';

import { BriefBuildingDisplay, BriefBuildingDisplayTitle, ExistingBuildingDisplay, ExistingMilitaryBuildingDisplay, ExpandButton } from './BuildingDisplay';
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

const MakeTerritory = ({territoryReplacementCity, handleMakeTerritory, myCiv}) => {
    if (myCiv === null) {return}
    const submitClickIfValid = () => {
        if (territoryReplacementCity == null) {
            handleMakeTerritory(null);
        } else {
            handleMakeTerritory(territoryReplacementCity.id);
        }
    }

    return <div className='make-territory-area'>
        <WithTooltip tooltip={`Make this city a territory instead of a puppet. ${territoryReplacementCity ? `Will replace ${territoryReplacementCity.name} and bring its stores of wood & metal here.` : ""}`}>
        <Button
            variant="contained"
            style = {{
                width: '250px',
                margin: '10px',
                padding: '20px 50px',
            }}
            onClick={submitClickIfValid}
        >
            <span>Make Territory
            {territoryReplacementCity && ` instead of ${territoryReplacementCity.name}`}</span>
        </Button>
        </WithTooltip>
    </div>
}

const CityDetailWindow = ({ gameState, myCivTemplate, myCiv, myTerritoryCapitals, declinePreviewMode, puppet, playerNum, playerApiUrl, setGameState, refreshSelectedCity,
    selectedCity,
    unitTemplatesByBuildingName, templates, descriptions,
    setHoveredUnit, setHoveredBuilding, setHoveredWonder, setSelectedCity, centerMap
     }) => {

    const canBuild = !declinePreviewMode && !puppet;

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

    const handleClickDevelop = (type) => {
        if (declinePreviewMode) return;
        submitPlayerInput('develop', {'type': type});
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

    const roomForNewTerritory = myCiv && (myCiv.id == selectedCity.civ_id) && myTerritoryCapitals.length < myCiv.max_territories;
    const territoryReplacementCity = !roomForNewTerritory ? 
        myTerritoryCapitals.reduce((minCity, city) => city.population < minCity.population ? city : minCity, myTerritoryCapitals[0])
    : null;

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
        {numPuppets > 0 ? <li>-{2 * numPuppets} from puppets (-2/puppet) </li> : ""}
        </ul> </>

    const bldgQueueMaxIndexFinishing = selectedCity.projected_build_queue_depth - 1;
    const availableBuildingEntry = (buildingName, index) => {
        const inOtherQueue = myCiv.buildings_in_all_queues.includes(buildingName);
        return <div key={index} className='building-choices-row'>
            <BriefBuildingDisplay 
                buildingName={buildingName}
                faded={inOtherQueue}
                wonderCostsByAge={gameState.wonder_cost_by_age}
                clickable={true}
                unitTemplatesByBuildingName={unitTemplatesByBuildingName} templates={templates}
                setHoveredBuilding={setHoveredBuilding} setHoveredWonder={setHoveredWonder} setHoveredUnit={setHoveredUnit}
                onClick={() => handleClickBuildingChoice(buildingName)}
                descriptions={descriptions}
                yields = {selectedCity.building_yields?.[buildingName]} 
                payoffTime = {selectedCity.available_buildings_payoff_times?.[buildingName]}
                />
        </div>
    }

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
            {puppet && (territoryReplacementCity === null || selectedCity.population > territoryReplacementCity.population) &&
                <MakeTerritory myCiv={myCiv} territoryReplacementCity={territoryReplacementCity} handleMakeTerritory={handleMakeTerritory}/>                    
            }
            <div className="existing-buildings-container">
            {selectedCity?.unit_buildings.slice().reverse().map((building, index) => (
                    <ExistingMilitaryBuildingDisplay key={index} 
                    unitBuilding={building}
                    handleSetInfiniteQueue={canBuild && handleSetInfiniteQueue}
                    templates={templates} setHoveredUnit={setHoveredUnit} 
                    slotsFull={selectedCity.building_slots_full.military}
                    />
                ))}
                {Array.from({ length: selectedCity?.military_slots - selectedCity?.unit_buildings.length }).map((_, index) => (
                    <ExistingMilitaryBuildingDisplay key={`empty-${index}`} unitName={null} templates={templates} setHoveredUnit={setHoveredUnit}/>
                ))}
                {selectedCity?.buildings.map((building, index) => (
                    building.type=="rural" &&
                    <ExistingBuildingDisplay key={index} buildingName={building.building_name} 
                    templates={templates} setHoveredBuilding={setHoveredBuilding} 
                    yields={selectedCity.building_yields} 
                    slotsFull={selectedCity.building_slots_full.rural}/>
                ))}
                {Array.from({ length: selectedCity?.rural_slots - selectedCity?.buildings.filter(building => building.type=="rural").length }).map((_, index) => (
                    <ExistingBuildingDisplay key={`empty-${index}`} buildingName={null} templates={templates} setHoveredBuilding={setHoveredBuilding} 
                        emptyType="rural"
                        militarizeBtn={selectedCity?.can_militarize && index === 0}
                        urbanizeBtn={selectedCity?.can_urbanize && index === 0}
                        canAffordDevelop={myCiv?.city_power > 100}
                        handleClickDevelop={handleClickDevelop}
                    />
                ))}
                {selectedCity?.buildings.map((building, index) => (
                    building.type=="urban" &&
                    <ExistingBuildingDisplay key={index} buildingName={building.building_name} 
                    templates={templates} setHoveredBuilding={setHoveredBuilding} 
                    yields={selectedCity.building_yields} 
                    slotsFull={selectedCity.building_slots_full.urban}/>
                ))}
                {Array.from({ length: selectedCity?.urban_slots - selectedCity?.buildings.filter(building => building.type=="urban").length }).map((_, index) => (
                    <ExistingBuildingDisplay key={`empty-${index}`} buildingName={null} templates={templates} setHoveredBuilding={setHoveredBuilding} emptyType="urban"/>
                ))}
                {selectedCity.can_expand && 
                    <ExpandButton expandSufficientPower={myCiv.city_power > 25} handleClickDevelop={handleClickDevelop}/>
                }
            </div>
            <div className="wonders-container">
                {selectedCity?.buildings.map((building, index) => (
                    building.type=="wonder" &&
                    <BriefBuildingDisplay key={index} buildingName={building.building_name} faded={building.ruined} clickable={false} hideCost={true} templates={templates} setHoveredBuilding={setHoveredBuilding} setHoveredWonder={setHoveredWonder}/>
                ))}
            </div>
            <div className="city-detail-columns">
            <div className="city-detail-column">
                <CityDetailPanel title="metal" icon={metalImg} hideStored={!canBuild} selectedCity={selectedCity} total_tooltip="available to spend this turn." handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                </CityDetailPanel>
                <CityDetailPanel title="wood" icon={woodImg} hideStored={!canBuild} selectedCity={selectedCity} total_tooltip="available to spend this turn." handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                    {selectedCity && canBuild &&  (
                        <div className="building-queue-container">
                            <BriefBuildingDisplayTitle title="Building Queue" />
                            {selectedCity.buildings_queue.map((entry, index) => {
                                return <div key={index} className={index > bldgQueueMaxIndexFinishing ? "queue-not-building" : "queue-building"} >
                                    <BriefBuildingDisplay 
                                        buildingName={entry.template_name} 
                                        clickable={true} 
                                        wonderCostsByAge={gameState.wonder_cost_by_age} unitTemplatesByBuildingName={unitTemplatesByBuildingName} templates={templates} 
                                        setHoveredBuilding={setHoveredBuilding} setHoveredWonder={setHoveredWonder} setHoveredUnit={setHoveredUnit}
                                        onClick={() => handleCancelBuilding(entry.template_name)} 
                                        descriptions={descriptions} yields={selectedCity.building_yields?.[entry.template_name]} payoffTime = {selectedCity.available_buildings_payoff_times?.[entry.template_name]}/>
                                </div>
                            })}
                        </div>
                    )}               
                </CityDetailPanel>
            </div>
            <div className="city-detail-column">
                <CityDetailPanel title='science' icon={scienceImg} selectedCity={selectedCity} hideStored='true' total_tooltip="produced by this city." handleClickFocus={handleClickFocus} noFocus={declinePreviewMode}>
                </CityDetailPanel>
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
            </div>
            </div>
            {selectedCity && canBuild && 
            <div className="available-buildings city-detail-columns">
                <div className="city-detail-column">
                    <div className="building-choices-container">
                        {selectedCity.available_wonders.map(availableBuildingEntry)}
                    </div>
                    <div className="building-choices-container">
                        {selectedCity.available_unit_building_names.map(availableBuildingEntry)}
                        {selectedCity.max_units_in_build_queue && <div className="building-slots-full-banner">
                            <span>Queued Max Units</span>
                        </div>}
                    </div>
                </div>
                <div className="city-detail-column">
                    <div className="building-choices-container">
                        {selectedCity.available_urban_building_names.map(availableBuildingEntry)}
                        {selectedCity.building_slots_full.urban && <div className="building-slots-full-banner">
                            <span>No Urban Slots</span>
                        </div>}
                    </div>
                    <div className="building-choices-container">
                        {selectedCity.available_rural_building_names.map(availableBuildingEntry)}
                        {selectedCity.building_slots_full.rural && <div className="building-slots-full-banner">
                            <span>No Rural Slots</span>
                        </div>}
                    </div>
                </div>
            </div>}
        </div>
    );
};

export default CityDetailWindow;