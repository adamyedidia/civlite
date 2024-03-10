import React from 'react';
import './UpperRightDisplay.css';
import { Grid, Typography } from '@mui/material';
import { romanNumeral } from './TechListDialog.js';
import foodImg from './images/food.png';
import scienceImg from './images/science.png';
import woodImg from './images/wood.png';
import metalImg from './images/metal.png';
import vitalityImg from './images/heart.png';
import vpImg from './images/crown.png';
import declineImg from './images/phoenix.png';
import sadImg from './images/sadface.png';
import cityImg from './images/city.png';
import workerImg from './images/worker.png';
import ProgressBar from './ProgressBar';
import { Button } from '@mui/material';
import { TextOnIcon } from './TextOnIcon.js';
import { IconUnitDisplay } from './UnitDisplay.js';
import { BriefBuildingDisplay } from './BuildingDisplay.js';
import { WithTooltip } from './WithTooltip.js';

const CivDetailPanel = ({title, icon, iconTooltip, bignum, children}) => {
    const bignumCharLen = bignum.length;
    return (
        <div className={`civ-detail-panel ${title}-area`}>
            <WithTooltip tooltip={iconTooltip}>
                <div className="icon">
                    <img src={icon}></img>
                    <span className={bignumCharLen > 3 ? "small-font" : ""}>{bignum}</span>
                </div>
            </WithTooltip>
            <div className="panel-content">
                {children}
            </div>
        </div>
    );
}

const NewCityIcon = ({  civTemplate, size, disabled, children}) => {
    return <div className="new-city-icon" style={{height: size, width:size, backgroundColor: disabled? "#aaa" : civTemplate.primary_color, borderColor: disabled? "#888" : civTemplate.secondary_color}}> {children} </div>
}

const CityPowerDisplay = ({ civ, myCities, civTemplates, toggleFoundingCity, canFoundCity, isFoundingCity, disableUI}) => {
    const cityPowerCost = 100; // TODO is this const already defined somewhere?
    const storedProgress = (civ.city_power % cityPowerCost) / cityPowerCost * 100;
    const incomeProgress = civ.projected_city_power_income / cityPowerCost * 100;
    const newCities = Math.floor(civ.city_power / cityPowerCost);
    const civTemplate = civTemplates[civ.name];
    const iconTooltip = <table><tbody>
        <tr><td> +10 </td><td> base </td></tr>
        {myCities.map((city, index) => (
            <tr key={index}><td> +{Math.floor(city.projected_income.city_power)} </td><td> from {city.name} </td></tr>
        ))}
    </tbody></table>
    
    return <CivDetailPanel icon={cityImg} title='food' bignum={`+${Math.floor(civ.projected_city_power_income)}`}
        iconTooltip={iconTooltip}
    >
        <WithTooltip tooltip={newCities == 0  ?  "Gather City Power to build new cities" :
                newCities > 0 && !canFoundCity ? "No Valid City Sites" :
                newCities > 0 && canFoundCity && !isFoundingCity ? "Click to found city" :
                newCities > 0 && canFoundCity && isFoundingCity ? "Click to cancel found city" : null}>
        <div className={`city-power-new-cities`}>
            {[...Array(newCities)].map((_, index) => (
                <div key={index} className={`new-city-button ${(canFoundCity && index==0) ? (isFoundingCity ? 'active': 'enabled'): ''}`} onClick={disableUI? null :toggleFoundingCity}>
                    <NewCityIcon civTemplate={civTemplate} disabled={!canFoundCity || (isFoundingCity & index > 0)}>
                        +
                    </NewCityIcon>
                </div>
            ))}
        </div>
        </WithTooltip>
        <ProgressBar darkPercent={storedProgress} lightPercent={incomeProgress} barText={`${Math.floor(civ.city_power % cityPowerCost)} / ${cityPowerCost}`}/>
    </CivDetailPanel>
};


