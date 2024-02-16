import { Typography, Button } from '@mui/material';
import React, { useState, useEffect } from 'react';
import { URL } from './settings';

function Timer({ nextForcedRollAt, onTimerElapsed, gameId }) {
  const [secondsElapsed, setSecondsElapsed] = useState(0);

  console.log(nextForcedRollAt);

  const handlePause = () => {
    const data = {
    }

    fetch(`${URL}/api/pause/${gameId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data),
    })

  }

  useEffect(() => {
    if (!nextForcedRollAt) return;

    const intervalId = setInterval(() => {
      const currentTime = Date.now();
      const difference = Math.floor((nextForcedRollAt * 1000 - currentTime) / 1000);
      setSecondsElapsed(difference);
      if (onTimerElapsed && difference <= 0) {
        onTimerElapsed();
        clearInterval(intervalId);
      }
    }, 1000);

    return () => clearInterval(intervalId);
  }, [nextForcedRollAt, onTimerElapsed]);

  function formatTime(seconds) {
    if (seconds < 0) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  const isTimeLow = secondsElapsed === 4 || secondsElapsed === 2 || secondsElapsed === 0; // Check if time is 3 or fewer seconds

  return (
      <div className="announcements-display" style={{ display: 'flex', flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}>
            <Typography variant="h2" style={{ color: isTimeLow ? 'red' : 'inherit', marginLeft: '5px'}}>
                {formatTime(secondsElapsed)}
            </Typography>
            <Button onClick={handlePause} variant="contained">
                Pause 
            </Button>
        </div>
  );
}

export default Timer;

