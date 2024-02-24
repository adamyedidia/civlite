import React from 'react';
import './UpperRightDisplay.css';
import CityDisplay from './CityDisplay';
import { Grid, Typography } from '@mui/material';
import Timer from './Timer';
import { CityDetailPanel } from './CityDetailPanel';
import foodImg from './images/food.png';
import scienceImg from './images/science.png';
import ProgressBar from './ProgressBar';
import { Button } from '@mui/material';
import { TextOnIcon } from './TextOnIcon';

const CivDetailPanel = ({title, icon, income, children}) => {
    return (
        <div className={`civ-detail-panel ${title}-area`}>
            <div className="icon">
                <img src={icon}></img>
                <span>+{Math.floor(income)}</span>
            </div>
            <div className="panel-content">
                {children}
            </div>
        </div>
    );
}

const NewCityIcon = ({  civTemplate, size, children}) => {
    return <div className="new-city-icon" style={{height: size, width:size, backgroundColor: civTemplate.primary_color, borderColor: civTemplate.secondary_color}}> {children} </div>
}

const CityPowerDisplay = ({ civ, civTemplates }) => {
    const cityPowerCost = 100; // TODO is this const already defined somewhere?
    const storedProgress = (civ.city_power % cityPowerCost) / cityPowerCost * 100;
    const incomeProgress = civ.projected_city_power_income / cityPowerCost * 100;
    const newCitites = Math.floor(civ.city_power / cityPowerCost);
    const civTemplate = civTemplates[civ.name];

    return <CivDetailPanel icon={foodImg} title='food' income={civ.projected_city_power_income}>
        <div className="city-power-new-cities">
            {[...Array(newCitites)].map((_, index) => (
                <NewCityIcon key={index} civTemplate={civTemplate}>+</NewCityIcon>
            ))}
        </div>
        <ProgressBar darkPercent={storedProgress} lightPercent={incomeProgress} barText={`${Math.floor(civ.city_power % cityPowerCost)} / ${cityPowerCost}`}/>
    </CivDetailPanel>
};

const CivVitalityDisplay = ({ civVitality, turnNum }) => {
    const percentage = (civVitality * 100).toFixed(1);
    const newCivPercentage = ((2.0 + turnNum * 0.1) * 100).toFixed(1);
    return (
        <div className="civ-vitality-display">
            <p>Civ vitality: {percentage}% (New civ vitality: {newCivPercentage}%)</p>
        </div>
    );
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

const ScienceDisplay = ({civ, techTemplates, setTechListDialogOpen, setHoveredTech}) => {
    const tech = civ.tech_queue?.[0];
    const storedProgress = tech ? civ.science / tech.cost * 100 : 0;
    const incomeProgress = tech ? civ.projected_science_income / tech.cost * 100 : 0;
    return <CivDetailPanel title='science' icon={scienceImg} income={civ.projected_science_income}>
        <h2 className="tech-name" 
            onMouseEnter={tech ? () => setHoveredTech(techTemplates[tech.name]) : () => {}}
            onMouseLeave={() => setHoveredTech(null)}  
        > {tech?.name} </h2>
        <ProgressBar darkPercent={storedProgress} lightPercent={incomeProgress} barText={tech ? `${Math.floor(civ.science)} / ${tech.cost}` : `${Math.floor(civ.science)} / ???`}/>
        <Button variant="contained" color="primary" onClick={() => setTechListDialogOpen(true)}>
            Researched
        </Button>
        <Button variant="contained" color="primary" onClick={() => {
            alert(`Haha nice try, this isn't implemented yet. You're stuck with ${tech.name}.`);
        }}>
            Change
        </Button>
    </CivDetailPanel>
}

const UpperRightDisplay = ({ city, isFriendlyCity, unitTemplates, civTemplates, setHoveredUnit, setHoveredBuilding, setHoveredTech, techTemplates, myCiv, myGamePlayer, announcements, setTechListDialogOpen, turnNum, nextForcedRollAt, gameId, timerMuted }) => {
    return (
        <div className="upper-right-display">
            {nextForcedRollAt && !timerMuted && <Timer nextForcedRollAt={nextForcedRollAt} gameId={gameId}/>}
            {city && !isFriendlyCity && <CityDisplay city={city} setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding} isFriendly={isFriendlyCity} unitTemplates={unitTemplates}/>}
            {myCiv && <ScienceDisplay civ={myCiv} setTechListDialogOpen={setTechListDialogOpen} setHoveredTech={setHoveredTech} techTemplates={techTemplates}/>}
            {myCiv && <CityPowerDisplay civ={myCiv} civTemplates={civTemplates} />}
            {myCiv && <CivVitalityDisplay civVitality={myCiv.vitality} turnNum={turnNum} />}
            {myGamePlayer && <ScoreDisplay myGamePlayer={myGamePlayer} />}
            {announcements.length > 0 && <AnnouncementsDisplay announcements={announcements} />}
        </div>
    );
};

export default UpperRightDisplay;