import React, { useEffect, useState } from 'react'
import { Paper, Typography, Box, Alert, CircularProgress, Grid, Card, CardContent, Button, FormControlLabel, Checkbox, Chip } from '@mui/material'
import Plot from 'react-plotly.js'
import axios from 'axios'

function EDAView({ datasetId, onComplete, targetColumn = null }) {
  const [loading, setLoading] = useState(true)
  const [eda, setEda] = useState(null)
  const [error, setError] = useState('')
  const [autoClean, setAutoClean] = useState(false)

  useEffect(() => { generate() }, [datasetId, autoClean])

  const generate = async () => {
    setLoading(true)
    setError('')
    try {
      const res = await axios.post('/api/eda/generate', { 
        dataset_id: datasetId, 
        target_column: targetColumn,
        auto_clean: autoClean
      })
      setEda(res.data)
    } catch (e) {
      setError(e.response?.data?.detail || 'Failed to generate EDA')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <Box display="flex" justifyContent="center" p={4}><CircularProgress /></Box>
  if (error) return <Alert severity="error">{error}</Alert>
  if (!eda) return <Alert severity="info">No EDA available</Alert>

  const viz = eda.visualizations || {}

  return (
    <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
        <Box>
          <Typography variant="h5" fontWeight={800} gutterBottom sx={{ mb: 1 }}>
            Exploratory Data Analysis
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Comprehensive statistical analysis, correlations, and distributions. Data cleaning can be applied automatically.
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={autoClean}
                onChange={(e) => setAutoClean(e.target.checked)}
                disabled={loading}
              />
            }
            label="Auto-apply safe cleaning"
          />
          <Button
            variant="outlined"
            size="small"
            onClick={generate}
            disabled={loading}
          >
            {loading ? 'Regenerating...' : 'Regenerate'}
          </Button>
        </Box>
      </Box>

      {eda?.cleaning_applied && eda?.cleaning_summary && (
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography variant="subtitle2" fontWeight={700}>Data Cleaning Applied</Typography>
          <Typography variant="body2">
            Applied {eda.cleaning_summary.operations_applied?.join(', ')}. 
            Rows: {eda.cleaning_summary.rows_before} → {eda.cleaning_summary.rows_after}, 
            Columns: {eda.cleaning_summary.columns_before} → {eda.cleaning_summary.columns_after}
          </Typography>
        </Alert>
      )}

      {(eda.insights || []).length > 0 && (
        <Card sx={{ mb: 3, borderRadius: 2, background: 'linear-gradient(135deg, rgba(99,102,241,0.05), rgba(34,211,238,0.05))' }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={700} sx={{ mb: 1 }}>
              Key Insights
            </Typography>
            {(eda.insights || []).map((i, idx) => (
              <Typography key={idx} variant="body2" sx={{ mb: 0.5 }}>
                • {i}
              </Typography>
            ))}
          </CardContent>
        </Card>
      )}

      {/* Histograms Section */}
      {(viz.histograms || []).length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
            Distribution Analysis
          </Typography>
          <Grid container spacing={3}>
            {(viz.histograms || []).slice(0, 4).map((h, idx) => (
              <Grid item xs={12} sm={6} key={idx}>
                <Card sx={{ p: 2, borderRadius: 2 }}>
                  <Plot 
                    data={JSON.parse(h.figure).data} 
                    layout={{
                      ...JSON.parse(h.figure).layout,
                      height: 400,
                      autosize: true
                    }} 
                    config={{
                      displayModeBar: true,
                      displaylogo: false,
                      modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
                      responsive: true
                    }}
                    style={{ width: '100%', height: '100%' }}
                  />
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Correlation Heatmap */}
      {viz.correlations && viz.correlations.figure && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
            Correlation Analysis
          </Typography>
          <Card sx={{ p: 2, borderRadius: 2, display: 'flex', justifyContent: 'center' }}>
            <Plot 
              data={JSON.parse(viz.correlations.figure).data} 
              layout={{
                ...JSON.parse(viz.correlations.figure).layout,
                height: 500,
                autosize: true
              }} 
              config={{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
                responsive: true
              }}
              style={{ width: '100%', maxWidth: '800px' }}
            />
          </Card>
        </Box>
      )}

      {/* Box Plots Section */}
      {(viz.box_plots || []).length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
            Outlier Detection
          </Typography>
          <Grid container spacing={3}>
            {(viz.box_plots || []).slice(0, 4).map((b, idx) => (
              <Grid item xs={12} sm={6} key={idx}>
                <Card sx={{ p: 2, borderRadius: 2 }}>
                  <Plot 
                    data={JSON.parse(b.figure).data} 
                    layout={{
                      ...JSON.parse(b.figure).layout,
                      height: 400,
                      autosize: true
                    }} 
                    config={{
                      displayModeBar: true,
                      displaylogo: false,
                      modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
                      responsive: true
                    }}
                    style={{ width: '100%', height: '100%' }}
                  />
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Scatter Plots (if available) */}
      {(viz.scatter_plots || []).length > 0 && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
            Feature Relationships
          </Typography>
          <Grid container spacing={3}>
            {(viz.scatter_plots || []).slice(0, 4).map((s, idx) => (
              <Grid item xs={12} sm={6} key={idx}>
                <Card sx={{ p: 2, borderRadius: 2 }}>
                  <Plot 
                    data={JSON.parse(s.figure).data} 
                    layout={{
                      ...JSON.parse(s.figure).layout,
                      height: 400,
                      autosize: true
                    }} 
                    config={{
                      displayModeBar: true,
                      displaylogo: false,
                      modeBarButtonsToRemove: ['pan2d', 'lasso2d'],
                      responsive: true
                    }}
                    style={{ width: '100%', height: '100%' }}
                  />
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {/* Continue Button */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 4 }}>
        <Button
          variant="contained"
          size="large"
          onClick={() => onComplete(eda)}
          sx={{
            px: 4,
            py: 1.5,
            background: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
            '&:hover': {
              background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
              transform: 'translateY(-2px)',
              boxShadow: 6
            },
            transition: 'all 0.3s ease'
          }}
        >
          Continue to Story Mode
        </Button>
      </Box>
    </Paper>
  )
}

export default EDAView
