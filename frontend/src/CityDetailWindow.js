import React from 'react';
import './CityDetailWindow.css';

import { BriefBuildingDisplay, BriefBuildingDisplayTitle } from './BuildingDisplay';
import {BriefUnitDisplay, BriefUnitDisplayTitle} from './UnitDisplay';
import foodImg from './images/food.png';
import woodImg from './images/wood.png';
import metalImg from './images/metal.png';
import scienceImg from './images/science.png';

import crateImg from './images/crate.png';
import hexesImg from './images/hexes.png';
import workerImg from './images/worker.png';

const roundValue = (value) => {
    return value < 10 ? value.toFixed(1) : Math.round(value);
};


const TextOnIcon = ({ image, style, children, tooltip }) => {
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

    const containerStyle = {
        position: 'relative',
        backgroundImage: image ? `url(${image})` : "",
        ...style
    };

    return (
        <div className="icon-bg-text" style={containerStyle} 
            onMouseOver={showTooltip} onMouseOut={hideTooltip}>
            <span style={{ textAlign: 'center' }}>{children}</span>
            {tooltip && (
                <div ref={tooltipRef} className="tooltip"
                >
                    {tooltip}
                </div>
            )}
        </div>
    );
}

const FocusSelectionOption = ({ focus, onClick, isSelected }) => {
    return (
        <div
            className={`focus-selection-option ${focus} ${isSelected ? 'selected' : ''}`}
            onClick={onClick}
        >
            <TextOnIcon image={workerImg}>
                {/* TODO(dfarhi) Get the amount contributed by focus*/}
            </TextOnIcon>
        </div>
    );
}

const CityDetailPanel = ({ title, icon, hideStored, selectedCity, handleClickFocus, children }) => {
    
    const storedAmount = selectedCity[title]
    const projected_income = selectedCity[`projected_${title}_income`]
    const projected_total = title == 'science' ? projected_income : storedAmount + projected_income
    const projected_total_rounded = Math.floor(projected_total) 
    let projected_total_display;
    switch (title) {
        case 'science':
            projected_total_display = `+${projected_total_rounded}`;
            break;
        // If we need custom display for any others, can add it here.
        default:
            projected_total_display = projected_total_rounded.toString();
            break;
    }
    const projected_total_rounded_2 = Math.floor(projected_total * 100) / 100;
    let totalAmountTooltip;
    switch (title) {
        case 'science':
            totalAmountTooltip = `${projected_total_rounded_2} ${title} produced by this city.`
        case 'food':
            totalAmountTooltip = `${projected_total_rounded_2} ${title} after this turn.`
        default:
            totalAmountTooltip = `${projected_total_rounded_2} ${title} available to spend this turn.`
    }

    const storedStyle = hideStored ? { visibility: 'hidden' } : {};

    return (
        <div className={`city-detail-panel ${title}-area`}>
            <div className="panel-header">    
                <div className="panel-icon">
                    <img src={icon}/>
                </div>
                <div className="amount-total">
                    <TextOnIcon tooltip={totalAmountTooltip}>{projected_total_display}</TextOnIcon>
                </div>
                
                <div className="panel-banner">
                    =
                    <TextOnIcon image={crateImg} style={storedStyle} tooltip={hideStored ? null : `${storedAmount.toFixed(2)} ${title} stored from last turn.`}> {roundValue(storedAmount)} </TextOnIcon>
                    <div>+</div>
                    <TextOnIcon image={hexesImg} tooltip={`${projected_income.toFixed(2)} ${title} produced this turn.`}> {roundValue(projected_income)} </TextOnIcon>
                    <FocusSelectionOption focus={title} isSelected={selectedCity?.focus === title} onClick={() => handleClickFocus(title)} />
                </div>
            </div>
            <div className="panel-content">
                {children}
            </div>
        </div>
    );
}

