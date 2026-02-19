import { useSelector } from 'react-redux';
import { RootState } from '../store';

/**
 * Permission strings from backend are "module:action" (e.g. "haccp:view", "documents:delete").
 * Use this hook to gate UI actions by permission.
 */
export function usePermissions() {
  const permissions = useSelector((state: RootState) => state.auth.user?.permissions ?? []) as string[];

  const hasPermission = (module: string, action: string): boolean => {
    if (!permissions || permissions.length === 0) return false;
    const key = `${module.toLowerCase()}:${action.toLowerCase()}`;
    return permissions.some((p) => (p || '').toLowerCase() === key);
  };

  const hasAnyPermission = (module: string, actions: string[]): boolean =>
    actions.some((action) => hasPermission(module, action));

  const canView = (module: string) => hasPermission(module, 'view');
  const canCreate = (module: string) => hasPermission(module, 'create');
  const canUpdate = (module: string) => hasPermission(module, 'update');
  const canDelete = (module: string) => hasPermission(module, 'delete');
  const canApprove = (module: string) => hasPermission(module, 'approve');
  const canExport = (module: string) => hasPermission(module, 'export');

  return {
    permissions,
    hasPermission,
    hasAnyPermission,
    canView,
    canCreate,
    canUpdate,
    canDelete,
    canApprove,
    canExport,
  };
}
