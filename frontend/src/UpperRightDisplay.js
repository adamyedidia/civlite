import React, { useState } from 'react';
import './UpperRightDisplay.css';
import { Grid, Table, TableBody, TableRow, TableCell, TableContainer, MenuItem, FormControl, InputLabel, Select, Tooltip } from '@mui/material';
import { romanNumeral } from "./romanNumeral.js";
import scienceImg from './images/science.png';
import vitalityImg from './images/heart.png';
import vpImg from './images/crown.png';
import sadImg from './images/sadface.png';
import cityImg from './images/city.png';
import workerImg from './images/worker.png';
import wonderImg from './images/wonders.png';
import ProgressBar from './ProgressBar';
import { Button } from '@mui/material';
import { TextOnIcon } from './TextOnIcon.js';
import { IconUnitDisplay } from './UnitDisplay.js';
import { YieldsDisplay } from './BuildingDisplay.js';
import { WithTooltip } from './WithTooltip.js';

const CivDetailPanel = ({title, icon, iconTooltip, bignum, children}) => {
    const bignumCharLen = bignum.length;
    return (
        <div className={`civ-detail-panel ${title}-area`}>
            <WithTooltip tooltip={iconTooltip} alignBottom={title === 'science'}>
                <div className="icon">
                    <img src={icon} alt=""></img>
                    <span className={bignumCharLen > 3 ? "small-font" : ""}>{bignum}</span>
                </div>
            </WithTooltip>
            <div className="panel-content">
                {children}
            </div>
        </div>
    );
}

const NewCityIcon = ({  civTemplate, size, disabled, children, atMaxTerritories}) => {
    return <div className={`new-city-icon ${atMaxTerritories ? "at-max" : ""}`} style={{height: size, width:size, backgroundColor: disabled? "#aaa" : civTemplate.primary_color, borderColor: disabled? "#888" : civTemplate.secondary_color}}> {children} </div>
}

const CityPowerDisplay = ({ civ, myCities, templates, toggleFoundingCity, canFoundCity, isFoundingCity, disableUI}) => {
    const cityPowerCost = 100; // TODO is this const already defined somewhere?
    const storedProgress = (civ.city_power % cityPowerCost) / cityPowerCost * 100;
    const incomeProgress = civ.projected_city_power_income / cityPowerCost * 100;
    const newCities = Math.max(0, Math.floor(civ.city_power / cityPowerCost));
    const civTemplate = templates.CIVS[civ.name];
    const currentTerritories = myCities.filter(city => !city.territory_parent_id).length;
    const atMaxTerritories = currentTerritories === civ.max_territories;
    const iconTooltip = <table><tbody>
        <tr><td> +10 </td><td> base </td></tr>
        {myCities?.map((city, index) => {
            const amount = Math.floor(city.projected_income['city_power']);
            return amount !== 0 && <tr key={index}><td> +{amount} </td><td> from {city.name} </td></tr>
        })}
    </tbody></table>
    
    return <CivDetailPanel icon={cityImg} title='food' bignum={`+${Math.floor(civ.projected_city_power_income)}`}
        iconTooltip={iconTooltip}
    >
        <div className='city-power-top-row'>
        <WithTooltip tooltip={newCities === 0  ?  "Gather City Power to build new cities" :
                newCities > 0 && !canFoundCity ? "No Valid City Sites" :
                newCities > 0 && canFoundCity && !isFoundingCity ? "Click to found city" :
                newCities > 0 && canFoundCity && isFoundingCity ? "Click to cancel found city" : null}>
        <div className={`city-power-new-cities`}>
            {[...Array(newCities)].map((_, index) => (
                <div key={index} className={`new-city-button ${(canFoundCity && index===0) ? (isFoundingCity ? 'active': 'enabled'): ''}`} onClick={disableUI? null :toggleFoundingCity}>
                    <NewCityIcon civTemplate={civTemplate} disabled={!canFoundCity || (isFoundingCity & index > 0)} atMaxTerritories={atMaxTerritories}>
                        +
                    </NewCityIcon>
                </div>
            ))}
        </div>
        </WithTooltip>
        <WithTooltip tooltip="Current / max territories">
            <div className='city-power-territories' style={{
                backgroundColor: civTemplate.primary_color,
                borderColor: civTemplate.secondary_color,
            }}>
                {currentTerritories}/{civ.max_territories}
            </div>
        </WithTooltip>
        </div>
        <ProgressBar darkPercent={storedProgress} lightPercent={incomeProgress} barText={`${Math.floor(civ.city_power % cityPowerCost)} / ${cityPowerCost}`}/>
    </CivDetailPanel>
};