const DeclineOptionRow = ({ city, setDeclineOptionsView, civTemplates, centerMap, unitTemplates, buildingTemplates, setHoveredCiv, setHoveredUnit, setHoveredBuilding, setSelectedCity, civsById}) => {
    return <div className="decline-option-row"
        style={{
            backgroundColor: civTemplates[city.civ.name]?.primary_color, 
            borderColor: civTemplates[city.civ.name]?.secondary_color}}
        onClick = {() => {
            setDeclineOptionsView(true);
            setSelectedCity(city);
            centerMap(city.hex);
        }}
        onMouseEnter={() => setHoveredCiv(civTemplates[city.civ.name])}
        onMouseLeave={() => setHoveredCiv(null)}
        >
        <div className="revolt-cities-row">
            <TextOnIcon image={vitalityImg} offset="-10px" style={{
                width: "60px",
                height: "60px",
                position: "absolute",
                left: "-10px",
            }}>
                {Math.floor(city.revolting_starting_vitality * 100)}%
            </TextOnIcon>
            <TextOnIcon image={workerImg} style={{width: "20px", height: "20px", marginLeft: "40px"}}>
                <b>{city.population}</b>
            </TextOnIcon>
            <div className="unit-count" style={{visibility: city.revolt_unit_count > 0 ? "visible" : "hidden" }}>
                {city.revolt_unit_count}
            </div>
            {city.name}
        </div>
        <div className="revolt-cities-detail">
            {Math.floor(city.projected_income['food'])}
            <img src={foodImg}/>
            {Math.floor(city.projected_income['science'])}
            <img src={scienceImg}/>
            {Math.floor(city.projected_income['wood'])}
            <img src={woodImg}/>
            {Math.floor(city.projected_income['metal'])}
            <img src={metalImg}/>
        </div>
        <div className="revolt-cities-detail">
        {city.available_units.map((unitName, index) => (
            <div key={index} className="city-unit">
                <IconUnitDisplay 
                    unitName={unitName} 
                    unitTemplates={unitTemplates} 
                    setHoveredUnit={setHoveredUnit} 
                    style={{borderRadius: '25%', height: "30px", width: "30px"}} 
                />
            </div>
        ))}
        </div>
        <div className="revolt-cities-detail">
        {city.buildings.filter(bldg => bldg.is_wonder).map((wonder, index) => (
            <div key={index} className="city-wonder">
                <BriefBuildingDisplay key={index} buildingName={wonder.name} buildingTemplates={buildingTemplates} setHoveredBuilding={setHoveredBuilding}/>
            </div>
        ))}
        </div>
    </div>
}

const CivVitalityDisplay = ({ civVitality, myCities, turnNum, myGamePlayer, declineOptionsView, centerMap, setDeclineOptionsView, declineViewGameState, 
    unitTemplates, civTemplates, buildingTemplates,
    setSelectedCity, setHoveredCiv, setHoveredUnit, setHoveredBuilding, civsById}) => {
    const citiesReadyForRevolt = Object.values(declineViewGameState?.cities_by_id || {}).filter(city => city.is_decline_view_option);
    const unhappinessThreshold = declineViewGameState?.unhappiness_threshold
    const maxPlayerScore = Math.max(...Object.values(declineViewGameState?.game_player_by_player_num || {}).map(player => player.score));
    const distanceFromWin = declineViewGameState?.game_end_score - maxPlayerScore;
    let content = <>
        {25 < distanceFromWin && distanceFromWin < 50 && <WithTooltip tooltip="Another player is within 50 points of winning. Declining may would let them win.">
            <div className="distance-from-win">
                GAME WILL END SOON
            </div>
        </WithTooltip>}
        {turnNum > 1 && <Button className="toggle-decline-view" 
            onClick={() => setDeclineOptionsView(!declineOptionsView)}
            variant="contained" 
            color="primary"
        >
            {declineOptionsView ? "Close Decline View" : "View Decline Options"}
        </Button>}
        <div className="revolt-cities">
            {citiesReadyForRevolt.length > 0 && <>
                {citiesReadyForRevolt.sort((a, b) => b.revolting_starting_vitality - a.revolting_starting_vitality).map((city, index) => {
                    return <DeclineOptionRow key={city.id} city={city} setDeclineOptionsView={setDeclineOptionsView} centerMap={centerMap}
                        civTemplates={civTemplates} unitTemplates={unitTemplates} buildingTemplates={buildingTemplates} setHoveredCiv={setHoveredCiv} 
                        setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding} setSelectedCity={setSelectedCity} 
                        civsById={civsById}/>
                    })}
            </>}
        </div>
        {turnNum > 1 && <div className="unhappiness-threshold">
            <WithTooltip tooltip={`Threshold unhappiness to enter decline choices: ${unhappinessThreshold?.toFixed(2)}`}>
                <div className="unhappiness-threshold-content">
                    {Math.floor(unhappinessThreshold)}
                    <img src={sadImg} height="16px"/>
                </div>
            </WithTooltip>
        </div>}
    </>
    if (0 < distanceFromWin && distanceFromWin <= 25) {
        content = <WithTooltip tooltip="Another player is within 25 points of winning. Declining now would let them win instantly.">
        <div className="distance-from-win">
            <div>GAME WILL END SOON</div>
            <div className="distance-from-win-warning">
                DECLINE IMPOSSIBLE
            </div>
        </div>
        </WithTooltip>
    }
    return <CivDetailPanel icon={vitalityImg} title='vitality' bignum={`${Math.round(civVitality * 100)}%`}>
        {content}
    </CivDetailPanel>
}

