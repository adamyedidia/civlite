import React, { createContext, useContext, useState, useEffect } from 'react';

const GlobalClockContext = createContext(0);

export function GlobalClockProvider({ children }) {
  const [clock, setClock] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setClock(prevClock => prevClock + 1);
    }, 120);
    return () => clearInterval(interval);
  }, []);

  return (
    <GlobalClockContext.Provider value={clock}>
      {children}
    </GlobalClockContext.Provider>
  );
}

export const useGlobalClockValue = () => useContext(GlobalClockContext);