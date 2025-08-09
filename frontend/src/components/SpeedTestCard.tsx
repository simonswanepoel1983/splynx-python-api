import React, { useState } from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import api from '../utils/api';
import CircularProgress from '@mui/material/CircularProgress';

interface SpeedResult {
  ping_ms: number;
  download_mbps: number;
  upload_mbps: number;
  timestamp: string;
}

export default function SpeedTestCard() {
  const [result, setResult] = useState<SpeedResult | null>(null);
  const [loading, setLoading] = useState(false);

  const runTest = () => {
    setLoading(true);
    api
      .get<SpeedResult>('/speedtest')
      .then((res) => setResult(res.data))
      .finally(() => setLoading(false));
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Speed Test
      </Typography>
      {loading && <CircularProgress />}
      {result && (
        <Typography>
          Ping: {result.ping_ms} ms | Down: {result.download_mbps} Mbps | Up: {result.upload_mbps} Mbps
        </Typography>
      )}
      <Button onClick={runTest} variant="contained" sx={{ mt: 1 }}>
        {result ? 'Run Again' : 'Run Test'}
      </Button>
    </Paper>
  );
}