const ScoreDisplay = ({ myGamePlayer, gameEndScore }) => {
    const score = myGamePlayer?.score;
    return <CivDetailPanel icon={vpImg} title='score' bignum={score} iconTooltip={`${gameEndScore} points to win`}>
        <Grid container direction="column" spacing={0}>
            <Grid item>
                <Typography>
                    {myGamePlayer?.sfku || 0} killing units (1/kill)
                </Typography>
            </Grid>
            <Grid item>
                <Typography>
                    {myGamePlayer?.sfccac || 0} camp/city captures (5/capture)
                </Typography>
            </Grid>
            <Grid item>
                <Typography>
                    {myGamePlayer?.sfrt || 0} research (2/tech)
                </Typography>
            </Grid>
            <Grid item>
                <Typography>
                    {myGamePlayer?.sfbv || 0} buildings and wonders
                </Typography>
            </Grid>
            <Grid item>
                <Typography>
                    {myGamePlayer?.sfa || 0} abilities
                </Typography>
            </Grid>
            <Grid item>
                <Typography>
                    {myGamePlayer?.sfs || 0} survival  (25/decline)
                </Typography>
            </Grid>
            <Grid item>
                <Typography>
                    {myGamePlayer?.sfrc || 0} revolting units (1/unit)
                </Typography>
            </Grid>                                                                     
        </Grid>
    </CivDetailPanel>
}

const ScienceDisplay = ({civ, myCities, techTemplates, setTechListDialogOpen, setTechChoiceDialogOpen, setHoveredTech, disableUI}) => {
    const tech = techTemplates[civ.researching_tech_name];
    const techCost = tech?.name  == "Renaissance" ? civ.renaissance_cost : tech?.cost;
    const storedProgress = tech ? civ.science / techCost * 100 : 0;
    const incomeProgress = tech ? civ.projected_science_income / techCost * 100 : 0;
    const iconTooltip = <table><tbody>
        {myCities.map((city, index) => (
            <tr key={index}><td> +{Math.floor(city.projected_income.science)} </td><td> from {city.name} </td></tr>
        ))}
    </tbody></table>
    return <CivDetailPanel title='science' icon={scienceImg} iconTooltip={iconTooltip} bignum={`+${Math.floor(civ.projected_science_income)}`}>
        <h2 className="tech-name" 
            onMouseEnter={tech ? () => setHoveredTech(techTemplates[tech.name]) : () => {}}
            onMouseLeave={() => setHoveredTech(null)}  
        > {romanNumeral(tech?.advancement_level)}. {tech?.name} </h2>
        <ProgressBar darkPercent={storedProgress} lightPercent={incomeProgress} barText={tech ? `${Math.floor(civ.science)} / ${techCost}` : `${Math.floor(civ.science)} / ???`}/>
        <Button variant="contained" color="primary" onClick={() => setTechListDialogOpen(true)}>
            Tech Tree
        </Button>
        <Button variant="contained" color="primary" disabled={disableUI} onClick={() => {
            setTechChoiceDialogOpen(true);
        }}>
            Change
        </Button>
    </CivDetailPanel>
}

const UpperRightDisplay = ({ gameState, canFoundCity, isFoundingCity, disableUI, centerMap, declineOptionsView,
    civTemplates, unitTemplates, buildingTemplates,
    setConfirmEnterDecline, setTechChoiceDialogOpen, setHoveredUnit, setHoveredBuilding, setHoveredTech, 
    toggleFoundingCity, techTemplates, myCiv, myGamePlayer, setTechListDialogOpen, 
    turnNum, setDeclineOptionsView, declineViewGameState, setSelectedCity, setHoveredCiv, civsById}) => {
    const myCities = Object.values(gameState.cities_by_id).filter(city => civsById?.[city.civ_id]?.game_player?.player_num === myGamePlayer?.player_num);
    return (
        <div className="upper-right-display">
            {myCiv && <ScienceDisplay civ={myCiv} myCities={myCities} setTechListDialogOpen={setTechListDialogOpen} setTechChoiceDialogOpen={setTechChoiceDialogOpen} setHoveredTech={setHoveredTech} techTemplates={techTemplates} disableUI={disableUI}/>}
            {myCiv && <CityPowerDisplay civ={myCiv} myCities={myCities} civTemplates={civTemplates} toggleFoundingCity={toggleFoundingCity} canFoundCity={canFoundCity} isFoundingCity={isFoundingCity} disableUI={disableUI}/>}
            {myCiv && <CivVitalityDisplay civVitality={myCiv.vitality} myGamePlayer={myGamePlayer} turnNum={turnNum}
                disableUI={disableUI} centerMap={centerMap} declineOptionsView={declineOptionsView} setDeclineOptionsView={setDeclineOptionsView} 
                declineViewGameState={declineViewGameState} civTemplates={civTemplates} unitTemplates={unitTemplates} buildingTemplates={buildingTemplates} 
                setSelectedCity={setSelectedCity} setHoveredCiv={setHoveredCiv} setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding}
                civsById={civsById}/>}
            {myGamePlayer && <ScoreDisplay myGamePlayer={myGamePlayer} gameEndScore={gameState.game_end_score}/>}
        </div>
    );
};

export default UpperRightDisplay;