// theme.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  components: {
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          fontSize: '16px', // Example: Set the font size
          backgroundColor: 'black',
        },
      },
    },
  },
});

export default theme;