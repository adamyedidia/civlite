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


const NumberOnImage = ({image, style, children}) => {
    return  <div className="icon-bg-text" style={{ ...style, backgroundImage: `url(${image})`}}>                          
                <span style={{ textAlign: 'center' }}>{children}</span>
            </div>
}

const FocusSelectionOption = ({ focus, onClick, isSelected }) => {
    return (
        <div
            className={`focus-selection-option ${focus} ${isSelected ? 'selected' : ''}`}
            onClick={onClick}
        >
            <NumberOnImage image={workerImg}>
                {/* TODO(dfarhi) Get the amount contributed by focus*/}
            </NumberOnImage>
        </div>
    );
}

const CityDetailPanel = ({ title, icon, hideStored, selectedCity, handleClickFocus, children }) => {
    
    const stored = selectedCity[title]
    const projected_income = selectedCity[`projected_${title}_income`]
    const projected_total = title == 'science' ? projected_income : stored + projected_income
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

    const storedStyle = hideStored ? { visibility: 'hidden' } : {};

    return (
        <div className={`city-detail-panel ${title}-area`}>
            <div className="panel-header">    
                <div className="panel-icon">
                    <img src={icon}/>
                </div>
                <div className="amount-total">
                    {projected_total_display}
                </div>
                
                <div className="panel-banner">
                    =
                    <NumberOnImage image={crateImg} style={storedStyle}> {roundValue(stored)} </NumberOnImage>
                    <div>+</div>
                    <NumberOnImage image={hexesImg}> {roundValue(projected_income)} </NumberOnImage>
                    <FocusSelectionOption focus={title} isSelected={selectedCity?.focus === title} onClick={() => handleClickFocus(title)} />
                </div>
            </div>
            <div className="panel-content">
                {children}
            </div>
        </div>
    );
}

const CityDetailWindow = ({ gameState, playerNum, playerApiUrl, setGameState, refreshSelectedCity,
    selectedCityBuildingChoices, selectedCityBuildingQueue, selectedCityBuildings, 
    selectedCityUnitChoices, selectedCityUnitQueue, selectedCity,
    unitTemplatesByBuildingName, buildingTemplates, unitTemplates, descriptions,
    setHoveredUnit, setHoveredBuilding,

     }) => {

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
        <div className="city-detail-window">
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
    );
};

export default CityDetailWindow;