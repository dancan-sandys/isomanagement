import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  alpha,
} from '@mui/material';
import {
  LocalDrink,
  Icecream,
  Cake,
  Restaurant,
  Build,
} from '@mui/icons-material';
import { ProductTemplate } from './types';
import { productTemplates, getTemplateByCategory } from './ProductTemplates';

interface TemplateSelectionDialogProps {
  open: boolean;
  onClose: () => void;
  onSelectTemplate: (template: ProductTemplate) => void;
}

const TemplateSelectionDialog: React.FC<TemplateSelectionDialogProps> = ({
  open,
  onClose,
  onSelectTemplate,
}) => {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'milk': return <LocalDrink />;
      case 'yogurt': return <Icecream />;
      case 'cheese': return <Cake />;
      case 'butter': return <Restaurant />;
      case 'ice_cream': return <Icecream />;
      default: return <Build />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'milk': return 'primary';
      case 'yogurt': return 'secondary';
      case 'cheese': return 'warning';
      case 'butter': return 'success';
      case 'ice_cream': return 'info';
      default: return 'default';
    }
  };

  const filteredTemplates = selectedCategory === 'all' 
    ? productTemplates 
    : getTemplateByCategory(selectedCategory);

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'milk', label: 'Milk Products' },
    { value: 'yogurt', label: 'Yogurt Products' },
    { value: 'cheese', label: 'Cheese Products' },
    { value: 'butter', label: 'Butter Products' },
    { value: 'ice_cream', label: 'Ice Cream' },
    { value: 'custom', label: 'Custom Templates' },
  ];

  const handleSelectTemplate = (template: ProductTemplate) => {
    onSelectTemplate(template);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">Choose Process Template</Typography>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel>Category</InputLabel>
            <Select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              label="Category"
            >
              {categories.map((category) => (
                <MenuItem key={category.value} value={category.value}>
                  {category.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </DialogTitle>
      
      <DialogContent>
        <Grid container spacing={2} sx={{ mt: 1 }}>
          {filteredTemplates.map((template) => (
            <Grid item xs={12} sm={6} md={4} key={template.id}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: 4,
                    bgcolor: alpha('#1976d2', 0.02),
                  },
                }}
                onClick={() => handleSelectTemplate(template)}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center',
                      width: 40,
                      height: 40,
                      borderRadius: '50%',
                      bgcolor: `${getCategoryColor(template.category)}.light`,
                      color: `${getCategoryColor(template.category)}.contrastText`,
                      mr: 2,
                    }}>
                      {getCategoryIcon(template.category)}
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                      <Typography variant="h6" component="h3" gutterBottom>
                        {template.name}
                      </Typography>
                      <Chip
                        size="small"
                        label={template.category.replace('_', ' ').toUpperCase()}
                        color={getCategoryColor(template.category) as any}
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {template.description}
                  </Typography>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 'auto' }}>
                    <Typography variant="caption" color="text.secondary">
                      {template.defaultNodes.length} Steps
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {template.defaultNodes.filter(n => n.data.ccp?.number).length} CCPs
                    </Typography>
                  </Box>
                </CardContent>
                
                <CardActions>
                  <Button
                    fullWidth
                    variant="outlined"
                    size="small"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectTemplate(template);
                    }}
                  >
                    Use Template
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
        
        {filteredTemplates.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body1" color="text.secondary">
              No templates available for the selected category.
            </Typography>
          </Box>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button 
          variant="outlined" 
          onClick={() => handleSelectTemplate(productTemplates.find(t => t.id === 'basic_template')!)}
        >
          Start Blank
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default TemplateSelectionDialog;
