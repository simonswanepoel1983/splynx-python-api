import React, { useEffect, useState } from 'react';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import CircularProgress from '@mui/material/CircularProgress';
import api from '../utils/api';

interface BillingItem {
  id: number;
  description: string;
  amount: number;
  due_date: string;
}

export default function BillingCard() {
  const [items, setItems] = useState<BillingItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<BillingItem[]>('/billing')
      .then((res) => setItems(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Billing
      </Typography>
      {items.length === 0 ? (
        <Typography>No invoices found</Typography>
      ) : (
        items.slice(0, 5).map((item) => (
          <Typography key={item.id} variant="body2">
            {item.description}: R{item.amount.toFixed(2)} (due {item.due_date})
          </Typography>
        ))
      )}
    </Paper>
  );
}