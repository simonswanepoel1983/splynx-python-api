import React, { useEffect, useState } from 'react';
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import api from '../../src/utils/api';
import CircularProgress from '@mui/material/CircularProgress';
import Snackbar from '@mui/material/Snackbar';

interface PackageItem {
  id: number;
  name: string;
  price: number;
  speed_mbps: number;
}

export default function PackagesPage() {
  const [packages, setPackages] = useState<PackageItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [snack, setSnack] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<PackageItem[]>('/packages')
      .then((res) => setPackages(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleUpgrade = (id: number) => {
    api
      .post('/upgrade', { package_id: id })
      .then(() => setSnack('Upgrade requested'))
      .catch((err) => setSnack(err.response?.data?.detail || 'Error'));
  };

  if (loading) return <CircularProgress />;

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Available Packages
      </Typography>
      <Grid container spacing={2}>
        {packages.map((pkg) => (
          <Grid item xs={12} md={4} key={pkg.id}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6">{pkg.name}</Typography>
              <Typography>
                {pkg.speed_mbps} Mbps - R{pkg.price.toFixed(2)} / month
              </Typography>
              <Button onClick={() => handleUpgrade(pkg.id)} variant="contained" sx={{ mt: 1 }}>
                Upgrade
              </Button>
            </Paper>
          </Grid>
        ))}
      </Grid>
      <Snackbar
        open={!!snack}
        autoHideDuration={4000}
        onClose={() => setSnack(null)}
        message={snack}
      />
    </>
  );
}