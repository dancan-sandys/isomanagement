## Project Styling Checklist

Short, actionable checklist to align UI/UX across the app. Use - [ ] to track progress. File paths refer to `frontend/` unless noted.

### Theme and Design System
- [ ] Consolidate to a single theme provider
  - [ ] Remove the ad-hoc MUI theme in `src/index.tsx` and wrap the app with `src/theme/ThemeProvider.tsx` only
  - [ ] Migrate any palette/typography/component overrides from `src/index.tsx` to `src/theme/designSystem.ts`
  - [ ] Ensure `CssBaseline` is applied only once by the custom provider
- [ ] Align global tokens in `src/theme/designSystem.ts`
  - [ ] Validate `PROFESSIONAL_COLORS` against brand and accessibility
  - [ ] Confirm `TYPOGRAPHY` scale and weights
  - [ ] Normalize elevations to light/medium/heavy presets
- [ ] Ensure all components use theme tokens (spacing, radius, colors) instead of hardcoded values

### Navigation and Information Architecture
- [ ] Hide or gate “Coming Soon” items from the sidebar by default
  - [ ] Keep routes accessible for deep-links but remove menu entries with `comingSoon: true` in `src/theme/navigationConfig.ts`
  - [ ] Optionally show behind a feature flag (e.g., `REACT_APP_SHOW_EXPERIMENTAL`)
- [ ] Enforce role-based visibility consistently between routes and menu
  - [ ] Cross-check `RoleBasedRoute` usage matches `getNavigationForUser`

### Loading, Empty, and Error States
- [ ] Create shared components: `Loader`, `EmptyState`, `ErrorState` in `src/components/UI/`
  - [ ] Replace plain text loaders with MUI `CircularProgress`/Skeletons
  - [ ] Replace repeated inline error/empty UIs with shared components
- [ ] Use skeletons for data-heavy pages (tables, detail panels)
  - [ ] Apply in Suppliers, Documents, HACCP dashboards
- [ ] Replace AuthProvider inline loader with shared `Loader`
  - [ ] File: `src/components/Auth/AuthProvider.tsx`

### Forms and Validation
- [ ] Standardize on Formik + Yup for all forms (where feasible)
  - [ ] Convert manual validation in dialogs (e.g. `BatchRegistrationForm`) to Yup schema
- [ ] Unify error/helper text placement and success feedback
  - [ ] Ensure consistent `helperText`, `error` usage across Login, Signup, app forms
- [ ] Add a shared `ConfirmDialog` for destructive/irreversible actions
  - [ ] Integrate with table row deletes and bulk actions

### Accessibility (WCAG 2.1 AA)
- [ ] Add `aria-label` or `aria-labelledby` to all `IconButton`s (AppBar, Drawer, Dialog actions)
- [ ] Manage focus on route changes, dialog open/close, and after redirects
- [ ] Verify color contrast of status chips, gradients, and text on colored surfaces
- [ ] Add a "Skip to content" link and landmark roles (header/nav/main)
- [ ] Set `document.title` per route (e.g., with a small hook)
- [ ] Ensure keyboard navigation and focus rings are visible

### Performance and Scalability
- [ ] Implement route-based code splitting
  - [ ] Convert page imports in `src/App.tsx` to `React.lazy` with `Suspense` fallback
- [ ] Add pagination to `DataTable` and support server-side mode
  - [ ] Consider virtualization for large datasets (MUI DataGrid or react-window)
- [ ] Debounce/throttle search inputs consistently (reuse a shared hook)

### Content and Copy
- [ ] Remove demo credentials from Login in production builds
  - [ ] File: `src/pages/Login.tsx` (conditional render via `REACT_APP_ENVIRONMENT`)
- [ ] Standardize empty-state copy and CTAs
- [ ] Prefer action-oriented error copy with recovery steps

### Consistency and Polish
- [ ] Adopt design-system elevations, spacings, and radii everywhere
  - [ ] Replace ad-hoc shadows and hardcoded paddings
- [ ] Keep animations subtle; reduce bounce/pulse where distracting
- [ ] Ensure consistent AppBar and Drawer styling across light/dark modes

