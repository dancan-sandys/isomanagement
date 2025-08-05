# ISO 22000 FSMS - Frontend Application

A comprehensive Food Safety Management System frontend built with React, TypeScript, and Material-UI, designed specifically for ISO 22000:2018 compliance and audit-readiness.

## 🎯 Design Philosophy

This application is built with the following core principles:

- **Audit-Ready**: Every interface element is designed for compliance documentation and traceability
- **Professional**: Clean, structured design that reflects the rigor of certified environments
- **Role-Based**: Tailored dashboards and interfaces for different user types (QA Manager, Operator, Auditor, Executive)
- **ISO 22000 Aligned**: Navigation and terminology follow ISO 22000:2018 structure

## 🎨 Design System

### Color Palette

The application uses a professional color scheme optimized for audit environments:

```typescript
// ISO Status Colors
compliant: '#2E7D32'      // Green - Compliant/Completed
nonConformance: '#D32F2F' // Red - Non-conformance/Urgent
pending: '#F57C00'        // Orange - Pending/Needs Review
warning: '#FF8F00'        // Yellow - Warning
info: '#1976D2'           // Blue - Information

// Professional Colors
primary: '#1E3A8A'        // Navy Blue
secondary: '#64748B'      // Slate Gray
background: '#F8FAFC'     // Light Gray
```

### Typography

Uses Inter and Roboto fonts for optimal readability in professional environments:

```typescript
fontFamily: '"Inter", "Roboto", "Helvetica Neue", Arial, sans-serif'
```

### Component System

#### Core Components

1. **StatusChip** - ISO status indicators with proper color coding
2. **PageHeader** - Consistent page headers with breadcrumbs and actions
3. **DataTable** - Audit-ready tables with sorting, filtering, and export
4. **QuickSearch** - Global search with typeahead functionality
5. **DashboardCard** - Reusable dashboard widgets

#### Usage Example

```typescript
import { StatusChip, PageHeader, DataTable } from '../components/UI';

// Status indicators
<StatusChip status="compliant" label="Approved" />

// Page headers with breadcrumbs
<PageHeader
  title="HACCP System"
  subtitle="Hazard Analysis and Critical Control Points"
  breadcrumbs={[
    { label: 'Dashboard', path: '/' },
    { label: 'HACCP', path: '/haccp' }
  ]}
  showAdd
  onAdd={() => handleAdd()}
/>

// Data tables with ISO styling
<DataTable
  data={ccpData}
  columns={columns}
  title="Critical Control Points"
  onRowClick={handleRowClick}
  onEdit={handleEdit}
  onExport={handleExport}
/>
```

## 🏗️ Architecture

### Theme System

The application uses a comprehensive theme system with:

- **Light/Dark Mode Support**: Toggle between light and dark themes
- **ISO-Specific Styling**: Professional colors and typography
- **Component Overrides**: Consistent styling across all components
- **CSS Variables**: Easy theme customization

### Navigation Structure

Follows ISO 22000:2018 structure:

```
FSMS Framework
├── Context & Leadership
├── Planning
├── Support
├── Operation
├── Performance Evaluation
└── Improvement

HACCP System
├── HACCP Team
├── Product Description
├── Process Flow Diagrams
├── Hazard Analysis
├── CCP Determination
├── Critical Limits
├── Monitoring System
├── Corrective Actions
├── Verification Procedures
└── Documentation

PRP Programs
├── Infrastructure
├── Maintenance
├── Cleaning & Sanitation
├── Pest Control
├── Personal Hygiene
├── Training
├── Supplier Management
└── Traceability
```

### Role-Based Dashboards

#### QA Manager Dashboard
- Non-conformance trends
- CAPA deadlines
- Document version alerts
- Audit schedule

#### Operator Dashboard
- Today's tasks
- Checklist reminders
- Quick input forms
- Recent activities

#### Auditor Dashboard
- Compliance scorecards
- Audit logs
- Evidence review panel
- Findings summary

#### Executive Dashboard
- Audit success rate
- Open CAPAs
- Compliance overview
- Risk assessment

## 🚀 Getting Started

### Prerequisites

- Node.js 16+
- npm or yarn
- React 18+
- TypeScript 4.9+

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