const WonderDisplay = ({ wonder, available, setHoveredWonder }) => {
    return <div className={`wonder-display ${available ? "" : "built"}`} onMouseEnter={() => setHoveredWonder(wonder)} onMouseLeave={() => setHoveredWonder(null)}>
        {wonder.name}
    </div>
}

const WonderAgeDisplay = ({ age, unlocked, wonders, available_wonders, vp_chunks_left, vp_chunks_total, templates, setHoveredWonder }) => {
    const vp_chunks_next_wonder = unlocked ? (vp_chunks_left == vp_chunks_total ? 2 : vp_chunks_left > 0 ? 1 : 0) : 0;
    const tooltip = !unlocked ? `Age ${age} not unlocked yet` :
        vp_chunks_left < 0 ? `Maximum wonders built` :
        `Next wonder earns ${vp_chunks_next_wonder} crowns (${vp_chunks_next_wonder * 5} vps)`;

    return <div className={`wonder-age-display ${unlocked ? "unlocked" : "locked"}`}>
        <div className="wonder-age">{romanNumeral(age)}</div>
        <Tooltip title={tooltip}>
            <div className="wonder-vp-container">
            <div className="wonder-vp">
            {vp_chunks_next_wonder > 0 && <div className="wonder-vps-next" style={{width: `${vp_chunks_next_wonder * (16+6)}px`}}/>}
            {[...Array(vp_chunks_total)].map((_, index) => (
                <img 
                    key={index}
                    src={vpImg} 
                    alt="Crown"
                    className={index >= vp_chunks_left ? 'wonder-vp-unavailable' : 'wonder-vp-available'}
                    style={{width: '16px', height: '16px'}}
                />
            ))}
            </div></div>
        </Tooltip>
        {wonders.map((wonder, index) => (
            <WonderDisplay key={index} wonder={templates.WONDERS[wonder]} available={available_wonders.includes(wonder)} templates={templates} setHoveredWonder={setHoveredWonder}/>
        ))}
    </div>
}

const WonderListDisplay = ({ wonders_by_age, game_age, available_wonders, templates, setHoveredWonder, vp_chunks_left_by_age, vp_chunks_total_per_age }) => {
    return <CivDetailPanel title="wonders" icon={wonderImg} iconTooltip="Wonders" bignum="">
    <div className="wonder-list-display">
        {Object.entries(wonders_by_age).map(([age, wonders]) => {
            return <WonderAgeDisplay key={age} unlocked={game_age >= parseInt(age)} age={parseInt(age)} wonders={wonders} available_wonders={available_wonders}
             vp_chunks_left={vp_chunks_left_by_age[age]} vp_chunks_total={vp_chunks_total_per_age} templates={templates} setHoveredWonder={setHoveredWonder}/>
        })}
    </div>
    </CivDetailPanel>
}

const DeclineOptionRow = ({ city, isMyCity, myCiv, setDeclineOptionsView, templates, centerMap, setHoveredCiv, setHoveredUnit, setHoveredBuilding, setSelectedCity, declineViewCivsById, myGamePlayer}) => {
    const civ = declineViewCivsById[city.civ_id];
    const civTemplate = templates.CIVS[civ.name];
    return <div className="decline-option-row clickable"
        style={{
            backgroundColor: civTemplate.primary_color, 
            borderColor: civTemplate.secondary_color}}
        onClick = {() => {
            setDeclineOptionsView(true);
            setSelectedCity(city);
            centerMap(city.hex);
        }}
        onMouseEnter={() => setHoveredCiv(civ)}
        onMouseLeave={() => setHoveredCiv(null)}
        >
        <div className="revolt-cities-row">
            <TextOnIcon image={vitalityImg} offset="-10px" style={{
                width: "60px",
                height: "60px",
                position: "absolute",
                left: "-10px",
            }}>
                {Math.floor(city.revolting_starting_vitality * 100 * myGamePlayer.vitality_multiplier)}%
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
        <div className="revolt-cities-detail-container">
        <div className="revolt-cities-detail">
            <YieldsDisplay yields={city.projected_income_base}/>
        </div>
        <div className="revolt-cities-detail">
            {city.available_units.map((unitName, index) => (
                <div key={index} className="slot military">
                    <IconUnitDisplay 
                        unitName={unitName} 
                        templates={templates} 
                        setHoveredUnit={setHoveredUnit} 
                        size={20}
                        style={{border: '0px'}}
                    />
                </div>
            ))}
            {Array.from({length: city.military_slots - city.available_units.length}, (_, index) => (
                <div key={index} className="slot military"></div>
            ))}
            {Array.from({length: city.rural_slots}, (_, index) => (
                <div key={index} className="slot rural"></div>
            ))}
            {Array.from({length: city.urban_slots}, (_, index) => (
                <div key={index} className="slot urban"></div>
            ))}
        </div>
        </div>
    </div>
}

