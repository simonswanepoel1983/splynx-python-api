import * as React from 'react';
import { Inter } from 'next/font/google';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';

const inter = Inter({ subsets: ['latin'] });

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#ff6600', // RocketNet orange
    },
    secondary: {
      main: '#0066ff',
    },
  },
  typography: {
    fontFamily: inter.style.fontFamily,
  },
});

export const metadata = {
  title: 'RocketNet Portal',
  description: 'Manage your RocketNet account with blazing speed',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <Box component="main" sx={{ p: 2 }}>
            {children}
          </Box>
        </ThemeProvider>
      </body>
    </html>
  );
}