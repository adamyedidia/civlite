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
import cityImg from './images/city.png';
import workerImg from './images/worker.png';
import ProgressBar from './ProgressBar';
import { Button } from '@mui/material';
import { TextOnIcon } from './TextOnIcon.js';
import { IconUnitDisplay } from './UnitDisplay.js';
import { BriefBuildingDisplay } from './BuildingDisplay.js';

const CivDetailPanel = ({title, icon, bignum, children}) => {
    const bignumCharLen = bignum.length;
    return (
        <div className={`civ-detail-panel ${title}-area`}>
            <div className="icon">
                <img src={icon}></img>
                <span className={bignumCharLen > 3 ? "small-font" : ""}>{bignum}</span>
            </div>
            <div className="panel-content">
                {children}
            </div>
        </div>
    );
}

const NewCityIcon = ({  civTemplate, size, disabled, children}) => {
    return <div className="new-city-icon" style={{height: size, width:size, backgroundColor: disabled? "#aaa" : civTemplate.primary_color, borderColor: disabled? "#888" : civTemplate.secondary_color}}> {children} </div>
}

const CityPowerDisplay = ({ civ, civTemplates, toggleFoundingCity, canFoundCity, isFoundingCity, disableUI}) => {
    const cityPowerCost = 100; // TODO is this const already defined somewhere?
    const storedProgress = (civ.city_power % cityPowerCost) / cityPowerCost * 100;
    const incomeProgress = civ.projected_city_power_income / cityPowerCost * 100;
    const newCities = Math.floor(civ.city_power / cityPowerCost);
    const civTemplate = civTemplates[civ.name];

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

    return <CivDetailPanel icon={cityImg} title='food' bignum={`+${Math.floor(civ.projected_city_power_income)}`}>
        <div className={`city-power-new-cities`} onMouseOver={showTooltip} onMouseOut={hideTooltip}>
            {[...Array(newCities)].map((_, index) => (
                <div key={index} className={`new-city-button ${(canFoundCity && index==0) ? (isFoundingCity ? 'active': 'enabled'): ''}`} onClick={disableUI? null :toggleFoundingCity}>
                    <NewCityIcon civTemplate={civTemplate} disabled={!canFoundCity || (isFoundingCity & index > 0)}>
                        +
                    </NewCityIcon>
                </div>
            ))}
            <div ref={tooltipRef} className="tooltip">
                {newCities == 0  &&  "Gather City Power to build new cities"}
                {newCities > 0 && !canFoundCity && "No Valid City Sites"}
                {newCities > 0 && canFoundCity && !isFoundingCity && "Click to found city"}
                {newCities > 0 && canFoundCity && isFoundingCity && "Click to cancel found city"}
            </div>
        </div>
        <ProgressBar darkPercent={storedProgress} lightPercent={incomeProgress} barText={`${Math.floor(civ.city_power % cityPowerCost)} / ${cityPowerCost}`}/>
    </CivDetailPanel>
};

