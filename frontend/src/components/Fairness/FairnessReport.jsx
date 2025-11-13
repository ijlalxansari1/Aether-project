import React from 'react'
import {
  Paper,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  Chip,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material'

function FairnessReport({ fairnessData: propFairnessData, fairnessReportId }) {
  // If fairnessReportId is provided, fetch data
  // For now, use propFairnessData if available
  
  if (!propFairnessData) {
    return (
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography>No fairness data available</Typography>
      </Paper>
    )
  }

  const { bias_detected, bias_severity, bias_description, groups, overall_metrics } = propFairnessData

  return (
    <Box>
      <Paper elevation={3} sx={{ p: 4, mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Fairness Evaluation
        </Typography>

        {bias_detected ? (
          <Alert severity={bias_severity === 'high' ? 'error' : 'warning'} sx={{ mt: 2 }}>
            <Typography variant="h6">Bias Detected</Typography>
            <Typography>{bias_description}</Typography>
          </Alert>
        ) : (
          <Alert severity="success" sx={{ mt: 2 }}>
            No significant bias detected across groups
          </Alert>
        )}

        {overall_metrics && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Overall Metrics
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(overall_metrics).map(([metric, value]) => (
                <Grid item xs={6} md={3} key={metric}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="body2" color="text.secondary">
                        {metric.replace('_', ' ').toUpperCase()}
                      </Typography>
                      <Typography variant="h6">{value.toFixed(4)}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {groups && Object.keys(groups).length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Per-Group Metrics
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Group</TableCell>
                    <TableCell align="right">Count</TableCell>
                    {overall_metrics && 'accuracy' in overall_metrics && (
                      <>
                        <TableCell align="right">Accuracy</TableCell>
                        <TableCell align="right">F1 Score</TableCell>
                        <TableCell align="right">Difference</TableCell>
                      </>
                    )}
                    {overall_metrics && 'rmse' in overall_metrics && (
                      <>
                        <TableCell align="right">RMSE</TableCell>
                        <TableCell align="right">R² Score</TableCell>
                      </>
                    )}
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(groups).map(([group, metrics]) => (
                    <TableRow key={group}>
                      <TableCell>{group}</TableCell>
                      <TableCell align="right">{metrics.count}</TableCell>
                      {'accuracy' in metrics && (
                        <>
                          <TableCell align="right">{(metrics.accuracy * 100).toFixed(2)}%</TableCell>
                          <TableCell align="right">{metrics.f1_score.toFixed(4)}</TableCell>
                          <TableCell align="right">
                            <Chip
                              label={`${(metrics.accuracy_difference * 100).toFixed(2)}%`}
                              color={Math.abs(metrics.accuracy_difference) > 0.1 ? 'error' : 'default'}
                              size="small"
                            />
                          </TableCell>
                        </>
                      )}
                      {'rmse' in metrics && (
                        <>
                          <TableCell align="right">{metrics.rmse.toFixed(4)}</TableCell>
                          <TableCell align="right">{metrics.r2_score.toFixed(4)}</TableCell>
                        </>
                      )}
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Box>
        )}
      </Paper>
    </Box>
  )
}

export default FairnessReport