const CityDetailWindow = ({ gameState, myCivTemplate, playerNum, playerApiUrl, setGameState, refreshSelectedCity,
    selectedCityBuildingChoices, selectedCityBuildingQueue, selectedCityBuildings, 
    selectedCityUnitChoices, selectedCityUnitQueue, selectedCity,
    unitTemplatesByBuildingName, buildingTemplates, unitTemplates, descriptions,
    setHoveredUnit, setHoveredBuilding, setSelectedCity
     }) => {

    const handleClickClose = () => {
        setSelectedCity(null);
    }

    const handleClickBuildingChoice = (buildingName) => {
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

    const handleClickUnitChoice = (unitName) => {
        const playerInput = {
            'unit_name': (unitName),
            'move_type': 'choose_unit',
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

    const handleCancelUnit = (unitIndex) => {
        const playerInput = {
            'unit_index_in_queue': unitIndex,
            'move_type': 'cancel_unit',
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

    const foodProgressStored = selectedCity.food / selectedCity.growth_cost;
    const foodProgressProduced = selectedCity.projected_food_income / selectedCity.growth_cost;
    const foodProgressStoredDisplay = Math.min(100, Math.floor(foodProgressStored * 100)).toString()
    const foodProgressProducedDisplay = Math.floor(Math.min(100, (foodProgressStored + foodProgressProduced) * 100) - foodProgressStoredDisplay).toString()
    const foodProgressWillGrow = foodProgressStored + foodProgressProduced > 1

    return (
        <div className="city-detail-window" 
            style={{borderColor: myCivTemplate.secondary_color}}>
            <div className="city-detail-header" style={{backgroundColor: `${myCivTemplate.primary_color}e0`}}>
                <h1 style={{ margin: '0', display: 'flex' }}>
                    <TextOnIcon image={workerImg}>{selectedCity.population}</TextOnIcon>
                    {selectedCity.name}
                </h1>
                <button className="city-detail-close-button" onClick={handleClickClose}>X</button>
            </div>
            <div className="city-detail-columns">
            <div className="city-detail-column">
                <CityDetailPanel title="wood" icon={woodImg} selectedCity={selectedCity} handleClickFocus={handleClickFocus}>
                    {selectedCityBuildingChoices && (
                        <div className="building-choices-container">
                            <BriefBuildingDisplayTitle title="Building Choices" />
                            {selectedCityBuildingChoices.map((buildingName, index) => (
                                <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} onClick={() => handleClickBuildingChoice(buildingName)} descriptions={descriptions} />
                            ))}
                        </div>
                    )}
                    {selectedCityBuildingQueue && (
                        <div className="building-queue-container">
                            <BriefBuildingDisplayTitle title="Building Queue" />
                            {selectedCityBuildingQueue.map((buildingName, index) => (
                                <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} onClick={() => handleCancelBuilding(buildingName)} descriptions={descriptions}/>
                            ))}
                        </div>
                    )}               
                    {selectedCityBuildings && (
                        <div className="existing-buildings-container">
                            <BriefBuildingDisplayTitle title="Existing buildings" />
                            {selectedCityBuildings.map((buildingName, index) => (
                                <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} descriptions={descriptions}/>
                            ))}
                        </div>
                    )}
                </CityDetailPanel>
            </div>
            <div className="city-detail-column">
                <CityDetailPanel title='food' icon={foodImg} selectedCity={selectedCity} handleClickFocus={handleClickFocus}>
                    <div className="food-progress-bar">
                        <div className="bar stored" style={{ width: `${foodProgressStoredDisplay}%`, }}></div>
                        <div className="bar produced" style={{ width: `${foodProgressProducedDisplay}%`}}></div>
                    <div className="food-progress-text" style={{ position: 'absolute', width: '100%', textAlign: 'center', color: 'black', fontWeight: 'bold' }}>
                        {Math.floor(selectedCity.food + selectedCity.projected_food_income)} / {Math.floor(selectedCity.growth_cost)}
                    </div>
                    {foodProgressWillGrow && (<div className="checkmark">✅</div>)}
                    </div>
                </CityDetailPanel>
                <CityDetailPanel title='science' icon={scienceImg} hideStored='true' selectedCity={selectedCity} handleClickFocus={handleClickFocus}>

                </CityDetailPanel>
                <CityDetailPanel title="metal" icon={metalImg} selectedCity={selectedCity} handleClickFocus={handleClickFocus}>
                    {selectedCityUnitChoices && (
                        <div className="unit-choices-container">
                            <BriefUnitDisplayTitle title="Unit Choices" />
                            {selectedCityUnitChoices.map((unitName, index) => (
                                <BriefUnitDisplay key={index} unitName={unitName} unitTemplates={unitTemplates} setHoveredUnit={setHoveredUnit} onClick={() => handleClickUnitChoice(unitName)} />
                            ))}
                        </div>
                    )}
                    {selectedCityUnitQueue && (
                        <div className="unit-queue-container">
                            <BriefUnitDisplayTitle title="Unit Queue" />
                            {selectedCityUnitQueue.map((unitName, index) => (
                                <BriefUnitDisplay key={index} unitName={unitName} unitTemplates={unitTemplates} setHoveredUnit={setHoveredUnit} onClick={() => handleCancelUnit(index)}/>
                            ))}
                        </div>
                    )}
                </CityDetailPanel>
            </div>
            </div>
        </div>
    );
};

export default CityDetailWindow;