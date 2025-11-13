import React, { useState, useEffect } from 'react'
import {
  Paper,
  Typography,
  Box,
  Button,
  Alert,
  CircularProgress,
  Chip,
  Grid,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody
} from '@mui/material'
import axios from 'axios'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import WarningIcon from '@mui/icons-material/Warning'
import ErrorIcon from '@mui/icons-material/Error'

function DataProfile({ datasetId, onComplete }) {
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState('')
  const [cleaningDialog, setCleaningDialog] = useState(false)
  const [selectedOperations, setSelectedOperations] = useState([])

  useEffect(() => {
    fetchProfile()
  }, [datasetId])

  const fetchProfile = async () => {
    try {
      const response = await axios.get(`/api/data-processing/profile/${datasetId}`)
      setProfile(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load profile')
    } finally {
      setLoading(false)
    }
  }

  const handleClean = async () => {
    try {
      await axios.post('/api/data-processing/clean', {
        dataset_id: datasetId,
        operations: selectedOperations,
        user_approved: true
      })
      setCleaningDialog(false)
      fetchProfile() // Refresh profile
    } catch (err) {
      setError(err.response?.data?.detail || 'Cleaning failed')
    }
  }

  const getQualityColor = (score) => {
    if (score >= 80) return 'success'
    if (score >= 50) return 'warning'
    return 'error'
  }

  const getQualityIcon = (score) => {
    if (score >= 80) return <CheckCircleIcon />
    if (score >= 50) return <WarningIcon />
    return <ErrorIcon />
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>
  }

  if (!profile) {
    return <Alert severity="info">No profile data available</Alert>
  }

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 4, mb: 3, borderRadius: 3 }}>
        <Typography variant="h5" gutterBottom fontWeight={800} sx={{ mb: 2 }}>
          Data Profile & Quality Assessment
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          High-level health check: metadata, missing values, cardinality, and basic statistics.
        </Typography>
        
        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={4}>
            <Card sx={{ overflow: 'hidden' }}>
              <Box sx={{ height: 6, background: 'linear-gradient(90deg, #22c55e, #16a34a)' }} />
              <CardContent>
                <Box display="flex" alignItems="center" gap={1}>
                  {getQualityIcon(profile.data_quality_score)}
                  <Typography variant="h6">Quality Score</Typography>
                </Box>
                <Typography variant="h3" color={getQualityColor(profile.data_quality_score) + '.main'}>
                  {profile.data_quality_score}/100
                </Typography>
                <Chip
                  label={profile.data_quality_score >= 80 ? 'High' : profile.data_quality_score >= 50 ? 'Medium' : 'Low'}
                  color={getQualityColor(profile.data_quality_score)}
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ overflow: 'hidden' }}>
              <Box sx={{ height: 6, background: 'linear-gradient(90deg, #3b82f6, #0284c7)' }} />
              <CardContent>
                <Typography variant="h6">Rows</Typography>
                <Typography variant="h4">{profile.profile.summary.row_count.toLocaleString()}</Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <Card sx={{ overflow: 'hidden' }}>
              <Box sx={{ height: 6, background: 'linear-gradient(90deg, #a855f7, #7c3aed)' }} />
              <CardContent>
                <Typography variant="h6">Columns</Typography>
                <Typography variant="h4">{profile.profile.summary.column_count}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Data preview */}
        {profile.preview && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>Data Preview</Typography>
            <Box sx={{ maxHeight: 300, overflow: 'auto', border: '1px solid #e5e7eb', borderRadius: 1 }}>
              <Table size="small" stickyHeader>
                <TableHead>
                  <TableRow>
                    {profile.preview.columns.map((c) => (
                      <TableCell key={c}>{c}</TableCell>
                    ))}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {profile.preview.data.map((r, i) => (
                    <TableRow key={i}>
                      {r.map((cell, j) => (
                        <TableCell key={j}>{String(cell)}</TableCell>
                      ))}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Box>
          </Box>
        )}

        {/* Cleaning suggestions + continue (unchanged) */}
        {profile.cleaning_suggestions && profile.cleaning_suggestions.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cleaning Suggestions
            </Typography>
            <List>
              {profile.cleaning_suggestions.map((suggestion, idx) => (
                <ListItem key={idx}>
                  <ListItemText
                    primary={suggestion.description}
                    secondary={`Impact: ${suggestion.impact}`}
                  />
                </ListItem>
              ))}
            </List>
            <Button
              variant="outlined"
              onClick={() => {
                setSelectedOperations(profile.cleaning_suggestions.map(s => s.operation))
                setCleaningDialog(true)
              }}
              sx={{ mt: 2 }}
            >
              Apply Cleaning Operations
            </Button>
          </Box>
        )}

        <Box sx={{ mt: 4, display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            onClick={() => onComplete(profile)}
            size="large"
            sx={{
              px: 4,
              background: 'linear-gradient(135deg, #6366f1 0%, #22d3ee 100%)',
              '&:hover': {
                background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
                transform: 'translateY(-2px)',
                boxShadow: 6
              },
              transition: 'all 0.3s ease'
            }}
          >
            Continue to Ethics Analysis
          </Button>
          {profile.data_quality_score < 50 && (
            <Alert severity="warning" sx={{ flex: 1, minWidth: 300 }}>
              Data quality is low. Consider cleaning the data first.
            </Alert>
          )}
        </Box>
      </Paper>

      {/* Dialog code unchanged */}
      <Dialog open={cleaningDialog} onClose={() => setCleaningDialog(false)}>
        <DialogTitle>Confirm Cleaning Operations</DialogTitle>
        <DialogContent>
          <Typography>Apply the following cleaning operations?</Typography>
          <List>
            {selectedOperations.map((op, idx) => (
              <ListItem key={idx}>
                <ListItemText primary={op} />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCleaningDialog(false)}>Cancel</Button>
          <Button onClick={handleClean} variant="contained">Apply</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default DataProfile

