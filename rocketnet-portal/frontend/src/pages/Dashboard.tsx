import React from 'react';
import { useQuery } from 'react-query';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Chip,
  Avatar,
  IconButton,
} from '@mui/material';
import {
  Speed as SpeedIcon,
  DataUsage as UsageIcon,
  Receipt as BillingIcon,
  TrendingUp as TrendingUpIcon,
  Refresh as RefreshIcon,
  ArrowForward as ArrowForwardIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

interface DashboardData {
  currentUsage: {
    total_usage_gb: number;
    usage_limit_gb: number;
    usage_percentage: number;
  };
  currentBilling: {
    total_outstanding: number;
    overdue_count: number;
  };
  speedTest: {
    average_download: number;
    average_upload: number;
    average_ping: number;
  };
  usageHistory: Array<{
    date: string;
    total_gb: number;
  }>;
}

const Dashboard: React.FC = () => {
  const { data: dashboardData, isLoading, refetch } = useQuery<DashboardData>(
    'dashboard',
    async () => {
      const [usageRes, billingRes, speedRes, usageHistoryRes] = await Promise.all([
        axios.get('/api/usage/current'),
        axios.get('/api/billing/summary'),
        axios.get('/api/speed-tests/summary'),
        axios.get('/api/usage/history?days=7'),
      ]);

      return {
        currentUsage: usageRes.data,
        currentBilling: billingRes.data,
        speedTest: speedRes.data,
        usageHistory: usageHistoryRes.data,
      };
    },
    {
      refetchInterval: 300000, // Refetch every 5 minutes
    }
  );

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    subtitle?: string;
    icon: React.ReactNode;
    color: string;
    onClick?: () => void;
  }> = ({ title, value, subtitle, icon, color, onClick }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <Card
        sx={{
          height: '100%',
          cursor: onClick ? 'pointer' : 'default',
          '&:hover': onClick ? { transform: 'translateY(-4px)', boxShadow: 4 } : {},
          transition: 'all 0.3s ease',
        }}
        onClick={onClick}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Avatar sx={{ bgcolor: color, width: 56, height: 56 }}>
              {icon}
            </Avatar>
            {onClick && (
              <IconButton size="small">
                <ArrowForwardIcon />
              </IconButton>
            )}
          </Box>
          <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', mb: 0.5 }}>
            {value}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );

  if (isLoading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1" sx={{ fontWeight: 'bold' }}>
          Dashboard
        </Typography>
        <Button
          startIcon={<RefreshIcon />}
          onClick={() => refetch()}
          variant="outlined"
        >
          Refresh
        </Button>
      </Box>

      <Grid container spacing={3}>
        {/* Usage Overview */}
        <Grid item xs={12} md={6} lg={3}>
          <StatCard
            title="Data Usage"
            value={`${dashboardData?.currentUsage?.total_usage_gb?.toFixed(1) || 0} GB`}
            subtitle={`${dashboardData?.currentUsage?.usage_percentage?.toFixed(1) || 0}% of limit`}
            icon={<UsageIcon />}
            color="#1976d2"
            onClick={() => window.location.href = '/usage'}
          />
        </Grid>

        {/* Billing Overview */}
        <Grid item xs={12} md={6} lg={3}>
          <StatCard
            title="Outstanding Balance"
            value={`$${dashboardData?.currentBilling?.total_outstanding?.toFixed(2) || 0}`}
            subtitle={`${dashboardData?.currentBilling?.overdue_count || 0} overdue invoices`}
            icon={<BillingIcon />}
            color={dashboardData?.currentBilling?.total_outstanding > 0 ? '#d32f2f' : '#2e7d32'}
            onClick={() => window.location.href = '/billing'}
          />
        </Grid>

        {/* Speed Test Overview */}
        <Grid item xs={12} md={6} lg={3}>
          <StatCard
            title="Average Download"
            value={`${dashboardData?.speedTest?.average_download?.toFixed(0) || 0} Mbps`}
            subtitle={`${dashboardData?.speedTest?.average_upload?.toFixed(0) || 0} Mbps upload`}
            icon={<SpeedIcon />}
            color="#ed6c02"
            onClick={() => window.location.href = '/speed-tests'}
          />
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12} md={6} lg={3}>
          <StatCard
            title="Quick Actions"
            value="4"
            subtitle="Available actions"
            icon={<TrendingUpIcon />}
            color="#9c27b0"
          />
        </Grid>

        {/* Usage Chart */}
        <Grid item xs={12} lg={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                  Data Usage (Last 7 Days)
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={dashboardData?.usageHistory || []}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="date"
                      tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis />
                    <Tooltip
                      labelFormatter={(value) => new Date(value).toLocaleDateString()}
                      formatter={(value: number) => [`${value.toFixed(1)} GB`, 'Usage']}
                    />
                    <Line
                      type="monotone"
                      dataKey="total_gb"
                      stroke="#1976d2"
                      strokeWidth={2}
                      dot={{ fill: '#1976d2', strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Quick Actions Panel */}
        <Grid item xs={12} lg={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                  Quick Actions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<SpeedIcon />}
                    onClick={() => window.location.href = '/speed-tests'}
                    sx={{ justifyContent: 'flex-start' }}
                  >
                    Run Speed Test
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<BillingIcon />}
                    onClick={() => window.location.href = '/billing'}
                    sx={{ justifyContent: 'flex-start' }}
                  >
                    View Bills
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<UsageIcon />}
                    onClick={() => window.location.href = '/usage'}
                    sx={{ justifyContent: 'flex-start' }}
                  >
                    Check Usage
                  </Button>
                  <Button
                    variant="outlined"
                    startIcon={<TrendingUpIcon />}
                    onClick={() => window.location.href = '/packages'}
                    sx={{ justifyContent: 'flex-start' }}
                  >
                    Upgrade Package
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
          >
            <Card>
              <CardContent>
                <Typography variant="h6" component="h2" sx={{ mb: 2 }}>
                  Recent Activity
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip label="Speed test completed - 245 Mbps" color="primary" />
                  <Chip label="Bill paid - $89.99" color="success" />
                  <Chip label="Usage alert - 80% of limit" color="warning" />
                  <Chip label="Package upgrade requested" color="info" />
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;