## 📁 Project Structure

```
src/
├── components/
│   ├── UI/                 # Reusable UI components
│   │   ├── StatusChip.tsx
│   │   ├── PageHeader.tsx
│   │   ├── DataTable.tsx
│   │   ├── QuickSearch.tsx
│   │   └── index.ts
│   ├── Dashboard/          # Dashboard components
│   │   ├── DashboardCard.tsx
│   │   └── index.ts
│   ├── Layout/            # Layout components
│   │   └── Layout.tsx
│   └── Auth/              # Authentication components
├── pages/                 # Page components
│   ├── Dashboard.tsx
│   ├── HACCP.tsx
│   ├── Documents.tsx
│   └── ...
├── theme/                 # Design system
│   ├── designSystem.ts
│   └── ThemeProvider.tsx
├── store/                 # Redux store
├── services/              # API services
└── utils/                 # Utility functions
```

## 🎯 Key Features

### 1. Audit-Ready Interface
- Consistent status indicators
- Comprehensive audit trails
- Export capabilities
- Version control

### 2. Role-Based Access
- Tailored dashboards per user role
- Appropriate data visibility
- Role-specific actions

### 3. ISO 22000 Compliance
- Proper terminology usage
- Structured navigation
- Compliance tracking
- Document management

### 4. Mobile Responsive
- Mobile-friendly cards
- Responsive tables
- Touch-optimized interactions

### 5. Accessibility
- WCAG 2.1 compliance
- Keyboard navigation
- Screen reader support
- High contrast mode

## 🔧 Customization

### Adding New Components

1. Create component in appropriate directory
2. Follow naming conventions
3. Add to index.ts exports
4. Include TypeScript interfaces
5. Add to storybook (if applicable)

### Theme Customization

```typescript
// Modify theme colors
const customTheme = createISOTheme('light');
customTheme.palette.primary.main = '#your-color';

// Add custom component styles
customTheme.components.MuiButton = {
  styleOverrides: {
    root: {
      // Your custom styles
    }
  }
};
```

### Adding New Pages

1. Create page component
2. Add route in App.tsx
3. Add navigation item in Layout.tsx
4. Include proper breadcrumbs
5. Add to role-based access control

## 📊 Performance

### Optimization Strategies

- **Code Splitting**: Lazy loading of routes
- **Memoization**: React.memo for expensive components
- **Virtualization**: For large data tables
- **Image Optimization**: WebP format support
- **Bundle Analysis**: Regular bundle size monitoring

### Monitoring

- Performance metrics tracking
- Error boundary implementation
- User interaction analytics
- Load time optimization

## 🧪 Testing

### Testing Strategy

```bash
# Run unit tests
npm test

# Run integration tests
npm run test:integration

# Run e2e tests
npm run test:e2e

# Generate coverage report
npm run test:coverage
```

### Test Structure

```
__tests__/
├── components/           # Component tests
├── pages/               # Page tests
├── utils/               # Utility tests
└── integration/         # Integration tests
```

## 🚀 Deployment

### Production Build

```bash
# Create production build
npm run build

# Analyze bundle size
npm run analyze

# Deploy to hosting platform
npm run deploy
```

### Environment Configuration

- Production API endpoints
- CDN configuration
- Error tracking setup
- Performance monitoring

## 📚 Documentation

### API Documentation
- RESTful API endpoints
- Request/response schemas
- Authentication methods
- Error handling

### User Documentation
- Role-based user guides
- Feature walkthroughs
- Troubleshooting guides
- Best practices

## 🤝 Contributing

### Development Workflow

1. Create feature branch
2. Implement changes
3. Add tests
4. Update documentation
5. Submit pull request

### Code Standards

- TypeScript strict mode
- ESLint configuration
- Prettier formatting
- Conventional commits

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- **Documentation**: Check the docs folder
- **Issues**: Create GitHub issue
- **Email**: support@example.com
- **Slack**: #iso22000-fsms

## 🔄 Changelog

### Version 1.0.0
- Initial release
- ISO 22000 compliant design system
- Role-based dashboards
- Document management
- HACCP system interface

---

**Built with ❤️ for Food Safety Management** 