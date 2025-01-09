import React from "react";

import { lowercaseAndReplaceSpacesWithUnderscores } from "./lowercaseAndReplaceSpacesWithUnderscores";

import workerIcon from './images/worker.png';
import vpImage from './images/crown.png';
import vitalityImg from './images/heart.png';
import declineImg from './images/phoenix.png';

const cityBoxCanvas = {'width': 8, 'height': 6};

export const CityRectangle = ({cityBoxPanel, primaryColor, secondaryColor, puppet, friendly, cityName, onMouseEnter, gameState, onClick, children, capitalCityNames, darkMode}) => {
    const capital = capitalCityNames.includes(cityName);
    const cityBoxPanelBottomY = cityBoxCanvas.height / 2 + cityBoxPanel.height / 2
    return <svg width={cityBoxCanvas.width} height={cityBoxCanvas.height} viewBox={`0 0 ${cityBoxCanvas.width} ${cityBoxCanvas.height}`} x={-cityBoxCanvas.width / 2} y={-1.5 - cityBoxCanvas.height / 2} onMouseEnter={onMouseEnter} onClick={onClick} style={{...(friendly ? {cursor : 'pointer'} : {})}}>
        {/* Background rectangle */}
        {capital && <>
            <rect width={cityBoxPanel.width / 4} height={cityBoxPanel.height} x={(cityBoxCanvas.width - cityBoxPanel.width) / 2} y={(cityBoxCanvas.height - cityBoxPanel.height) / 2 - 3/4 * cityBoxPanel.height} fill={primaryColor} stroke={secondaryColor} strokeWidth={0.2}/>
            <rect width={cityBoxPanel.width / 4} height={cityBoxPanel.height} x={(cityBoxCanvas.width - cityBoxPanel.width) / 2 + 3/4 * cityBoxPanel.width} y={(cityBoxCanvas.height - cityBoxPanel.height) / 2 - 3/4 * cityBoxPanel.height} fill={primaryColor} stroke={secondaryColor} strokeWidth={0.2}/>
            <circle cx={cityBoxCanvas.width / 2} cy={cityBoxCanvas.height / 2 - cityBoxPanel.height / 2} r={cityBoxPanel.width / 4} fill={primaryColor} stroke={secondaryColor} strokeWidth={0.2}/>
        </>}
        <rect width={cityBoxPanel.width} height={cityBoxPanel.height} x={(cityBoxCanvas.width - cityBoxPanel.width) / 2} y={(cityBoxCanvas.height - cityBoxPanel.height) / 2} fill={primaryColor} stroke={secondaryColor} strokeWidth={0.2} {...(puppet ? {rx: "1", ry: "1"} : {})}/>
        {/* Pointer triangle. make the fill and the stroke separately so the fill can cover the border of the main box without the stroke looking dumb */}
        <path d={`M3.3,${cityBoxPanelBottomY-0.12} L4,${cityBoxPanelBottomY + 1} L4.7,${cityBoxPanelBottomY-0.12}`} style={{opacity: 1.0, fill: primaryColor, stroke: "none", strokeWidth: 0.2}} />
        <path d={`M3.3,${cityBoxPanelBottomY} L4,${cityBoxPanelBottomY + 1} L4.7,${cityBoxPanelBottomY}`} style={{strokeOpacity: 1.0, stroke: secondaryColor, strokeWidth: 0.2}} />
        <text x="50%" y={0.3 + cityBoxCanvas.height / 2} dominantBaseline="middle" textAnchor="middle" style={{fontSize: "0.8px", fill: darkMode ? "white" : "black"}}>
            {cityName}
        </text>
        {children}
    </svg>
}

export const FogCity = ({ cityName, capitalCityNames }) => {
    return <CityRectangle 
        cityBoxPanel={{width: 6, height: 2}} 
        primaryColor="#bbbbbb" 
        secondaryColor="#888888" 
        puppet={false} 
        cityName={cityName}
        capitalCityNames={capitalCityNames}
        darkMode={false}
    >
        <rect width={cityBoxCanvas.width} height={cityBoxCanvas.height} fill="none" stroke="none" />
    </CityRectangle>
}

