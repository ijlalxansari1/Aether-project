import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import {
  Container,
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Button
} from '@mui/material'
import axios from 'axios'
import ModelResults from '../ML/ModelResults'
import FairnessReport from '../Fairness/FairnessReport'

function Dashboard({ datasetId: propDatasetId }) {
  const { datasetId: paramDatasetId } = useParams()
  const datasetId = propDatasetId || paramDatasetId
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState(null)
  const [error, setError] = useState('')
  const [tab, setTab] = useState(0)

  useEffect(() => {
    if (datasetId) {
      fetchDashboard()
    }
  }, [datasetId])

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`/api/dashboard/${datasetId}`)
      setDashboardData(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  const downloadReport = async () => {
    try {
      const res = await axios.get(`/api/report/${datasetId}`)
      const html = res.data.html
      const blob = new Blob([html], { type: 'text/html' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `aether_report_${datasetId}.html`
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to generate report')
    }
  }

  const downloadPDF = async () => {
    try {
      const res = await axios.get(`/api/report/${datasetId}`)
      const html = res.data.html
      const w = window.open('', '_blank')
      w.document.write(html)
      w.document.close()
      w.focus()
      w.print()
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to open PDF view')
    }
  }

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      </Container>
    )
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    )
  }

  if (!dashboardData) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="info">No dashboard data available</Alert>
      </Container>
    )
  }

  const getQualityColor = (score) => {
    if (score >= 80) return 'success'
    if (score >= 50) return 'warning'
    return 'error'
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight={800} gutterBottom>
            Project Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Unified view across data quality, performance, and fairness.
          </Typography>
        </Box>
        <Box sx={{ display:'flex', gap:1 }}>
          <Button variant="outlined" onClick={downloadPDF}>Download PDF</Button>
          <Button variant="contained" onClick={downloadReport}>Download Report</Button>
        </Box>
      </Box>

      <Tabs value={tab} onChange={(e, newValue) => setTab(newValue)} sx={{ mb: 3 }}>
        <Tab label="Overview" />
        <Tab label="Model Results" />
        <Tab label="Fairness Report" />
      </Tabs>

      {tab === 0 && (
        <Box>
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Card sx={{ overflow: 'hidden' }}>
                <Box sx={{ height: 6, background: 'linear-gradient(90deg, #22c55e, #16a34a)' }} />
                <CardContent>
                  <Typography variant="overline" color="text.secondary">Data Quality</Typography>
                  <Typography variant="h3" color={`${getQualityColor(dashboardData.data_quality.score)}.main`}>
                    {dashboardData.data_quality.score}/100
                  </Typography>
                  <Chip label={dashboardData.data_quality.status} color={getQualityColor(dashboardData.data_quality.score)} size="small" sx={{ mt: 1 }} />
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card sx={{ overflow: 'hidden' }}>
                <Box sx={{ height: 6, background: 'linear-gradient(90deg, #3b82f6, #0284c7)' }} />
                <CardContent>
                  <Typography variant="overline" color="text.secondary">Rows</Typography>
                  <Typography variant="h4">{dashboardData.summary.row_count.toLocaleString()}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <Card sx={{ overflow: 'hidden' }}>
                <Box sx={{ height: 6, background: 'linear-gradient(90deg, #a855f7, #7c3aed)' }} />
                <CardContent>
                  <Typography variant="overline" color="text.secondary">Columns</Typography>
                  <Typography variant="h4">{dashboardData.summary.column_count}</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Story/Narrative Section */}
          {dashboardData.narrative && (
            <Paper elevation={3} sx={{ p: 4, mt: 3, borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom fontWeight={700}>Data Story & Insights</Typography>
              <Typography variant="body1" sx={{ whiteSpace: 'pre-line', lineHeight: 1.8 }}>
                {dashboardData.narrative}
              </Typography>
            </Paper>
          )}

          {/* Model Performance (only if ML path was taken) */}
          {dashboardData.model_performance && (
            <Paper elevation={3} sx={{ p: 4, mt: 3, borderRadius: 2 }}>
              <Typography variant="h6" gutterBottom fontWeight={700}>Model Performance</Typography>
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body1">
                    <strong>Best Model:</strong> {dashboardData.model_performance.best_model}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Problem Type: {dashboardData.model_performance.problem_type}
                  </Typography>
                </Grid>
                {dashboardData.model_performance.models && Object.keys(dashboardData.model_performance.models).length > 0 && (
                  <Grid item xs={12}>
                    <Typography variant="subtitle2" sx={{ mb: 1 }}>All Models:</Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                      {Object.entries(dashboardData.model_performance.models).map(([name, data]) => (
                        <Chip
                          key={name}
                          label={`${name}: ${data.status || 'completed'}`}
                          color={name === dashboardData.model_performance.best_model ? 'primary' : 'default'}
                          size="small"
                        />
                      ))}
                    </Box>
                  </Grid>
                )}
              </Grid>
            </Paper>
          )}

          {/* Path Indicator */}
          <Paper 
            elevation={2} 
            sx={{ 
              p: 3, 
              mt: 3, 
              borderRadius: 2,
              background: dashboardData.model_performance 
                ? 'linear-gradient(135deg, rgba(34,211,238,0.1), rgba(96,165,250,0.1))'
                : 'linear-gradient(135deg, rgba(99,102,241,0.1), rgba(34,211,238,0.1))'
            }}
          >
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 1 }}>
              Analysis Path: {dashboardData.model_performance ? 'Deep ML Analysis' : 'Descriptive Report'}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {dashboardData.model_performance 
                ? 'This analysis includes predictive modeling with trained ML models and fairness evaluation.'
                : 'This is a descriptive analysis report with EDA visualizations and data story. No ML models were trained.'}
            </Typography>
          </Paper>
        </Box>
      )}

      {tab === 1 && dashboardData.model_results && (<ModelResults modelResults={dashboardData.model_results} />)}

      {tab === 2 && dashboardData.fairness_report && (<FairnessReport fairnessData={dashboardData.fairness_report} />)}
    </Container>
  )
}

export default Dashboard

