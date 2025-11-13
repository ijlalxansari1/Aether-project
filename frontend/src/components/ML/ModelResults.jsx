import React from 'react'
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material'
import Plot from 'react-plotly.js'

function ModelResults({ modelResults: propModelResults, modelRunId }) {
  // If modelRunId is provided, fetch data
  // For now, use propModelResults if available
  
  if (!propModelResults) {
    return (
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography>No model results available</Typography>
      </Paper>
    )
  }

  const { problem_type, models, best_model, best_score, feature_importance } = propModelResults

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Model Results
        </Typography>

        <Typography variant="h6" sx={{ mt: 2, mb: 1 }}>
          Best Model: <Chip label={best_model} color="primary" />
        </Typography>

        <Grid container spacing={2} sx={{ mt: 2 }}>
          {Object.entries(models).map(([modelName, modelData]) => (
            <Grid item xs={12} md={6} key={modelName}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6">{modelName}</Typography>
                  {modelData.metrics && (
                    <Box sx={{ mt: 2 }}>
                      {problem_type === 'classification' ? (
                        <>
                          <Typography>Accuracy: {(modelData.metrics.accuracy * 100).toFixed(2)}%</Typography>
                          <Typography>F1 Score: {modelData.metrics.f1_score.toFixed(4)}</Typography>
                          {modelData.metrics.auc && (
                            <Typography>AUC: {modelData.metrics.auc.toFixed(4)}</Typography>
                          )}
                        </>
                      ) : (
                        <>
                          <Typography>RMSE: {modelData.metrics.rmse.toFixed(4)}</Typography>
                          <Typography>R² Score: {modelData.metrics.r2_score.toFixed(4)}</Typography>
                        </>
                      )}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>

      {feature_importance && feature_importance.feature_importance && (
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h6" gutterBottom>
            Feature Importance
          </Typography>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Feature</TableCell>
                  <TableCell align="right">Importance</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {Object.entries(feature_importance.feature_importance)
                  .slice(0, 10)
                  .map(([feature, importance]) => (
                    <TableRow key={feature}>
                      <TableCell>{feature}</TableCell>
                      <TableCell align="right">{(importance * 100).toFixed(2)}%</TableCell>
                    </TableRow>
                  ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  )
}

export default ModelResults

