import React, { useState } from 'react';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import api from '../../src/utils/api';
import Snackbar from '@mui/material/Snackbar';

const RETENTION_FEE = 250; // Should match backend

export default function CancelPage() {
  const [step, setStep] = useState<'confirm' | 'payment' | 'done'>('confirm');
  const [card, setCard] = useState('');
  const [snack, setSnack] = useState<string | null>(null);

  const handlePay = () => {
    // Simulate payment success. In real app integrate Stripe/Payfast etc.
    setStep('done');
    api
      .post('/downgrade', { package_id: 0, paid_retention_fee: true })
      .then(() => setSnack('Cancellation processed'))
      .catch((err) => setSnack(err.response?.data?.detail || 'Error'));
  };

  return (
    <Paper sx={{ p: 2 }}>
      {step === 'confirm' && (
        <> 
          <Typography variant="h5" gutterBottom>
            Sorry to see you go
          </Typography>
          <Typography gutterBottom>
            A retention fee of R{RETENTION_FEE} is required to cancel your service.
          </Typography>
          <Button variant="contained" onClick={() => setStep('payment')}>
            Proceed to Payment
          </Button>
        </>
      )}

      {step === 'payment' && (
        <>
          <Typography variant="h6" gutterBottom>
            Pay Retention Fee (R{RETENTION_FEE})
          </Typography>
          <TextField
            fullWidth
            label="Card Number"
            value={card}
            onChange={(e) => setCard(e.target.value)}
            sx={{ mb: 2 }}
          />
          <Button variant="contained" onClick={handlePay} disabled={!card}>
            Pay & Cancel
          </Button>
        </>
      )}

      {step === 'done' && (
        <Typography variant="h6">Your cancellation is being processed. Thank you.</Typography>
      )}

      <Snackbar open={!!snack} autoHideDuration={4000} onClose={() => setSnack(null)} message={snack} />
    </Paper>
  );
}