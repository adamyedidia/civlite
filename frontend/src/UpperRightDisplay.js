import React from 'react';
import './UpperRightDisplay.css';
import CityDisplay from './CityDisplay';
import { Grid, Typography } from '@mui/material';
import Timer from './Timer';
import foodImg from './images/food.png';
import scienceImg from './images/science.png';
import vitalityImg from './images/heart.png';
import ProgressBar from './ProgressBar';
import { Button } from '@mui/material';

const CivDetailPanel = ({title, icon, income, children}) => {
    const incomeCharLen = income.length;
    return (
        <div className={`civ-detail-panel ${title}-area`}>
            <div className="icon">
                <img src={icon}></img>
                <span className={incomeCharLen > 3 ? "small-font" : ""}>{income}</span>
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
    const newCitites = Math.floor(civ.city_power / cityPowerCost);
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

    return <CivDetailPanel icon={foodImg} title='food' income={`+${Math.floor(civ.projected_city_power_income)}`}>
        <div className={`city-power-new-cities`} onMouseOver={showTooltip} onMouseOut={hideTooltip}>
            {[...Array(newCitites)].map((_, index) => (
                <div key={index} class={`new-city-button ${(canFoundCity && index==0) ? (isFoundingCity ? 'active': 'enabled'): ''}`} onClick={disableUI? "" :toggleFoundingCity}>
                    <NewCityIcon civTemplate={civTemplate} disabled={!canFoundCity || (isFoundingCity & index > 0)}>
                        +
                    </NewCityIcon>
                </div>
            ))}
            <div ref={tooltipRef} className="tooltip">
                {!canFoundCity && "No Valid City Sites"}
                {canFoundCity && !isFoundingCity && "Click to found city"}
                {canFoundCity && isFoundingCity && "Click to cancel found city"}
            </div>
        </div>
        <ProgressBar darkPercent={storedProgress} lightPercent={incomeProgress} barText={`${Math.floor(civ.city_power % cityPowerCost)} / ${cityPowerCost}`}/>
    </CivDetailPanel>
};

const CivVitalityDisplay = ({ civVitality, turnNum, setConfirmEnterDecline, disableUI }) => {
    const newCivPercentage = Math.round((2.0 + turnNum * 0.1) * 100);
    return <CivDetailPanel icon={vitalityImg} title='vitality' income={`${Math.round(civVitality * 100)}%`}>
        <Button
            color="primary"
            variant="contained"
            width= "100%"
            onClick={() => setConfirmEnterDecline(true)}
            disabled={disableUI}
        >
            <div className="decline-button-content">
                <div className="decline-button-label">Enter decline</div>
                <div className="decline-button-new-vitality">
                    New Civ = {newCivPercentage}%
                    <img src={vitalityImg} height="75%"/>
                </div>
            </div>
        </Button>
    </CivDetailPanel>
}

const ScoreDisplay = ({ myGamePlayer }) => {
    const score = myGamePlayer?.score;
    return (
        <div className="score-display">
            <Grid container direction="column" spacing={0}>
                <Grid item>
                    <Typography variant="h5">You have {score} VPs</Typography>
                </Grid>
                <Grid item>
                    <Typography>
                        {myGamePlayer?.sfku || 0} from killing units
                    </Typography>
                </Grid>
                <Grid item>
                    <Typography>
                        {myGamePlayer?.sfccac || 0} from camp/city captures
                    </Typography>
                </Grid>
                <Grid item>
                    <Typography>
                        {myGamePlayer?.sfrt || 0} from research
                    </Typography>
                </Grid>
                <Grid item>
                    <Typography>
                        {myGamePlayer?.sfbv || 0} from building VP rewards
                    </Typography>
                </Grid>
                <Grid item>
                    <Typography>
                        {myGamePlayer?.sfa || 0} from abilities
                    </Typography>
                </Grid>
                <Grid item>
                    <Typography>
                        {myGamePlayer?.sfs || 0} from survival
                    </Typography>
                </Grid>
                <Grid item>
                    <Typography>
                        {myGamePlayer?.sfrc || 0} from revolting cities
                    </Typography>
                </Grid>                                                                     
            </Grid>
        </div>
    );
}

const AnnouncementsDisplay = ({ announcements }) => {
    return (
      <div className="announcements-display" style={{ maxHeight: '120px', overflowY: 'scroll' }}>
        <Grid container direction="column" spacing={0}>
          {announcements.map((announcement, index) => (
            <Grid item key={index}>
              <Typography>{announcement}</Typography>
            </Grid>
          ))}
        </Grid>
      </div>
    );
  };

const ScienceDisplay = ({civ, techTemplates, setTechListDialogOpen, setHoveredTech, disableUI}) => {
    const tech = civ.tech_queue?.[0];
    const storedProgress = tech ? civ.science / tech.cost * 100 : 0;
    const incomeProgress = tech ? civ.projected_science_income / tech.cost * 100 : 0;
    return <CivDetailPanel title='science' icon={scienceImg} income={`+${Math.floor(civ.projected_science_income)}`}>
        <h2 className="tech-name" 
            onMouseEnter={tech ? () => setHoveredTech(techTemplates[tech.name]) : () => {}}
            onMouseLeave={() => setHoveredTech(null)}  
        > {tech?.name} </h2>
        <ProgressBar darkPercent={storedProgress} lightPercent={incomeProgress} barText={tech ? `${Math.floor(civ.science)} / ${tech.cost}` : `${Math.floor(civ.science)} / ???`}/>
        <Button variant="contained" color="primary" onClick={() => setTechListDialogOpen(true)}>
            Researched
        </Button>
        <Button variant="contained" color="primary" disabled={disableUI} onClick={() => {
            alert(`Haha nice try, this isn't implemented yet. You're stuck with ${tech.name}.`);
        }}>
            Change
        </Button>
    </CivDetailPanel>
}

const UpperRightDisplay = ({ city, isFriendlyCity, canFoundCity, isFoundingCity, disableUI, unitTemplates, civTemplates, setConfirmEnterDecline, setHoveredUnit, setHoveredBuilding, setHoveredTech, toggleFoundingCity, techTemplates, myCiv, myGamePlayer, announcements, setTechListDialogOpen, turnNum, nextForcedRollAt, gameId, timerMuted }) => {
    return (
        <div className="upper-right-display">
            {nextForcedRollAt && !timerMuted && <Timer nextForcedRollAt={nextForcedRollAt} gameId={gameId}/>}
            {myCiv && <ScienceDisplay civ={myCiv} setTechListDialogOpen={setTechListDialogOpen} setHoveredTech={setHoveredTech} techTemplates={techTemplates} disableUI={disableUI}/>}
            {myCiv && <CityPowerDisplay civ={myCiv} civTemplates={civTemplates} toggleFoundingCity={toggleFoundingCity} canFoundCity={canFoundCity} isFoundingCity={isFoundingCity} disableUI={disableUI}/>}
            {myCiv && <CivVitalityDisplay civVitality={myCiv.vitality} turnNum={turnNum} setConfirmEnterDecline={setConfirmEnterDecline} disableUI={disableUI}/>}
            {myGamePlayer && <ScoreDisplay myGamePlayer={myGamePlayer} />}
            {announcements.length > 0 && <AnnouncementsDisplay announcements={announcements} />}
            {city && !isFriendlyCity && <CityDisplay city={city} setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding} isFriendly={isFriendlyCity} unitTemplates={unitTemplates}/>}
        </div>
    );
};

export default UpperRightDisplay;