const CivVitalityDisplay = ({ playerNum, myCiv, turnNum, centerMap, myGamePlayer,
    setDeclineOptionsView, declineViewGameState, mainGameState, declineOptionsView, 
    templates, 
    setSelectedCity, setHoveredCiv, setHoveredUnit, setHoveredBuilding, declineViewCivsById}) => {
    const citiesReadyForRevolt = Object.values(declineViewGameState?.cities_by_id || {}).filter(city => city.is_decline_view_option);
    const citiesRevoltingNextTurn = Object.values(mainGameState?.cities_by_id || {}).filter(city => (city.projected_on_decline_leaderboard && city.civ_id == myCiv?.id && !citiesReadyForRevolt.map(c => c.id).includes(city.id)));
    const unhappinessThreshold = mainGameState?.unhappiness_threshold
    const previousUnhappinessThreshold = mainGameState?.previous_unhappiness_threshold
    // Max of all other players' scores
    const maxPlayerScore = Math.max(...Object.values(mainGameState?.game_player_by_player_num || {}).map(player => player.player_num === playerNum ? 0 : player.score));
    const distanceFromWin = mainGameState?.game_end_score - maxPlayerScore;
    const newUnhappinessThresholdHigher = unhappinessThreshold > previousUnhappinessThreshold;
    const unhappinesThresholdObject = <div className="unhappiness-threshold" style={{bottom: newUnhappinessThresholdHigher ? "" : "-10px", top: newUnhappinessThresholdHigher ? `${20 + Math.min(5, citiesReadyForRevolt.length) * 30}px` : ""}}>
            <Tooltip title={`Next turn's threshold: ${unhappinessThreshold?.toFixed(2)}`}>
                <div className="unhappiness-threshold-content">
                    {Math.floor(unhappinessThreshold)}
                    <img src={sadImg} height="16px" alt=""/>
                </div>
            </Tooltip>
        </div>
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
                        declineViewCivsById={declineViewCivsById} myGamePlayer={myGamePlayer}/>
                    })}
            </>}
            {turnNum > 2 && <div className="unhappiness-threshold previous-threshold">
                <Tooltip title={`This turn's threshold: ${previousUnhappinessThreshold?.toFixed(2)}`}>
                    <div className="unhappiness-threshold-content">
                        {Math.floor(previousUnhappinessThreshold)}
                        <img src={sadImg} height="16px" alt=""/>
                    </div>
                </Tooltip>
            </div>}
            {turnNum > 1 && newUnhappinessThresholdHigher && unhappinesThresholdObject}
        </div><div className="revolt-cities" style={{minHeight: newUnhappinessThresholdHigher ? "" : "30px"}}>
            {citiesRevoltingNextTurn.length > 0 && <>
                {citiesRevoltingNextTurn.sort((a, b) => b.unhappiness + b.projected_income.unhappiness - a.unhappiness - a.projected_income.unhappiness).map((city, index) => {
                    return <Tooltip title="Your city will be revolting next turn">
                    <div className="decline-option-row future-revolting"
                    style={{
                        backgroundColor: templates.CIVS[myCiv.name]?.primary_color, 
                        borderColor: templates.CIVS[myCiv.name]?.secondary_color}}
                    >
                    <div className="revolt-cities-row">
                        <TextOnIcon image={workerImg} style={{width: "20px", height: "20px", marginLeft: "40px"}}>
                            <b>{city.population}</b>
                        </TextOnIcon>
                        {city.name}
                        <div className="my-city-revolting"
                                        style={{
                                            backgroundColor: templates.CIVS[myCiv.name]?.primary_color, 
                                            borderColor: templates.CIVS[myCiv.name]?.secondary_color}}
                                    >
                                !
                        </div>
                    </div>
                </div></Tooltip>
                })}
            </>}
            {turnNum > 1 && !newUnhappinessThresholdHigher && unhappinesThresholdObject}
        </div>
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

