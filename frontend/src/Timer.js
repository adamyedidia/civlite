import { Typography } from '@mui/material';
import React, { useState, useEffect } from 'react';

function Timer({ nextForcedRollAt, onTimerElapsed }) {
  const [secondsElapsed, setSecondsElapsed] = useState(0);

  console.log(nextForcedRollAt);

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
      <div className="announcements-display" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <Typography variant="h2" style={{ color: isTimeLow ? 'red' : 'inherit' }}>
            {formatTime(secondsElapsed)}
            </Typography>
        </div>
  );
}

export default Timer;

