import React from 'react';
import { 
    Dialog, 
    DialogTitle, 
    DialogContent, 
    Box, 
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
                <Box sx={{ minWidth: 240 }}>
                    <Typography id="volume-slider" gutterBottom>
                        Volume
                    </Typography>
                    <Slider
                        value={volume}
                        onChange={handleVolumeChange}
                        aria-labelledby="volume-slider"
                        valueLabelDisplay="auto"
                        step={1}
                        min={0}
                        max={100}
                    />
                </Box>
            </DialogContent>
            <DialogActions>
                <Button variant="contained" onClick={onClose}>Ok</Button>
            </DialogActions>
        </Dialog>
    );
}