import React, { useEffect, useState } from 'react';
import {
  Box, Card, CardContent, Grid, Typography, Stack, Button, Chip,
  Paper, Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  FormControl, InputLabel, Select, MenuItem, Alert, Avatar, Tooltip,
  List, ListItem, ListItemText, ListItemIcon, Divider, IconButton
} from '@mui/material';
import {
  CalendarToday as CalendarIcon, Schedule as ScheduleIcon, Add as AddIcon,
  Event as EventIcon, Warning as WarningIcon, CheckCircle as CheckCircleIcon,
  Notifications as NotificationsIcon, Person as PersonIcon, Edit as EditIcon,
  Delete as DeleteIcon, Refresh as RefreshIcon, Today as TodayIcon,
  ChevronLeft as ChevronLeftIcon, ChevronRight as ChevronRightIcon
} from '@mui/icons-material';
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, eachDayOfInterval, 
         isSameMonth, isSameDay, addMonths, addWeeks, subMonths, subWeeks, 
         getDay, isToday, parseISO } from 'date-fns';
import managementReviewAPI, { MRPayload } from '../services/managementReviewAPI';

const ManagementReviewCalendar: React.FC = () => {
  const [reviews, setReviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'agenda'>('month');
  const [scheduleDialogOpen, setScheduleDialogOpen] = useState(false);
  
  const [scheduleForm, setScheduleForm] = useState<MRPayload>({
    title: '',
    review_type: 'scheduled',
    review_date: '',
    review_frequency: 'quarterly',
    status: 'planned'
  });

  const loadReviews = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await managementReviewAPI.list();
      const data = resp.data || resp;
      setReviews(data.items || []);
    } catch (e: any) {
      setError(e?.message || 'Failed to load reviews');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReviews();
  }, []);

  const scheduleReview = async () => {
    try {
      await managementReviewAPI.create(scheduleForm);
      setScheduleDialogOpen(false);
      setScheduleForm({
        title: '',
        review_type: 'scheduled',
        review_date: '',
        review_frequency: 'quarterly',
        status: 'planned'
      });
      await loadReviews();
    } catch (e: any) {
      setError(e?.message || 'Failed to schedule review');
    }
  };

  const getUpcomingReviews = () => {
    const now = new Date();
    const upcoming = reviews.filter(review => {
      if (!review.review_date) return false;
      const reviewDate = new Date(review.review_date);
      return reviewDate > now && review.status === 'planned';
    }).sort((a, b) => new Date(a.review_date).getTime() - new Date(b.review_date).getTime());
    
    return upcoming.slice(0, 5); // Next 5 upcoming reviews
  };

  const getOverdueReviews = () => {
    const now = new Date();
    return reviews.filter(review => {
      if (!review.review_date) return false;
      const reviewDate = new Date(review.review_date);
      return reviewDate < now && review.status === 'planned';
    });
  };

  const getReviewsThisMonth = () => {
    const now = new Date();
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);
    const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0);
    
    return reviews.filter(review => {
      if (!review.review_date) return false;
      const reviewDate = new Date(review.review_date);
      return reviewDate >= startOfMonth && reviewDate <= endOfMonth;
    });
  };

  const getNextScheduledReview = () => {
    const upcoming = getUpcomingReviews();
    return upcoming.length > 0 ? upcoming[0] : null;
  };

  const getDaysUntilNext = (dateString: string) => {
    const reviewDate = new Date(dateString);
    const now = new Date();
    const diffTime = reviewDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'success';
      case 'in_progress': return 'warning';
      case 'planned': return 'info';
      default: return 'default';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'emergency': return 'error';
      case 'ad_hoc': return 'warning';
      default: return 'primary';
    }
  };

  // Calendar navigation functions
  const goToPrevious = () => {
    if (viewMode === 'month') {
      setSelectedDate(subMonths(selectedDate, 1));
    } else if (viewMode === 'week') {
      setSelectedDate(subWeeks(selectedDate, 1));
    }
  };

  const goToNext = () => {
    if (viewMode === 'month') {
      setSelectedDate(addMonths(selectedDate, 1));
    } else if (viewMode === 'week') {
      setSelectedDate(addWeeks(selectedDate, 1));
    }
  };

  const goToToday = () => {
    setSelectedDate(new Date());
  };

  // Calendar view functions
  const getMonthDays = () => {
    const start = startOfMonth(selectedDate);
    const end = endOfMonth(selectedDate);
    const startWeek = startOfWeek(start);
    const endWeek = endOfWeek(end);
    return eachDayOfInterval({ start: startWeek, end: endWeek });
  };

  const getWeekDays = () => {
    const start = startOfWeek(selectedDate);
    const end = endOfWeek(selectedDate);
    return eachDayOfInterval({ start, end });
  };

  const getReviewsForDate = (date: Date) => {
    return reviews.filter(review => {
      if (!review.review_date) return false;
      const reviewDate = new Date(review.review_date);
      return isSameDay(reviewDate, date);
    });
  };

  const renderMonthView = () => {
    const days = getMonthDays();
    const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    return (
      <Box>
        {/* Calendar Header */}
        <Grid container sx={{ mb: 2 }}>
          {weekDays.map(day => (
            <Grid item xs key={day} sx={{ textAlign: 'center', py: 1 }}>
              <Typography variant="subtitle2" fontWeight="bold" color="text.secondary">
                {day}
              </Typography>
            </Grid>
          ))}
        </Grid>

        {/* Calendar Grid */}
        <Grid container>
          {days.map((day, index) => {
            const dayReviews = getReviewsForDate(day);
            const isCurrentMonth = isSameMonth(day, selectedDate);
            const isCurrentDay = isToday(day);

            return (
              <Grid 
                item 
                xs 
                key={index}
                sx={{
                  minHeight: 120,
                  border: '1px solid',
                  borderColor: 'divider',
                  p: 1,
                  bgcolor: isCurrentDay ? 'action.hover' : 'background.paper',
                  opacity: isCurrentMonth ? 1 : 0.5
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontWeight: isCurrentDay ? 'bold' : 'normal',
                      color: isCurrentDay ? 'primary.main' : 'text.primary'
                    }}
                  >
                    {format(day, 'd')}
                  </Typography>
                  {dayReviews.length > 0 && (
                    <Chip 
                      label={dayReviews.length} 
                      size="small" 
                      color="primary" 
                      sx={{ minWidth: 20, height: 20 }}
                    />
                  )}
                </Box>

                {/* Events for this day */}
                <Box sx={{ maxHeight: 80, overflow: 'hidden' }}>
                  {dayReviews.slice(0, 2).map((review) => (
                    <Box 
                      key={review.id}
                      sx={{
                        bgcolor: getStatusColor(review.status) === 'success' ? 'success.light' : 
                                getStatusColor(review.status) === 'warning' ? 'warning.light' : 'info.light',
                        color: 'text.primary',
                        p: 0.5,
                        mb: 0.5,
                        borderRadius: 1,
                        fontSize: '0.75rem',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        cursor: 'pointer',
                        '&:hover': {
                          bgcolor: getStatusColor(review.status) === 'success' ? 'success.main' : 
                                  getStatusColor(review.status) === 'warning' ? 'warning.main' : 'info.main',
                          color: 'white'
                        }
                      }}
                      title={`${review.title} - ${review.status}`}
                    >
                      {review.title}
                    </Box>
                  ))}
                  {dayReviews.length > 2 && (
                    <Typography variant="caption" color="text.secondary">
                      +{dayReviews.length - 2} more
                    </Typography>
                  )}
                </Box>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    );
  };

  const renderWeekView = () => {
    const days = getWeekDays();
    const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

    return (
      <Box>
        {/* Week Header */}
        <Grid container sx={{ mb: 2 }}>
          {weekDays.map((day, index) => (
            <Grid item xs key={day} sx={{ textAlign: 'center', py: 1 }}>
              <Typography variant="subtitle2" fontWeight="bold" color="text.secondary">
                {day}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {format(days[index], 'MMM d')}
              </Typography>
            </Grid>
          ))}
        </Grid>

        {/* Week Grid */}
        <Grid container>
          {days.map((day, index) => {
            const dayReviews = getReviewsForDate(day);
            const isCurrentDay = isToday(day);

            return (
              <Grid 
                item 
                xs 
                key={index}
                sx={{
                  minHeight: 200,
                  border: '1px solid',
                  borderColor: 'divider',
                  p: 1,
                  bgcolor: isCurrentDay ? 'action.hover' : 'background.paper'
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                  <Typography 
                    variant="body2" 
                    sx={{ 
                      fontWeight: isCurrentDay ? 'bold' : 'normal',
                      color: isCurrentDay ? 'primary.main' : 'text.primary'
                    }}
                  >
                    {format(day, 'd')}
                  </Typography>
                  {dayReviews.length > 0 && (
                    <Chip 
                      label={dayReviews.length} 
                      size="small" 
                      color="primary" 
                      sx={{ minWidth: 20, height: 20 }}
                    />
                  )}
                </Box>

                {/* Events for this day */}
                <Box>
                  {dayReviews.map((review) => (
                    <Box 
                      key={review.id}
                      sx={{
                        bgcolor: getStatusColor(review.status) === 'success' ? 'success.light' : 
                                getStatusColor(review.status) === 'warning' ? 'warning.light' : 'info.light',
                        color: 'text.primary',
                        p: 1,
                        mb: 1,
                        borderRadius: 1,
                        fontSize: '0.75rem',
                        cursor: 'pointer',
                        '&:hover': {
                          bgcolor: getStatusColor(review.status) === 'success' ? 'success.main' : 
                                  getStatusColor(review.status) === 'warning' ? 'warning.main' : 'info.main',
                          color: 'white'
                        }
                      }}
                      title={`${review.title} - ${review.status}`}
                    >
                      <Typography variant="caption" display="block" fontWeight="bold">
                        {review.title}
                      </Typography>
                      <Typography variant="caption" display="block">
                        {review.status}
                      </Typography>
                      {review.review_date && (
                        <Typography variant="caption" display="block" color="text.secondary">
                          {format(new Date(review.review_date), 'HH:mm')}
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Box>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    );
  };

  const upcomingReviews = getUpcomingReviews();
  const overdueReviews = getOverdueReviews();
  const thisMonthReviews = getReviewsThisMonth();
  const nextReview = getNextScheduledReview();

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 3 }}>
        <Box>
          <Typography variant="h4" gutterBottom>Review Calendar & Scheduling</Typography>
          <Typography variant="subtitle1" color="text.secondary">
            Plan and track management review schedules for ISO compliance
          </Typography>
        </Box>
        <Stack direction="row" spacing={2}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={loadReviews}>
            Refresh
          </Button>
          <Button variant="contained" startIcon={<AddIcon />} onClick={() => setScheduleDialogOpen(true)}>
            Schedule Review
          </Button>
        </Stack>
      </Stack>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Quick Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <CalendarIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">{reviews.length}</Typography>
                  <Typography variant="body2" color="text.secondary">Total Reviews</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: 'info.main' }}>
                  <ScheduleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">{upcomingReviews.length}</Typography>
                  <Typography variant="body2" color="text.secondary">Upcoming</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <TodayIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">{thisMonthReviews.length}</Typography>
                  <Typography variant="body2" color="text.secondary">This Month</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Stack direction="row" alignItems="center" spacing={2}>
                <Avatar sx={{ bgcolor: overdueReviews.length > 0 ? 'error.main' : 'success.main' }}>
                  <WarningIcon />
                </Avatar>
                <Box>
                  <Typography variant="h4">{overdueReviews.length}</Typography>
                  <Typography variant="body2" color="text.secondary">Overdue</Typography>
                </Box>
              </Stack>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Overdue Reviews Alert */}
      {overdueReviews.length > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <Typography variant="subtitle2">
            {overdueReviews.length} review{overdueReviews.length > 1 ? 's are' : ' is'} overdue. 
            Please reschedule or complete immediately.
          </Typography>
        </Alert>
      )}

      {/* Next Review Alert */}
      {nextReview && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="subtitle2">
            Next review "{nextReview.title}" is scheduled for{' '}
            {new Date(nextReview.review_date).toLocaleDateString()} 
            ({getDaysUntilNext(nextReview.review_date)} days from now)
          </Typography>
        </Alert>
      )}

      {/* Main Content */}
      <Grid container spacing={3}>
        {/* Calendar View */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Typography variant="h6">Review Schedule</Typography>
              <FormControl size="small">
                <Select
                  value={viewMode}
                  onChange={(e) => setViewMode(e.target.value as any)}
                >
                  <MenuItem value="month">Month View</MenuItem>
                  <MenuItem value="week">Week View</MenuItem>
                  <MenuItem value="agenda">Agenda View</MenuItem>
                </Select>
              </FormControl>
            </Stack>

            {/* Calendar Navigation */}
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Stack direction="row" spacing={1}>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<ChevronLeftIcon />}
                  onClick={goToPrevious}
                >
                  Previous
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={goToToday}
                >
                  Today
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  endIcon={<ChevronRightIcon />}
                  onClick={goToNext}
                >
                  Next
                </Button>
              </Stack>
              
              <Typography variant="h6" color="primary">
                {viewMode === 'month' 
                  ? format(selectedDate, 'MMMM yyyy')
                  : viewMode === 'week'
                  ? `${format(startOfWeek(selectedDate), 'MMM d')} - ${format(endOfWeek(selectedDate), 'MMM d, yyyy')}`
                  : 'Agenda View'
                }
              </Typography>
            </Stack>
            
            {viewMode === 'agenda' ? (
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 2 }}>Scheduled Reviews</Typography>
                <List>
                  {reviews
                    .filter(r => r.review_date)
                    .sort((a, b) => new Date(a.review_date).getTime() - new Date(b.review_date).getTime())
                    .map((review) => (
                    <ListItem key={review.id} divider>
                      <ListItemIcon>
                        <EventIcon color={getTypeColor(review.review_type)} />
                      </ListItemIcon>
                      <ListItemText
                        primary={
                          <Stack direction="row" alignItems="center" spacing={1}>
                            <Typography variant="subtitle2">{review.title}</Typography>
                            <Chip label={review.status} color={getStatusColor(review.status)} size="small" />
                            <Chip label={review.review_type} variant="outlined" size="small" />
                          </Stack>
                        }
                        secondary={
                          <Stack direction="row" alignItems="center" spacing={2} sx={{ mt: 0.5 }}>
                            <Typography variant="body2">
                              {new Date(review.review_date).toLocaleDateString()} at{' '}
                              {new Date(review.review_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </Typography>
                            {isOverdue(review) && (
                              <Chip label="Overdue" color="error" size="small" />
                            )}
                            {getDaysUntilNext(review.review_date) <= 7 && getDaysUntilNext(review.review_date) > 0 && (
                              <Chip label="Due Soon" color="warning" size="small" />
                            )}
                          </Stack>
                        }
                      />
                      <Stack direction="row" spacing={1}>
                        <IconButton size="small">
                          <EditIcon />
                        </IconButton>
                        {review.status === 'planned' && (
                          <Button size="small" variant="outlined">
                            Start
                          </Button>
                        )}
                      </Stack>
                    </ListItem>
                  ))}
                </List>
              </Box>
            ) : viewMode === 'month' ? (
              renderMonthView()
            ) : (
              renderWeekView()
            )}
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          <Stack spacing={3}>
            {/* Upcoming Reviews */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  <Stack direction="row" alignItems="center" spacing={1}>
                    <ScheduleIcon color="primary" />
                    <span>Upcoming Reviews</span>
                  </Stack>
                </Typography>
                {upcomingReviews.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">
                    No upcoming reviews scheduled
                  </Typography>
                ) : (
                  <List dense>
                    {upcomingReviews.map((review) => (
                      <ListItem key={review.id} divider>
                        <ListItemText
                          primary={review.title}
                          secondary={
                            <Stack direction="row" alignItems="center" spacing={1}>
                              <Typography variant="caption">
                                {new Date(review.review_date).toLocaleDateString()}
                              </Typography>
                              <Chip 
                                label={`${getDaysUntilNext(review.review_date)} days`} 
                                size="small" 
                                variant="outlined"
                              />
                            </Stack>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </CardContent>
            </Card>

            {/* Overdue Reviews */}
            {overdueReviews.length > 0 && (
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom color="error">
                    <Stack direction="row" alignItems="center" spacing={1}>
                      <WarningIcon color="error" />
                      <span>Overdue Reviews</span>
                    </Stack>
                  </Typography>
                  <List dense>
                    {overdueReviews.map((review) => (
                      <ListItem key={review.id} divider>
                        <ListItemText
                          primary={review.title}
                          secondary={
                            <Typography variant="caption" color="error">
                              {Math.abs(getDaysUntilNext(review.review_date))} days overdue
                            </Typography>
                          }
                        />
                        <Button size="small" color="error">
                          Reschedule
                        </Button>
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            )}

            {/* Review Frequency Guide */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>ISO 22000:2018 Guidelines</Typography>
                <Stack spacing={2}>
                  <Box>
                    <Typography variant="subtitle2" color="primary">Recommended Frequency</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Management reviews should be conducted at planned intervals, typically:
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Quarterly Reviews" 
                          secondary="For comprehensive FSMS evaluation"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Annual Reviews" 
                          secondary="For strategic planning and policy review"
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Ad-hoc Reviews" 
                          secondary="For significant changes or incidents"
                        />
                      </ListItem>
                    </List>
                  </Box>
                  
                  <Divider />
                  
                  <Box>
                    <Typography variant="subtitle2" color="warning.main">Required Inputs</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Ensure these inputs are available before each review:
                    </Typography>
                    <List dense>
                      <ListItem>
                        <ListItemIcon><CheckCircleIcon fontSize="small" /></ListItemIcon>
                        <ListItemText primary="Audit results" />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircleIcon fontSize="small" /></ListItemIcon>
                        <ListItemText primary="NC/CAPA status" />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircleIcon fontSize="small" /></ListItemIcon>
                        <ListItemText primary="Supplier performance" />
                      </ListItem>
                      <ListItem>
                        <ListItemIcon><CheckCircleIcon fontSize="small" /></ListItemIcon>
                        <ListItemText primary="HACCP/PRP monitoring" />
                      </ListItem>
                    </List>
                  </Box>
                </Stack>
              </CardContent>
            </Card>
          </Stack>
        </Grid>
      </Grid>

      {/* Schedule Review Dialog */}
      <Dialog open={scheduleDialogOpen} onClose={() => setScheduleDialogOpen(false)} fullWidth maxWidth="md">
        <DialogTitle>
          <Stack direction="row" alignItems="center" spacing={1}>
            <ScheduleIcon />
            <Typography variant="h6">Schedule Management Review</Typography>
          </Stack>
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={8}>
              <TextField
                label="Review Title"
                fullWidth
                value={scheduleForm.title}
                onChange={(e) => setScheduleForm({ ...scheduleForm, title: e.target.value })}
                required
                placeholder="e.g., Q1 2024 Management Review"
              />
            </Grid>
            
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Review Type</InputLabel>
                <Select
                  value={scheduleForm.review_type || 'scheduled'}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, review_type: e.target.value as any })}
                  label="Review Type"
                >
                  <MenuItem value="scheduled">Scheduled</MenuItem>
                  <MenuItem value="ad_hoc">Ad Hoc</MenuItem>
                  <MenuItem value="emergency">Emergency</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <TextField
                label="Review Date & Time"
                type="datetime-local"
                fullWidth
                InputLabelProps={{ shrink: true }}
                value={scheduleForm.review_date || ''}
                onChange={(e) => setScheduleForm({ ...scheduleForm, review_date: e.target.value })}
                required
              />
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Review Frequency</InputLabel>
                <Select
                  value={scheduleForm.review_frequency || 'quarterly'}
                  onChange={(e) => setScheduleForm({ ...scheduleForm, review_frequency: e.target.value })}
                  label="Review Frequency"
                >
                  <MenuItem value="monthly">Monthly</MenuItem>
                  <MenuItem value="quarterly">Quarterly</MenuItem>
                  <MenuItem value="semi_annually">Semi-Annually</MenuItem>
                  <MenuItem value="annually">Annually</MenuItem>
                  <MenuItem value="ad_hoc">As Needed</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                label="Review Scope"
                fullWidth
                multiline
                rows={3}
                value={scheduleForm.review_scope || ''}
                onChange={(e) => setScheduleForm({ ...scheduleForm, review_scope: e.target.value })}
                placeholder="Define the scope and areas to be covered in this review..."
              />
            </Grid>
            
            <Grid item xs={12}>
              <Alert severity="info">
                <Typography variant="body2">
                  <strong>ISO 22000:2018 Reminder:</strong> Management reviews must be conducted at planned intervals 
                  to ensure the continuing suitability, adequacy, effectiveness, and alignment of the FSMS 
                  with the organization's strategic direction.
                </Typography>
              </Alert>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setScheduleDialogOpen(false)}>Cancel</Button>
          <Button 
            variant="contained" 
            onClick={scheduleReview} 
            disabled={!scheduleForm.title || !scheduleForm.review_date}
          >
            Schedule Review
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

// Helper function to check if a review is overdue
const isOverdue = (review: any) => {
  if (!review.review_date || review.status !== 'planned') return false;
  return new Date(review.review_date) < new Date();
};

export default ManagementReviewCalendar;