### Notifications and Toasts
- [ ] Ensure toasts use `aria-live="polite"` and don’t obscure primary actions
- [ ] Provide clear action buttons (e.g., View, Dismiss) for long-running alerts
- [ ] Timeouts consistent across app; avoid stacking duplicates

### Mobile Responsiveness
- [ ] Validate all pages at `sm`/`md` breakpoints
  - [ ] Sidebar behavior already responsive; verify content grids/tables
- [ ] Define responsive column hiding/stacking in tables

### Error Boundaries and Resilience
- [ ] Add a global error boundary with a friendly fallback
- [ ] Add route-level error boundaries for critical pages

### Page Titles and Metadata
- [ ] Add a small hook to update `document.title` based on route and content

### Code Hygiene and Cleanups
- [ ] Remove unused/temporary files (e.g., `src/pages/e.tsx`)
- [ ] Remove unused imports and dead code
- [ ] Move global CSS patterns into theme where possible

---

## Card Styling Guidelines (and Suppliers Module Fixes)

Objective: reduce overly rounded cards and enforce consistent card styles across the app.

### Global Card Tokens (Design System)
- [ ] Set a sane global radius
  - [ ] `shape.borderRadius` = 12 in `src/theme/designSystem.ts`
  - [ ] `COMPONENT_STYLES.card.borderRadius` = 12
  - [ ] `COMPONENT_STYLES.elevatedCard.borderRadius` = 16
  - [ ] `MuiPaper.styleOverrides.root.borderRadius` = 12–16 (match card usage)
- [ ] Unify hover/press states
  - [ ] Limit translateY to 1–2px on hover; keep shadows subtle
  - [ ] Remove excessive glow where it competes with content

### EnhancedCard Component Standardization
Files: `src/components/UI/EnhancedCard.tsx`
- [ ] Reduce default rounding
  - [ ] Default card: border radius 12
  - [ ] Featured card: border radius 16
- [ ] Respect global design tokens
  - [ ] Use theme spacing and shadows; no hardcoded radii or colors where tokens exist
- [ ] Keep animations minimal (fade/grow preferred)

### Suppliers Module Adjustments (too rounded)
Files: `src/components/Suppliers/`
- [ ] Audit all card usages (`SupplierDashboard.tsx`, `SupplierList.tsx`, `SupplierForm.tsx`)
  - [ ] Ensure they use `EnhancedCard` or `Paper` with radius 12 (featured at 16)
  - [ ] Remove any local `sx={{ borderRadius: 20+ }}` overrides
  - [ ] Align elevations to `light` or `medium` presets
- [ ] Verify nested elements (chips, progress bars) don’t introduce conflicting radii

### Tables and Containers
- [ ] Ensure `Paper` wrapping tables uses radius 12 and consistent borders
- [ ] Keep table header cells squared if content alignment is affected by rounding

### Quick Visual QA Checklist
- [ ] Cards don’t appear “pill-shaped” on desktop
- [ ] Consistent spacing: 16–24px internal padding depending on density
- [ ] Content readability prioritized over decorative gradients
- [ ] Light/dark mode parity for surfaces and shadows

---

## Implementation References

- Theme Provider consolidation
  - `src/index.tsx` (remove local `createTheme` and wrap with `src/theme/ThemeProvider.tsx`)
  - `src/theme/designSystem.ts` (single source of truth)
- Navigation
  - `src/theme/navigationConfig.ts` (remove menu items with `comingSoon: true` or guard behind flag)
- Shared UI components
  - `src/components/UI/Loader.tsx` (new)
  - `src/components/UI/EmptyState.tsx` (new)
  - `src/components/UI/ErrorState.tsx` (new)
  - `src/components/UI/ConfirmDialog.tsx` (new)
- DataTable
  - `src/components/UI/DataTable.tsx` (add pagination, optional server-side hooks; add skeletons)
- Accessibility
  - AppBar/Drawer buttons in `src/components/Layout/*`
  - Add page title hook, skip link in layout

---

Notes
- When implementing, prefer incremental PRs per section (Theme, Nav, Tables, Forms) to keep diffs clear and testable.
- Validate changes with quick visual snapshots in light/dark mode and at sm/md breakpoints.


