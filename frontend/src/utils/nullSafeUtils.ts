/**
 * Utility functions for safe handling of potentially null/undefined values
 */

/**
 * Safely converts a string to uppercase, handling null/undefined values
 */
export const safeToUpperCase = (value: string | null | undefined, fallback: string = 'N/A'): string => {
  return value?.toUpperCase() || fallback;
};

/**
 * Safely formats a string by replacing underscores with spaces and capitalizing words
 */
export const safeFormatString = (value: string | null | undefined, fallback: string = 'N/A'): string => {
  if (!value) return fallback;
  return value.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
};

/**
 * Safely gets the first character of a string and capitalizes it
 */
export const safeCapitalizeFirst = (value: string | null | undefined, fallback: string = 'N/A'): string => {
  if (!value) return fallback;
  return value.charAt(0).toUpperCase() + value.slice(1);
};

/**
 * Safely formats a number with decimal places
 */
export const safeFormatNumber = (value: number | null | undefined, decimals: number = 1, fallback: string = '0'): string => {
  if (value === null || value === undefined || isNaN(value)) return fallback;
  return value.toFixed(decimals);
};

/**
 * Safely formats a date string
 */
export const safeFormatDate = (dateString: string | null | undefined, fallback: string = 'N/A'): string => {
  if (!dateString) return fallback;
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return fallback;
    return date.toLocaleDateString();
  } catch {
    return fallback;
  }
};

/**
 * Safely gets a nested property value
 */
export const safeGet = <T>(obj: any, path: string, fallback: T): T => {
  try {
    return path.split('.').reduce((current, key) => current?.[key], obj) ?? fallback;
  } catch {
    return fallback;
  }
};

/**
 * Safely converts a value to string
 */
export const safeToString = (value: any, fallback: string = 'N/A'): string => {
  if (value === null || value === undefined) return fallback;
  return String(value);
};