const ScoreDisplay = ({ myGamePlayer, gameEndScore, gameState }) => {
    const [civId, setCivId] = useState("Total");
    const score = myGamePlayer?.score;
    const playerScoreDict = myGamePlayer?.score_dict;
    const myCivIds = myGamePlayer?.all_civ_ids;
    const activeScoreDict = civId === "Total" ? playerScoreDict : gameState.civs_by_id[civId].score_dict;
    return <CivDetailPanel icon={vpImg} title='score' bignum={score} iconTooltip={`${gameEndScore} points to win`}>
        {myCivIds.length > 1 && <FormControl style={{marginTop: '10px'}}>
            <InputLabel id="select-civ-label">Select Civilization</InputLabel>
            <Select
                labelId="select-civ-label"
                id="select-civ"
                value={civId}
                label="Select Civilization"
                onChange={(event) => setCivId(event.target.value)}
                autoWidth
                sx={{
                    '.MuiSelect-select': {
                        paddingTop: '5px',
                        paddingBottom: '5px',
                        paddingLeft: '10px',
                        paddingRight: '10px'
                    }
                }}
            >
                <MenuItem value="Total">Total ({score})</MenuItem>
                {[...myCivIds].reverse().map((civId) => {
                    const civ = gameState.civs_by_id[civId];
                    const totalScore = Object.values(civ.score_dict).reduce((acc, current) => acc + current, 0);
                    return <MenuItem key={civId} value={civId}>{civ.name} ({totalScore})</MenuItem>
                })}
            </Select>
        </FormControl>}
        <Grid container direction="column" spacing={0}>
            <Grid item>
                <TableContainer>
                    <Table size="small">
                        <TableBody>
                            {Object.entries(playerScoreDict).sort((a, b) => b[1] - a[1]).map(([label, score]) => (
                                <TableRow key={label} style={{ borderBottom: 'none' }}>
                                    <TableCell align="right" style={{ border: 'none', padding: '2px 0px' }}>{activeScoreDict[label] ? activeScoreDict[label] : '-'}</TableCell>
                                    <TableCell style={{ border: 'none', padding: '2px 2px 2px 10px' }}>{label}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </Grid>
        </Grid>
    </CivDetailPanel>
}

const ScienceDisplay = ({civ, myCities, templates, setTechListDialogOpen, setTechChoiceDialogOpen, setHoveredTech, disableUI}) => {
    const tech = templates.TECHS[civ.researching_tech_name];
    const techCost = tech?.name  === "Renaissance" ? civ.renaissance_cost : tech?.cost;
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
    turnNum, setDeclineOptionsView, declineViewGameState, setSelectedCity, setHoveredCiv, setHoveredWonder, civsById, declineViewCivsById}) => {
    return (
        <div className="upper-right-display">
            {mainGameState && <WonderListDisplay wonders_by_age={mainGameState?.wonders_by_age} game_age={mainGameState?.advancement_level} available_wonders={mainGameState?.available_wonders} templates={templates} setHoveredWonder={setHoveredWonder}
            vp_chunks_left_by_age={mainGameState?.wonder_vp_chunks_left_by_age} vp_chunks_total_per_age={mainGameState?.vp_chunks_total_per_age}
            />}
            {myCiv && <ScienceDisplay civ={myCiv} myCities={myCities} setTechListDialogOpen={setTechListDialogOpen} setTechChoiceDialogOpen={setTechChoiceDialogOpen} setHoveredTech={setHoveredTech} templates={templates} disableUI={disableUI}/>}
            {myCiv && <CityPowerDisplay civ={myCiv} myCities={myCities} templates={templates} toggleFoundingCity={toggleFoundingCity} canFoundCity={canFoundCity} isFoundingCity={isFoundingCity} disableUI={disableUI}/>}
            {myCiv && <CivVitalityDisplay playerNum={myGamePlayer?.player_num} myCiv={myCiv} myGamePlayer={myGamePlayer} turnNum={turnNum}
                disableUI={disableUI} centerMap={centerMap} declineOptionsView={declineOptionsView} setDeclineOptionsView={setDeclineOptionsView} 
                declineViewGameState={declineViewGameState} mainGameState={mainGameState} templates={templates}
                setSelectedCity={setSelectedCity} setHoveredCiv={setHoveredCiv} setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding}
                declineViewCivsById={declineViewCivsById}/>}
            {myGamePlayer?.score > 0 && <ScoreDisplay myGamePlayer={myGamePlayer} gameEndScore={mainGameState.game_end_score} gameState={mainGameState}/>}
        </div>
    );
};

export default UpperRightDisplay;