export default function City({ 
    city, 
    isHovered, 
    isSelected, 
    isUnitInHex, 
    everControlled, 
    myGamePlayer, 
    templates,
    isFriendlyCity,
    gameState,
    playerNum,
    declineOptionsView,
    civsById,
    handleMouseOverCity,
    handleClickCity,
    myCiv,
    capitalCityNames,
}) {
    const civTemplate = templates.CIVS[civsById?.[city.civ_id]?.name]
    const civName = civTemplate?.name;

    const primaryColor = civTemplate?.primary_color;
    const secondaryColor = civTemplate?.secondary_color;

    const friendly = isFriendlyCity(city);
    const puppet = city.territory_parent_coords;

    const colors = 
        {'wood': '#e0b096',
        'food': '#ccffaa',
        'metal': '#bbbbbb',
        'science': '#b0e0e6'}
    const focusColor = friendly ? colors[city.focus] : primaryColor;
    let buildingText;
    let buildingIconUnit;
    if (city.buildings_queue.length === 0) {
        buildingText = "??";
        buildingIconUnit = null;
    } else if (templates.UNITS[city.buildings_queue[0].template_name]) {
        buildingText = "";
        buildingIconUnit = templates.UNITS[city.buildings_queue[0].template_name].name;
    } else {
        buildingText = city.buildings_queue[0].template_name.slice(0, 2);
        buildingIconUnit = null;
    }
    const buildingImage = buildingIconUnit && `/images/${lowercaseAndReplaceSpacesWithUnderscores(buildingIconUnit)}.svg`; 

    const unitText = !city.icon_unit_name && "??";
    const unitIconUnit = city.icon_unit_name;    
    const unitImage = unitIconUnit && `/images/${lowercaseAndReplaceSpacesWithUnderscores(unitIconUnit)}.svg`;

    const cityBoxPanel = {'width': (puppet ? 5 : 6), 'height': 2};
    const cityCircleRadius = 0.75;

    const cityCirclesY = (cityBoxCanvas.height - cityBoxPanel.height) / 2
    const cityCirclesTextY = cityCirclesY + 0.05;
    return (
        <>
            {isHovered && <circle cx="0" cy={`${isUnitInHex ? -1 : 0}`} r="2.25" fill="none" stroke="white" strokeWidth="0.2"/>}
            {isSelected && <circle cx="0" cy={`${isUnitInHex ? -1 : 0}`} r="2.25" fill="none" stroke="black" strokeWidth="0.2"/>}
            {city.under_siege_by_civ_id && <svg width="6" height="6" viewBox="0 0 6 6" x={-3} y={isUnitInHex ? -4 : -3}>
                    <image href="/images/fire.svg" x="0" y="0" height="6" width="6" />
                </svg>
            }
            {/* {civName && <image href={civNameToFlagImgSrc(civName)} x={-1.6} y={-4.6} height={2} width={3} />} */}
            <CityRectangle
                cityBoxPanel={cityBoxPanel} 
                primaryColor={primaryColor} 
                secondaryColor={secondaryColor} 
                puppet={puppet} 
                cityName={city.name} 
                onMouseEnter={() => handleMouseOverCity(city)} 
                onClick={() => handleClickCity(city)} 
                friendly={friendly}
                gameState={gameState}
                capitalCityNames={capitalCityNames}
                darkMode={civTemplate?.darkmode}
            >
                {/* Population */}
                <circle cx="50%" cy={cityCirclesY} r={cityCircleRadius} fill={focusColor} stroke={secondaryColor} strokeWidth="0.1"/>
                <image opacity={.7} href={workerIcon} x="3.5" y="1.4" height="1" width="1" />
                <text x="50%" y={cityCirclesTextY} dominantBaseline="middle" textAnchor="middle" style={{fontSize: "1.2px"}}>
                    {city.population}
                </text>              

                {friendly && puppet === null &&
                    <>
                        {/* Wood */}
                        <circle cx="1.7" cy={cityCirclesY} r={cityCircleRadius} fill={colors.wood} stroke={secondaryColor} strokeWidth="0.1"/>
                        <image href={buildingImage} x={1.2} y={1.45} height="1" width="1" />
                        <text x="1.7" y={cityCirclesTextY} dominantBaseline="middle" textAnchor="middle" style={{fontSize: "0.8px"}}>
                            {buildingText}
                        </text>    

                        {/* Metal */}
                        <circle cx="6.3" cy={cityCirclesY} r={cityCircleRadius} fill={colors.metal} stroke={secondaryColor} strokeWidth="0.1"/>
                        <image href={unitImage} x={5.8} y={1.45} height="1" width="1" />
                        <text x="6.3" y={cityCirclesTextY} dominantBaseline="middle" textAnchor="middle" style={{fontSize: "0.8px"}}>
                            {unitText}
                        </text>    
                    </>
                }
                {friendly && (city.projected_on_decline_leaderboard || city.civ_to_revolt_into) && <>
                    <circle cx={6.5} cy={3} r={0.7} fill={city.civ_to_revolt_into ? "white" : "lightgrey"} opacity={city.civ_to_revolt_into ? 1 : 0.75}/>
                    <image href={declineImg} x={6.0} y={2.5} height="1" opacity={city.civ_to_revolt_into ? 1 : 0.75}/>
                </>
                }
                {myCiv && !everControlled && 
                    <image href={vpImage} x={5.75} y={1.1} height="1" />
                }
            </CityRectangle>
            {declineOptionsView && city.is_decline_view_option && <>
                <image href={vitalityImg} x="-1.8" y="-1" height="3.6" width="3.6" />
                <text x="0" y="0.4" dominantBaseline="middle" textAnchor="middle" style={{fontSize: "1.2px"}}>
                    {Math.floor(city.revolting_starting_vitality * 100 * myGamePlayer.vitality_multiplier)}%
                </text>
                </>
            }
            {!declineOptionsView && friendly && city.revolting_to_rebels_this_turn && <>
                <image href={declineImg} x="-1.5" y="-2.5" height="3" width="3" style={{ pointerEvents: 'none' }}/>
                </>
            }
        </>
    );
};