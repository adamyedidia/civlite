import React, { useState } from 'react';
import { 
    Dialog, 
    DialogTitle, 
    DialogContent, 
    DialogContentText, 
    createTheme, 
    ThemeProvider, 
    Slider, 
    Typography,
    DialogActions,
    Button,
} from '@mui/material';

export default function SettingsDialog({ 
    open,
    onClose, 
    volume, 
    setVolume,
}) {
    const handleVolumeChange = (event, newValue) => {
        setVolume(newValue);
    };

    return (
        <Dialog open={open} onClose={onClose}>
            <DialogTitle>Game Settings</DialogTitle>
            <DialogContent>
                <DialogContentText>
                    <Typography id="volume-slider" gutterBottom>
                        Volume
                    </Typography>
                    <Slider
                        value={volume}
                        onChange={handleVolumeChange}
                        aria-labelledby="volume-slider"
                        valueLabelDisplay="auto"
                        step={1}
                        marks
                        min={0}
                        max={100}
                    />
                </DialogContentText>
            </DialogContent>
            <DialogActions>
                <Button variant="contained" onClick={onClose}>Ok</Button>
            </DialogActions>
        </Dialog>
    );
}