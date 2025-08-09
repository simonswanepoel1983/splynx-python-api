import React, { useEffect, useState } from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import LinearProgress from '@mui/material/LinearProgress';
import api from '../utils/api';

interface UsageItem {
  period: string;
  used_gb: number;
  quota_gb?: number;
}

export default function UsageCard() {
  const [usage, setUsage] = useState<UsageItem | null>(null);

  useEffect(() => {
    api
      .get<UsageItem[]>('/usage')
      .then((res) => {
        if (res.data.length > 0) setUsage(res.data[0]);
      })
      .catch(console.error);
  }, []);

  if (!usage) return <LinearProgress />;

  const percent = usage.quota_gb ? (usage.used_gb / usage.quota_gb) * 100 : 0;

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Usage ({usage.period})
      </Typography>
      {usage.quota_gb ? (
        <>
          <Typography>
            {usage.used_gb.toFixed(2)} GB of {usage.quota_gb.toFixed(2)} GB used
          </Typography>
          <LinearProgress variant="determinate" value={percent} />
        </>
      ) : (
        <Typography>{usage.used_gb.toFixed(2)} GB used</Typography>
      )}
    </Paper>
  );
}