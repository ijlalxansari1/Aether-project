import React, { useState, useEffect } from 'react'
import {
  Paper,
  Typography,
  Box,
  Button,
  Alert,
  CircularProgress,
  FormControlLabel,
  Checkbox,
  Card,
  CardContent,
  Grid,
  Chip,
  TextField,
  MenuItem
} from '@mui/material'
import axios from 'axios'

function ModelSelection({ datasetId, onTrainingComplete }) {
  const [loading, setLoading] = useState(false)
  const [recommendations, setRecommendations] = useState(null)
  const [targetColumn, setTargetColumn] = useState('')
  const [columns, setColumns] = useState([])
  const [selectedModels, setSelectedModels] = useState([])
  const [training, setTraining] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const loadCols = async () => {
      try {
        const res = await axios.get(`/api/data-processing/profile/${datasetId}`)
        const cols = Object.keys(res.data.profile?.data_types || {})
        setColumns(cols)
      } catch (e) {
        // ignore; free text still works
      }
    }
    if (datasetId) loadCols()
  }, [datasetId])

  const downloadReport = async () => {
    try {
      const res = await axios.get(`/api/report/${datasetId}`)
      const blob = new Blob([res.data.html], { type: 'text/html' })
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

  const handleGetRecommendations = async () => {
    if (!targetColumn) {
      setError('Please choose or enter a target column')
      return
    }
    setLoading(true)
    setError('')
    try {
      const response = await axios.post('/api/ml/recommend', {
        dataset_id: datasetId,
        target_column: targetColumn
      })
      setRecommendations(response.data)
      const baseline = response.data.recommendations.find(r => r.type === 'baseline')
      if (baseline) setSelectedModels([baseline.name])
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get recommendations')
    } finally {
      setLoading(false)
    }
  }

  const handleTrain = async () => {
    if (selectedModels.length === 0) {
      setError('Please select at least one model')
      return
    }
    setTraining(true)
    setError('')
    try {
      const response = await axios.post('/api/ml/train', {
        dataset_id: datasetId,
        target_column: targetColumn,
        selected_models: selectedModels
      })
      onTrainingComplete(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Training failed')
    } finally {
      setTraining(false)
    }
  }

  const toggleModel = (modelName) => {
    if (selectedModels.includes(modelName)) setSelectedModels(selectedModels.filter(m => m !== modelName))
    else setSelectedModels([...selectedModels, modelName])
  }

  return (
    <Paper elevation={3} sx={{ p: 4, borderRadius: 3 }}>
      <Typography variant="h5" gutterBottom fontWeight={800} sx={{ mb: 1 }}>Model Selection & Training</Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>Choose a target column and models to train, or skip modeling and generate the report now.</Typography>
      {error && (<Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>)}

      {!recommendations && (
        <Box sx={{ mt: 3, display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 2 }}>
          <Box>
            {columns.length > 0 ? (
              <TextField select fullWidth label="Target column" value={targetColumn} onChange={(e) => setTargetColumn(e.target.value)} sx={{ mb: 2 }}>
                {columns.map((c) => (<MenuItem key={c} value={c}>{c}</MenuItem>))}
              </TextField>
            ) : (
              <TextField fullWidth label="Target column name" value={targetColumn} onChange={(e) => setTargetColumn(e.target.value)} helperText="Column to predict (e.g., churn, price)" sx={{ mb: 2 }} />
            )}
            <Button 
              variant="contained" 
              onClick={handleGetRecommendations} 
              disabled={loading || !targetColumn} 
              fullWidth
              size="large"
              sx={{
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
              {loading ? <CircularProgress size={24} color="inherit" /> : 'Get Model Recommendations'}
            </Button>
          </Box>
          <Box>
            <Button variant="outlined" onClick={downloadReport} fullWidth>Skip modeling → Download Report</Button>
          </Box>
        </Box>
      )}

      {recommendations && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>Problem Type: <Chip label={recommendations.problem_type} color="primary" /></Typography>
          <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>Recommended Models</Typography>
          <Grid container spacing={2}>
            {recommendations.recommendations.map((model, idx) => (
              <Grid item xs={12} md={6} key={idx}>
                <Card variant="outlined" sx={{ border: selectedModels.includes(model.name) ? '2px solid #0ea5e9' : '1px solid #e5e7eb', cursor: 'pointer', transition: 'transform .15s ease, box-shadow .15s ease', '&:hover': { transform: 'translateY(-2px)', boxShadow: 6 } }} onClick={() => toggleModel(model.name)}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Typography variant="h6" fontWeight={700}>{model.name}</Typography>
                      <Chip label={model.type} color={model.type === 'baseline' ? 'default' : 'primary'} size="small" />
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>{model.description}</Typography>
                    <FormControlLabel control={<Checkbox checked={selectedModels.includes(model.name)} onChange={() => toggleModel(model.name)} />} label="Select" sx={{ mt: 1 }} />
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
          <Box sx={{ mt: 4, display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 2 }}>
            <Button 
              variant="contained" 
              size="large" 
              onClick={handleTrain} 
              disabled={training || selectedModels.length === 0} 
              fullWidth
              sx={{
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
              {training ? <CircularProgress size={24} color="inherit" /> : 'Train Selected Models'}
            </Button>
            <Button 
              variant="outlined" 
              onClick={downloadReport} 
              fullWidth
              size="large"
              sx={{
                py: 1.5,
                borderWidth: 2,
                '&:hover': {
                  borderWidth: 2,
                  transform: 'translateY(-2px)'
                },
                transition: 'all 0.3s ease'
              }}
            >
              Skip modeling → Download Report
            </Button>
          </Box>
        </Box>
      )}
    </Paper>
  )
}

export default ModelSelection

