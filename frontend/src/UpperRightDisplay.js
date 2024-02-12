import React from 'react';
import './UpperRightDisplay.css';
import CityDisplay from './CityDisplay';
import { BriefTechDisplay } from './TechDisplay';
import { Grid, Typography } from '@mui/material';

const CityPowerDisplay = ({ myCiv }) => {
    return (
        <div className="city-power-display">
            <p>City power: {myCiv?.city_power?.toFixed(1)} (+{myCiv?.projected_city_power_income?.toFixed(1)})</p>
        </div>
    );
};

const CivVitalityDisplay = ({ civVitality }) => {
    const percentage = (civVitality * 100).toFixed(1);
    return (
        <div className="civ-vitality-display">
            <p>Civ vitality: {percentage}%</p>
        </div>
    );
}

const ScoreDisplay = ({ myGamePlayer }) => {
    const score = myGamePlayer?.score;
    return (
        <div className="score-display">
            <Grid container direction="column" spacing={1}>
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
      <div className="announcements-display" style={{ maxHeight: '200px', overflowY: 'scroll' }}>
        <Grid container direction="column" spacing={1}>
          {announcements.map((announcement, index) => (
            <Grid item key={index}>
              <Typography>{announcement}</Typography>
            </Grid>
          ))}
        </Grid>
      </div>
    );
  };

const UpperRightDisplay = ({ city, isFriendlyCity, unitTemplates, setHoveredUnit, setHoveredBuilding, setHoveredTech, techTemplates, myCiv, myGamePlayer, announcements, setTechListDialogOpen }) => {
    return (
        <div className="upper-right-display">
            {city && <CityDisplay city={city} setHoveredUnit={setHoveredUnit} setHoveredBuilding={setHoveredBuilding} isFriendly={isFriendlyCity} unitTemplates={unitTemplates}/>}
            {myCiv?.tech_queue?.[0] && <BriefTechDisplay tech={myCiv?.tech_queue?.[0]} myCiv={myCiv} setHoveredTech={setHoveredTech} setTechListDialogOpen={setTechListDialogOpen} techTemplates={techTemplates}/>}
            {myCiv && <CityPowerDisplay myCiv={myCiv} />}
            {myCiv && <CivVitalityDisplay civVitality={myCiv.vitality} />}
            {myGamePlayer && <ScoreDisplay myGamePlayer={myGamePlayer} />}
            {announcements.length > 0 && <AnnouncementsDisplay announcements={announcements} />}
        </div>
    );
};

export default UpperRightDisplay;