const CivVitalityDisplay = ({ civVitality, turnNum, setConfirmEnterDecline, disableUI, toggleDeclineView, declineViewGameState, 
    unitTemplates, civTemplates, buildingTemplates,
    setSelectedCity, setHoveredCiv, setHoveredUnit, setHoveredBuilding}) => {
    const newCivPercentage = Math.round((2.0 + turnNum * 0.1) * 100);


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

    const citiesReadyForRevolt = Object.values(declineViewGameState?.cities_by_id || {}).filter(city => city.capital && city.civ.game_player === null);
    return <CivDetailPanel icon={vitalityImg} title='vitality' bignum={`${Math.round(civVitality * 100)}%`}>
        <Button className="toggle-decline-view" 
            onClick={toggleDeclineView}
            variant="contained" 
            color="primary"
        >
            Toggle Decline View
        </Button>
        <div className="revolt-cities">
            {citiesReadyForRevolt.length > 0 && <>
                {citiesReadyForRevolt.map((city, index) => {
                    // TODO this should be its own named element thingy.
                    return <div key={index} className="revolt-cities-city"
                        style={{backgroundColor: civTemplates[city.civ.name].primary_color, borderColor: civTemplates[city.civ.name].secondary_color}}
                        onClick = {() => {
                            toggleDeclineView();
                            setSelectedCity(city);
                            // TODO centerMap(city.hex);
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
                            <TextOnIcon image={workerImg} style={{width: "20px", marginLeft: "40px"}}>{city.population}</TextOnIcon>
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
                    })}
            </>}
        </div>
    </CivDetailPanel>
}

const ScoreDisplay = ({ myGamePlayer }) => {
    const score = myGamePlayer?.score;
    return <CivDetailPanel icon={vpImg} title='score' bignum={score}>
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
                    {myGamePlayer?.sfrc || 0} revolting cities
                </Typography>
            </Grid>                                                                     
        </Grid>
    </CivDetailPanel>
}

const ScienceDisplay = ({civ, techTemplates, setTechListDialogOpen, setTechChoices, setHoveredTech, disableUI}) => {
    const tech = techTemplates[civ.researching_tech_name];
    const techCost = tech?.name  == "Renaissance" ? civ.renaissance_cost : tech?.cost;
    const storedProgress = tech ? civ.science / techCost * 100 : 0;
    const incomeProgress = tech ? civ.projected_science_income / techCost * 100 : 0;
    return <CivDetailPanel title='science' icon={scienceImg} bignum={`+${Math.floor(civ.projected_science_income)}`}>
        <h2 className="tech-name" 
            onMouseEnter={tech ? () => setHoveredTech(techTemplates[tech.name]) : () => {}}
            onMouseLeave={() => setHoveredTech(null)}  
        > {romanNumeral(tech?.advancement_level)}. {tech?.name} </h2>
        <ProgressBar darkPercent={storedProgress} lightPercent={incomeProgress} barText={tech ? `${Math.floor(civ.science)} / ${techCost}` : `${Math.floor(civ.science)} / ???`}/>
        <Button variant="contained" color="primary" onClick={() => setTechListDialogOpen(true)}>
            Tech Tree
        </Button>
        <Button variant="contained" color="primary" disabled={disableUI} onClick={() => {
            setTechChoices(civ.current_tech_choices);
        }}>
            Change
        </Button>
    </CivDetailPanel>
}

const UpperRightDisplay = ({ canFoundCity, isFoundingCity, disableUI, 
    civTemplates, unitTemplates, buildingTemplates,
    setConfirmEnterDecline, setTechChoices, setHoveredUnit, setHoveredBuilding, setHoveredTech, 
    toggleFoundingCity, techTemplates, myCiv, myGamePlayer, setTechListDialogOpen, 
    turnNum, toggleDeclineView, declineViewGameState, setSelectedCity, setHoveredCiv}) => {
    return (
        <div className="upper-right-display">
            {myCiv && <ScienceDisplay civ={myCiv} setTechListDialogOpen={setTechListDialogOpen} setTechChoices={setTechChoices} setHoveredTech={setHoveredTech} techTemplates={techTemplates} disableUI={disableUI}/>}
            {myCiv && <CityPowerDisplay civ={myCiv} civTemplates={civTemplates} toggleFoundingCity={toggleFoundingCity} canFoundCity={canFoundCity} isFoundingCity={isFoundingCity} disableUI={disableUI}/>}
            {myCiv && <CivVitalityDisplay civVitality={myCiv.vitality} turnNum={turnNum} setConfirmEnterDecline={setConfirmEnterDecline} disableUI={disableUI} toggleDeclineView={toggleDeclineView} declineViewGameState={declineViewGameState} civTemplates={civTemplates} unitTemplates={unitTemplates} buildingTemplates={buildingTemplates} setSelectedCity={setSelectedCity} setHoveredCiv={setHoveredCiv} setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding}/>}
            {myGamePlayer && <ScoreDisplay myGamePlayer={myGamePlayer} />}
        </div>
    );
};

export default UpperRightDisplay;