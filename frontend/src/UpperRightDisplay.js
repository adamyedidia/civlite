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
            <WithTooltip tooltip={iconTooltip} alignBottom={title === 'science'}>
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

const CityPowerDisplay = ({ civ, myCities, templates, toggleFoundingCity, canFoundCity, isFoundingCity, disableUI}) => {
    const cityPowerCost = 100; // TODO is this const already defined somewhere?
    const storedProgress = (civ.city_power % cityPowerCost) / cityPowerCost * 100;
    const incomeProgress = civ.projected_city_power_income / cityPowerCost * 100;
    const newCities = Math.max(0, Math.floor(civ.city_power / cityPowerCost));
    const civTemplate = templates.CIVS[civ.name];
    const iconTooltip = <table><tbody>
        <tr><td> +10 </td><td> base </td></tr>
        {myCities?.map((city, index) => {
            const amount = Math.floor(city.projected_income['city-power']);
            return amount != 0 && <tr key={index}><td> +{amount} </td><td> from {city.name} </td></tr>
        })}
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


const DeclineOptionRow = ({ city, isMyCity, myCiv, setDeclineOptionsView, templates, centerMap, setHoveredCiv, setHoveredUnit, setHoveredBuilding, setSelectedCity, civsById}) => {
    return <div className="decline-option-row"
        style={{
            backgroundColor: templates.CIVS[city.civ.name]?.primary_color, 
            borderColor: templates.CIVS[city.civ.name]?.secondary_color}}
        onClick = {() => {
            setDeclineOptionsView(true);
            setSelectedCity(city);
            centerMap(city.hex);
        }}
        onMouseEnter={() => setHoveredCiv(templates.CIVS[city.civ.name])}
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
            {isMyCity && <div className="my-city-revolting"
                            style={{
                                backgroundColor: templates.CIVS[myCiv.name]?.primary_color, 
                                borderColor: templates.CIVS[myCiv.name]?.secondary_color}}
                        >
                <WithTooltip tooltip="Your city">
                    !!
                </WithTooltip>
            </div>}
        </div>
        <div className="revolt-cities-detail">
            {Math.floor(city.projected_income_base['food'])}
            <img src={foodImg}/>
            {Math.floor(city.projected_income_base['science'])}
            <img src={scienceImg}/>
            {Math.floor(city.projected_income_base['wood'])}
            <img src={woodImg}/>
            {Math.floor(city.projected_income_base['metal'])}
            <img src={metalImg}/>
        </div>
        <div className="revolt-cities-detail">
        {city.available_units.map((unitName, index) => (
            <div key={index} className="city-unit">
                <IconUnitDisplay 
                    unitName={unitName} 
                    templates={templates} 
                    setHoveredUnit={setHoveredUnit} 
                    style={{borderRadius: '25%', height: "30px", width: "30px"}} 
                />
            </div>
        ))}
        </div>
        <div className="revolt-cities-detail">
        {city.buildings.filter(bldg => templates.BUILDINGS[bldg.name]?.is_wonder).map((wonder, index) => {
            return <div key={index} className="city-wonder">
                <BriefBuildingDisplay key={index} buildingName={wonder.name} clickable={false} hideCost={true} templates={templates} setHoveredBuilding={setHoveredBuilding}
                    style={{fontSize: "12px", width: "60px", margin: "2px"}}
                />
            </div>
        })}
        </div>
    </div>
}

const CivVitalityDisplay = ({ playerNum, myCiv, turnNum, centerMap, 
    setDeclineOptionsView, declineViewGameState, mainGameState, declineOptionsView, 
    templates,
    setSelectedCity, setHoveredCiv, setHoveredUnit, setHoveredBuilding, civsById}) => {
    const citiesReadyForRevolt = Object.values(declineViewGameState?.cities_by_id || {}).filter(city => city.is_decline_view_option);
    const unhappinessThreshold = mainGameState?.unhappiness_threshold
    // Max of all other players' scores
    const maxPlayerScore = Math.max(...Object.values(mainGameState?.game_player_by_player_num || {}).map(player => player.player_num === playerNum ? 0 : player.score));
    const distanceFromWin = mainGameState?.game_end_score - maxPlayerScore;
    let content = <>
        {25 < distanceFromWin && distanceFromWin < 50 && <WithTooltip tooltip="Another player is within 50 points of winning. Declining may let them win.">
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
                    const mainGameStateCity = mainGameState.cities_by_id[city.id];
                    const isMyCity = mainGameStateCity && mainGameStateCity.civ_id === myCiv.id;
                    return <DeclineOptionRow key={city.id} city={city} isMyCity={isMyCity} myCiv={myCiv} setDeclineOptionsView={setDeclineOptionsView} centerMap={centerMap}
                        templates={templates} setHoveredCiv={setHoveredCiv} 
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
    if (0 < distanceFromWin && distanceFromWin <= 25 && !declineOptionsView) {
        content = <WithTooltip tooltip="Another player is within 25 points of winning. Declining now would let them win instantly.">
        <div className="distance-from-win">
            <div>GAME WILL END SOON</div>
            <div className="distance-from-win-warning">
                DECLINE IMPOSSIBLE
            </div>
        </div>
        </WithTooltip>
    }
    return <CivDetailPanel icon={vitalityImg} title='vitality' bignum={`${Math.round(myCiv.vitality * 100)}%`}>
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

const ScienceDisplay = ({civ, myCities, templates, setTechListDialogOpen, setTechChoiceDialogOpen, setHoveredTech, disableUI}) => {
    const tech = templates.TECHS[civ.researching_tech_name];
    const techCost = tech?.name  == "Renaissance" ? civ.renaissance_cost : tech?.cost;
    const storedProgress = tech ? civ.science / techCost * 100 : 0;
    const incomeProgress = tech ? civ.projected_science_income / techCost * 100 : 0;
    const iconTooltip = <table><tbody>
        {myCities?.map((city, index) => (
            <tr key={index}><td> +{Math.floor(city.projected_income.science)} </td><td> from {city.name} </td></tr>
        ))}
    </tbody></table>
    return <CivDetailPanel title='science' icon={scienceImg} iconTooltip={iconTooltip} bignum={`+${Math.floor(civ.projected_science_income)}`}>
        <h2 className="tech-name" 
            onMouseEnter={tech ? () => setHoveredTech(templates.TECHS[tech.name]) : () => {}}
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

const UpperRightDisplay = ({ mainGameState, canFoundCity, isFoundingCity, disableUI, centerMap, declineOptionsView,
    templates,
    setConfirmEnterDecline, setTechChoiceDialogOpen, setHoveredUnit, setHoveredBuilding, setHoveredTech, 
    toggleFoundingCity, myCiv, myGamePlayer, myCities, setTechListDialogOpen, 
    turnNum, setDeclineOptionsView, declineViewGameState, setSelectedCity, setHoveredCiv, civsById}) => {
    return (
        <div className="upper-right-display">
            {myCiv && <ScienceDisplay civ={myCiv} myCities={myCities} setTechListDialogOpen={setTechListDialogOpen} setTechChoiceDialogOpen={setTechChoiceDialogOpen} setHoveredTech={setHoveredTech} templates={templates} disableUI={disableUI}/>}
            {myCiv && <CityPowerDisplay civ={myCiv} myCities={myCities} templates={templates} toggleFoundingCity={toggleFoundingCity} canFoundCity={canFoundCity} isFoundingCity={isFoundingCity} disableUI={disableUI}/>}
            {myCiv && <CivVitalityDisplay playerNum={myGamePlayer?.player_num} myCiv={myCiv} myGamePlayer={myGamePlayer} turnNum={turnNum}
                disableUI={disableUI} centerMap={centerMap} declineOptionsView={declineOptionsView} setDeclineOptionsView={setDeclineOptionsView} 
                declineViewGameState={declineViewGameState} mainGameState={mainGameState} templates={templates}
                setSelectedCity={setSelectedCity} setHoveredCiv={setHoveredCiv} setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding}
                civsById={civsById}/>}
            {myGamePlayer && <ScoreDisplay myGamePlayer={myGamePlayer} gameEndScore={mainGameState.game_end_score}/>}
        </div>
    );
};

export default UpperRightDisplay;