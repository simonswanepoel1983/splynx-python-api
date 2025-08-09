import React from 'react';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import BillingCard from '../src/components/BillingCard';
import UsageCard from '../src/components/UsageCard';
import SpeedTestCard from '../src/components/SpeedTestCard';

export default function HomePage() {
  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to RocketNet
        </Typography>
      </Grid>
      <Grid item xs={12} md={4}>
        <BillingCard />
      </Grid>
      <Grid item xs={12} md={4}>
        <UsageCard />
      </Grid>
      <Grid item xs={12} md={4}>
        <SpeedTestCard />
      </Grid>
    </Grid>
  );
}