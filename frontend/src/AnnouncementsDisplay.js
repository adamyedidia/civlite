import React from 'react';
import { Grid, Typography } from '@mui/material';
import './AnnouncementsDisplay.css';

const RenderAnnouncement = ({text, turn_num}) => {
    // Parse out 3 special flags from the string: 
    //   * <civ id=xxx></civ>
    //   * <city id=xxx></city>
    //   * <wonder name=xxx></wonder>

    const parseText = (text) => {
        // Define regex patterns for each tag
        const civRegex = /<civ id=([^>]+)>(.*?)<\/civ>/g;
        const cityRegex = /<city id=([^>]+)>(.*?)<\/city>/g;
        const wonderRegex = /<wonder name=([^>]+)>(.*?)<\/wonder>/g;    
        // Replace <civ> tags
        let parsedText = text.replace(civRegex, (match, p1, p2) => `<span class="civ">${p2}</span>`);

        // Replace <city> tags
        parsedText = parsedText.replace(cityRegex, (match, p1, p2) => `<span class="city">${p2}</span>`);

        // Replace <wonder> tags
        parsedText = parsedText.replace(wonderRegex, (match, p1, p2) => `<span class="wonder">${p2}</span>`);

        // Check the turn
        const turnRegex = /\[T (\d+)\]/g;
        parsedText = parsedText.replace(turnRegex, (match, t) => `<span class=${parseInt(t, 10) === turn_num ? "current-turn" : "previous-turn"}>${match}</span>` )

        return parsedText;
      };
    
      // Note: Be cautious with dangerouslySetInnerHTML to avoid XSS vulnerabilities
      return (
        <Typography dangerouslySetInnerHTML={{ __html: parseText(text) }} />
      );
    };
const AnnouncementsDisplay = ({ announcements, turn_num }) => {
    return (
        <div className="announcements-display">
            <Grid container direction="column" spacing={0}>
                {announcements.map((announcement, index) => (
                    <Grid item key={index}>
                        <RenderAnnouncement text={announcement} turn_num={turn_num}/>
                    </Grid>
                ))}
            </Grid>
        </div>
    );
};

export default AnnouncementsDisplay;