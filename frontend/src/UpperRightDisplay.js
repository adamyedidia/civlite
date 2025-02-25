import React, { useState } from 'react';
import './UpperRightDisplay.css';
import { Grid, Table, TableBody, TableRow, TableCell, TableContainer, MenuItem, FormControl, InputLabel, Select, Tooltip } from '@mui/material';
import { romanNumeral } from "./romanNumeral.js";
import scienceImg from './images/science.png';
import metalImg from './images/metal.png';
import woodImg from './images/wood.png';
import vitalityImg from './images/heart.png';
import vpImg from './images/crown.png';
import sadImg from './images/sadface.png';
import cityImg from './images/city.png';
import workerImg from './images/worker.png';
import workerDarkImg from './images/worker_darkmode.png';
import wonderImg from './images/wonders.png';
import ideologyImg from './images/ideology.png';
import fireImg from './images/fire.svg';
import greatPersonImg from './images/greatperson.png';
import ProgressBar from './ProgressBar';
import { Button } from '@mui/material';
import { TextOnIcon } from './TextOnIcon.js';
import { IconUnitDisplay } from './UnitDisplay.js';
import { YieldsDisplay } from './BuildingDisplay.js';
import { DetailedNumberTooltipContent } from './DetailedNumber.js';
import TradeHubIcon from './TradeHubIcon.js';
import { IDEOLOGY_LEVEL_STRINGS } from "./ideologyLevelStrings";

