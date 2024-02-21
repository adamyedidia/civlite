import React from 'react';
import './CityDetailWindow.css';

import { BriefBuildingDisplay, BriefBuildingDisplayTitle } from './BuildingDisplay';
import {BriefUnitDisplay, BriefUnitDisplayTitle} from './UnitDisplay';

const FocusSelectionOption = ({ focus, onClick, isSelected }) => {
    return (
        <div
            className={`focus-selection-option ${focus} ${isSelected ? 'selected' : ''}`}
            onClick={onClick}
        >
            <span>{focus}</span>
        </div>
    );
}

const FocusSelectorTitle = ({ title }) => {
    return (
        <div 
            className="focus-title-card" 
        >
            <span>{title}</span>
        </div>        
    );
}

const CityDetailWindow = ({ gameState, playerNum, playerApiUrl, setGameState, refreshSelectedCity,
    selectedCityBuildingChoices, selectedCityBuildingQueue, selectedCityBuildings, 
    selectedCityUnitChoices, selectedCityUnitQueue, selectedCity,
    unitTemplatesByBuildingName, buildingTemplates, unitTemplates, descriptions,
    setHoveredUnit, setHoveredBuilding
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

    return (
        <div className="city-detail-window">
            {selectedCityBuildingChoices && (
                <div className="building-choices-container">
                    <BriefBuildingDisplayTitle title="Building Choices" />
                    {selectedCityBuildingChoices.map((buildingName, index) => (
                        <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} onClick={() => handleClickBuildingChoice(buildingName)} descriptions={descriptions} />
                    ))}
                </div>
            )};
            {selectedCityBuildingQueue && (
                <div className="building-queue-container">
                    <BriefBuildingDisplayTitle title="Building Queue" />
                    {selectedCityBuildingQueue.map((buildingName, index) => (
                        <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} onClick={() => handleCancelBuilding(buildingName)} descriptions={descriptions}/>
                    ))}
                </div>
            )};                
            {selectedCityBuildings && (
                <div className="existing-buildings-container">
                    <BriefBuildingDisplayTitle title="Existing buildings" />
                    {selectedCityBuildings.map((buildingName, index) => (
                        <BriefBuildingDisplay key={index} buildingName={buildingName} unitTemplatesByBuildingName={unitTemplatesByBuildingName} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding} descriptions={descriptions}/>
                    ))}
                </div>
            )};  
            {selectedCityUnitChoices && (
                <div className="unit-choices-container">
                    <BriefUnitDisplayTitle title="Unit Choices" />
                    {selectedCityUnitChoices.map((unitName, index) => (
                        <BriefUnitDisplay key={index} unitName={unitName} unitTemplates={unitTemplates} setHoveredUnit={setHoveredUnit} onClick={() => handleClickUnitChoice(unitName)} />
                    ))}
                </div>
            )};
            {selectedCityUnitQueue && (
                <div className="unit-queue-container">
                    <BriefUnitDisplayTitle title="Unit Queue" />
                    {selectedCityUnitQueue.map((unitName, index) => (
                        <BriefUnitDisplay key={index} unitName={unitName} unitTemplates={unitTemplates} setHoveredUnit={setHoveredUnit} onClick={() => handleCancelUnit(index)}/>
                    ))}
                </div>
            )};
            {selectedCity && !gameState?.special_mode_by_player_num?.[playerNum] && (
                <div className="focus-container">
                    <FocusSelectorTitle title="City Focus" />
                    <FocusSelectionOption focus="food" isSelected={selectedCity.focus === 'food'} onClick={() => handleClickFocus('food')} />
                    <FocusSelectionOption focus="wood" isSelected={selectedCity.focus === 'wood'} onClick={() => handleClickFocus('wood')} />
                    <FocusSelectionOption focus="metal" isSelected={selectedCity.focus === 'metal'} onClick={() => handleClickFocus('metal')} />
                    <FocusSelectionOption focus="science" isSelected={selectedCity.focus === 'science'} onClick={() => handleClickFocus('science')} />
                </div>
            )}
        </div>
    );
};

export default CityDetailWindow;