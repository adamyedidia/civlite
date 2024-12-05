// theme.js
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  components: {
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          fontSize: '20px', // Example: Set the font size
        },
      },
    },
  },
});

export default theme;