const CivDetailPanel = ({title, icon, iconTooltip, bignum, children}) => {
    const bignumCharLen = bignum.length;
    return (
        <div className={`civ-detail-panel ${title}-area`}>
            <Tooltip title={iconTooltip}>
                <div className="icon">
                    <img src={icon} alt=""></img>
                    <span className={bignumCharLen > 3 ? "small-font" : ""}>{bignum}</span>
                </div>
            </Tooltip>
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
    const storedProgress = (Math.max(0, civ.city_power) % cityPowerCost) / cityPowerCost * 100;
    const incomeProgress = (civ.projected_city_power_income.value + Math.min(0, civ.city_power)) / cityPowerCost * 100;
    const newCities = Math.max(0, Math.floor(civ.city_power / cityPowerCost));
    const civTemplate = templates.CIVS[civ.name];
    const currentTerritories = myCities.filter(city => !city.territory_parent_id).length;
    const atMaxTerritories = currentTerritories === civ.max_territories;
    
    return <CivDetailPanel icon={cityImg} title='food' bignum={`+${Math.floor(civ.projected_city_power_income.value)}`}
        iconTooltip={<DetailedNumberTooltipContent detailedNumber={civ.projected_city_power_income} />}
    >
        <div className='city-power-top-row'>
        <Tooltip title={newCities === 0  ?  "Gather City Power to build new cities" :
                newCities > 0 && !canFoundCity ? "No Valid City Sites" :
                newCities > 0 && canFoundCity && !isFoundingCity ? "Click to found city" :
                newCities > 0 && canFoundCity && isFoundingCity ? "Click to cancel found city" : null}>
        <div className={`city-power-new-cities`}>
            {[...Array(newCities)].map((_, index) => (
                <div key={index} className={`new-city-button ${(canFoundCity && index===0) ? (isFoundingCity ? 'active': 'enabled'): ''}`} onClick={disableUI? null :toggleFoundingCity}>
                    <NewCityIcon civTemplate={civTemplate} disabled={!canFoundCity || (isFoundingCity & index > 0)} atMaxTerritories={atMaxTerritories}>
                        <div style={{color: civTemplate.darkmode && !(!canFoundCity || (isFoundingCity & index > 0)) ? "white" : "black"}}>
                            +
                        </div>
                    </NewCityIcon>
                </div>
            ))}
        </div>
        </Tooltip>
        <Tooltip title="Current / max territories">
            <div className='city-power-territories' style={{
                backgroundColor: civTemplate.primary_color,
                borderColor: civTemplate.secondary_color,
                color: civTemplate.darkmode ? "white" : "black"
            }}>
                {currentTerritories}/{civ.max_territories}
            </div>
        </Tooltip>
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
                <div style={{color: civTemplate?.darkmode ? "white" : "black"}}>
                    {Math.floor(city.revolting_starting_vitality * 100 * myGamePlayer.vitality_multiplier)}%
                </div>
            </TextOnIcon>
            <TextOnIcon image={civTemplate?.darkmode ? workerDarkImg : workerImg} style={{width: "20px", height: "20px", marginLeft: "40px"}}>
                <div style={{color: civTemplate?.darkmode ? "white" : "black"}}>
                    <b>{city.population}</b>
                </div>
            </TextOnIcon>
            <div className="unit-count" style={{visibility: city.revolt_unit_count > 0 ? "visible" : "hidden", border: civTemplate?.darkmode ? "2px solid white" : "2px solid black"}}>
                <div style={{color: civTemplate?.darkmode ? "white" : "black"}}>
                    {city.revolt_unit_count}
                </div>
            </div>
            <div style={{color: civTemplate?.darkmode ? "white" : "black"}}>
                {city.name}
            </div>
            {isMyCity && <div className="my-city-revolting"
                            style={{
                                backgroundColor: templates.CIVS[myCiv.name]?.primary_color, 
                                borderColor: templates.CIVS[myCiv.name]?.secondary_color}}
                        >
                <Tooltip title="Your city">
                    <div style={{color: templates.CIVS[myCiv.name]?.darkmode ? "white" : "black"}}>
                        !!
                    </div>
                </Tooltip>
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
        {25 < distanceFromWin && distanceFromWin < 50 && <Tooltip title="Another player is within 50 points of winning. Declining may let them win.">
            <div className="distance-from-win">
                GAME WILL END SOON
            </div>
        </Tooltip>}
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
            {turnNum > 2 && <div className="unhappiness-threshold previous-threshold" style={{bottom: (newUnhappinessThresholdHigher && citiesReadyForRevolt.length == 5) ? "-40px" : ""}}>
                <Tooltip title={`This turn's threshold: ${previousUnhappinessThreshold?.toFixed(2)}`}>
                    <div className="unhappiness-threshold-content">
                        {Math.floor(previousUnhappinessThreshold)}
                        <img src={sadImg} height="16px" alt=""/>
                    </div>
                </Tooltip>
            </div>}
            {turnNum > 1 && newUnhappinessThresholdHigher && unhappinesThresholdObject}
        </div><div className="revolt-cities" style={{minHeight: (newUnhappinessThresholdHigher && citiesReadyForRevolt.length > 5) ? "" : "30px"}}>
            {citiesRevoltingNextTurn.length > 0 && <>
                {citiesRevoltingNextTurn.sort((a, b) => b.unhappiness + b.projected_income.unhappiness - a.unhappiness - a.projected_income.unhappiness).map((city, index) => {
                    const cityCivTemplate = templates.CIVS[city.civ_id];
                    return <Tooltip title="Your city will be revolting next turn">
                    <div className="decline-option-row future-revolting"
                    style={{
                        backgroundColor: templates.CIVS[myCiv.name]?.primary_color, 
                        borderColor: templates.CIVS[myCiv.name]?.secondary_color}}
                    >
                    <div className="revolt-cities-row">
                        <TextOnIcon image={cityCivTemplate?.darkmode ? workerDarkImg : workerImg} style={{width: "20px", height: "20px", marginLeft: "40px"}}>
                            <div style={{color: cityCivTemplate?.darkmode ? "white" : "black"}}>
                                <b>{city.population}</b>
                            </div>
                        </TextOnIcon>
                        <div style={{color: cityCivTemplate?.darkmode ? "white" : "black"}}>
                            {city.name}
                        </div>
                        <div className="my-city-revolting"
                                        style={{
                                            backgroundColor: templates.CIVS[myCiv.name]?.primary_color, 
                                            borderColor: templates.CIVS[myCiv.name]?.secondary_color}}
                                    >
                                        <div style={{color: templates.CIVS[myCiv.name]?.darkmode ? "white" : "black"}}>
                                    !
                                </div>
                        </div>
                    </div>
                </div></Tooltip>
                })}
            </>}
            {turnNum > 1 && !newUnhappinessThresholdHigher && unhappinesThresholdObject}
        </div>
    </>
    if (0 < distanceFromWin && distanceFromWin <= 25 && !declineOptionsView) {
        content = <Tooltip title="Another player is within 25 points of winning. Declining now would let them win instantly.">
        <div className="distance-from-win">
            <div>GAME WILL END SOON</div>
            <div className="distance-from-win-warning">
                DECLINE IMPOSSIBLE
            </div>
        </div>
        </Tooltip>
    }
    const iconTooltip = <>
        Losing {(myCiv.vitality_decay_rate.value*100).toFixed(0)}% of our vitality per turn:
        <DetailedNumberTooltipContent detailedNumber={myCiv.vitality_decay_rate}/>
    </>
    return <CivDetailPanel icon={vitalityImg} iconTooltip={iconTooltip} title='vitality' bignum={`${Math.round(myCiv.vitality * 100)}%`}>
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
    const techCost = tech?.cost;
    const storedProgress = tech ? civ.science / techCost * 100 : 0;
    const incomeProgress = tech ? civ.projected_science_income.value / techCost * 100 : 0;
    return <CivDetailPanel title='science' icon={scienceImg} iconTooltip={<DetailedNumberTooltipContent detailedNumber={civ.projected_science_income}/>} bignum={`+${Math.floor(civ.projected_science_income.value)}`}>
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

const A2TenetIcon = ({tenetName}) => {
    const img = tenetName === "Rise of Equality" ? cityImg : tenetName === "Promise of Freedom" ? vpImg : tenetName === "Glorious Order" ? sadImg : tenetName === "Hymn of Unity" ? fireImg : "";
    return <img src={img} alt={tenetName} height="20px"/>
}

const IdeologyLevelDisplay = ({lvl, tenets, myPlayerNum, myCiv, templates, setHoveredTenet}) => {
    const opponentTenets = tenets.filter(tenet => tenet.player_num !== myPlayerNum);
    return <div className={`level ${lvl > myCiv.advancement_level ? 'active' : ''}`}>
        <div style={{width: "30px"}}>{romanNumeral(lvl)}</div>
        {myCiv.advancement_level === lvl && <span>★</span>}
        {opponentTenets.map((tenet, index) => (
            <div key={index} className={`tenet-marker ${lvl <= myCiv.advancement_level ? 'inactive' : 'active'}`} onMouseEnter={() => setHoveredTenet(templates.TENETS[tenet.tenet])} onMouseLeave={() => setHoveredTenet(null)}>
                <A2TenetIcon tenetName={tenet.tenet}/>
            </div>
        ))}
    </div>
}

const TenetDisplay = ({myTenets, level, setHoveredTenet, className, headerStyle, children}) => {
    const myTenet = myTenets[level];
    const content = <div 
        className={`tenet ${className} ${myTenet ? 'active' : 'inactive'}`} 
        onMouseEnter={myTenet ? () => setHoveredTenet(myTenets[level]) : null} 
        onMouseLeave={myTenet ? () => setHoveredTenet(null) : null}>
            <div className="tenet-header" style={myTenet && headerStyle}>{IDEOLOGY_LEVEL_STRINGS[level].header}</div>
            {myTenet ? children : null}
        </div>
    if (!myTenet) {
        return <Tooltip title={`We will choose our ${IDEOLOGY_LEVEL_STRINGS[level].header} in age ${level}.`}>
            {content}
        </Tooltip>
    }
    return content;
}

const IdeologyDisplay = ({myCiv, myGamePlayer, gameState, templates, setIdeologyTreeOpen, setHoveredTenet}) => {
    const levelMarkers = gameState?.advancement_level_tenets_display
    let levelsToDisplay = [...new Set(levelMarkers.map(marker => marker.advancement_level))];
    if (!levelsToDisplay.includes(myCiv.advancement_level)) {
        levelsToDisplay.push(myCiv.advancement_level);
    }
    levelsToDisplay.sort((a, b) => b - a);
    const numTenets = Object.keys(myGamePlayer.tenets).length;

    const myTenetTemplates = Object.keys(myGamePlayer.tenets).map(tenet => templates.TENETS[tenet]);
    myTenetTemplates.sort((a, b) => a.advancement_level - b.advancement_level);
    // Now they are zero-indexed; push a blank one on the front so the indexing is level
    myTenetTemplates.unshift({});
    
    const myA4TenetName = myTenetTemplates[4]?.name;
    const myA5TenetName = myTenetTemplates[5]?.name;
    const a5TenetIcon = myA5TenetName === 'Dragons' ? '/images/archer.svg' : myA5TenetName === 'Giants' ? '/images/cannon.svg' : myA5TenetName === 'Unicorns' ? '/images/horseman.svg' : myA5TenetName === 'Ninjas' ? '/images/swordsman.svg' : null;

    return <CivDetailPanel title='ideology' icon={ideologyImg} iconTooltip="Ideology" bignum="">
        <Button variant="contained" color="primary" onClick={() => setIdeologyTreeOpen(true)}>
            Ideologies
        </Button>
        <div className='ideology-columns'>
            <div className="ideology-column" style={{width: '45%'}}>
                <TenetDisplay myTenets={myTenetTemplates} level={2} setHoveredTenet={setHoveredTenet}>
                    <Tooltip title="The ages and Aspiration of each player are shown here. Players ahead of you are gaining their Aspiration effect against you.">
                        <div className="level-markers">
                            {levelsToDisplay.map((lvl, index) => {
                                const tenets = levelMarkers.filter(marker => marker.advancement_level === lvl);
                                return <IdeologyLevelDisplay key={index} lvl={lvl} tenets={tenets} myPlayerNum={myGamePlayer?.player_num} myCiv={myCiv} templates={templates} setHoveredTenet={setHoveredTenet}/>
                            })}
                        </div>
                    </Tooltip>
                </TenetDisplay>
            </div>
            <div className="ideology-column" style={{width: '55%'}}>
                <TenetDisplay myTenets={myTenetTemplates} level={3} setHoveredTenet={setHoveredTenet} className={myGamePlayer.tenet_quest.progress >= myGamePlayer.tenet_quest.target ? "one-row-tenet" : ""}>
                    <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
                        {myGamePlayer.tenet_quest.progress < myGamePlayer.tenet_quest.target ?
                            <>
                                <div>{myGamePlayer.tenet_quest.name}</div>
                                <div className="quest-progress">{myGamePlayer.tenet_quest.progress}/{myGamePlayer.tenet_quest.target}</div>
                            </>
                            :
                            <div className="quest-complete">
                                {myGamePlayer.tenet_quest.name == "Holy Grail" ? <>
                                    <img src={greatPersonImg} alt="holy grail" height="20px"/>
                                    x2
                                </> : myGamePlayer.tenet_quest.name == "El Dorado" ? <>
                                    <div style={{width: '32px', height: '24px', background: 'linear-gradient(to right, #bbbbbb 50%, #e08b5e 50%)', border: '2px solid black', borderRadius: '5px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '4px'}}>
                                        <img src={metalImg} alt="metal" height="8px"/>
                                        <img src={woodImg} alt="science" height="10px"/>
                                    </div>                                    
                                </> : myGamePlayer.tenet_quest.name == "Yggdrasils Seeds" ? <>
                                    <div style={{width: '24px', height: '12px', backgroundColor: 'grey', border: '2px solid black', fontSize: '10px', textAlign: 'center'}}>
                                        ++
                                    </div>
                                </> : myGamePlayer.tenet_quest.name == "Fountain of Youth" ? <>
                                    <TextOnIcon image={vitalityImg} alt="fountain of youth" style={{width: '20px', height: '20px'}} offset="-5px">
                                        +
                                    </TextOnIcon>
                                </> : "ERROR"
                                }
                            </div>
                        }
                    </div>
                </TenetDisplay>
                <TenetDisplay myTenets={myTenetTemplates} level={4} setHoveredTenet={setHoveredTenet} className="one-row-tenet">
                    <img src={vpImg} alt="vp" height="20px"/>
                    /
                    {myA4TenetName == "Honor" ? 
                    <div style={{
                        width: '0',
                        height: '0',
                        borderLeft: '10px solid transparent',
                        borderRight: '10px solid transparent',
                        borderBottom: '20px solid #ac3737',
                        display: 'inline-block'
                    }}/>
                    : <img src={myA4TenetName == "Faith" ? wonderImg : myA4TenetName == "Rationalism" ? scienceImg : myA4TenetName == "Community" ? cityImg : "ERROR"} alt={myA4TenetName} height="20px"/>
                    }
                </TenetDisplay>
                <TenetDisplay myTenets={myTenetTemplates} level={5} setHoveredTenet={setHoveredTenet} className="one-row-tenet">
                        <img src={cityImg} alt="city" height="20px"/>
                        /
                        <img src={a5TenetIcon} alt={myA5TenetName} height="20px"/>
                </TenetDisplay>
            </div>
        </div>
        <TenetDisplay myTenets={myTenetTemplates} level={7} setHoveredTenet={setHoveredTenet} className="one-row-tenet" headerStyle={{width: '80px'}}>
            <TradeHubIcon myGamePlayer={myGamePlayer} style={{width: '25px', height: '25px', borderRadius: '50%', backgroundColor: '#dddddd', padding: '3px'}}/>
        </TenetDisplay>
    </CivDetailPanel>
}
const UpperRightDisplay = ({ mainGameState, canFoundCity, isFoundingCity, disableUI, centerMap, declineOptionsView,
    templates,
    setConfirmEnterDecline, setTechChoiceDialogOpen, setIdeologyTreeOpen, setHoveredUnit, setHoveredBuilding, setHoveredTech, setHoveredTenet,
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
            {myCiv && <IdeologyDisplay myCiv={myCiv} myGamePlayer={myGamePlayer} gameState={mainGameState} templates={templates} setIdeologyTreeOpen={() => {setIdeologyTreeOpen(true); setDeclineOptionsView(false);}} setHoveredTenet={setHoveredTenet}/>}
            {myGamePlayer?.score > 0 && <ScoreDisplay myGamePlayer={myGamePlayer} gameEndScore={mainGameState.game_end_score} gameState={mainGameState}/>}
        </div>
    );
};

export default UpperRightDisplay;