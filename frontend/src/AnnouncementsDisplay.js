import React from 'react';
import { Grid, Typography } from '@mui/material';
import './AnnouncementsDisplay.css';

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

export default AnnouncementsDisplay;