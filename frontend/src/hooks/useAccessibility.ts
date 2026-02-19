import { useEffect, useState } from 'react';
import { useTheme } from '@mui/material/styles';

interface AccessibilityPreferences {
  reducedMotion: boolean;
  highContrast: boolean;
  fontSize: 'small' | 'medium' | 'large' | 'xl';
  screenReader: boolean;
  keyboardNavigation: boolean;
}

interface AccessibilityState {
  preferences: AccessibilityPreferences;
  isKeyboardUser: boolean;
  focusVisible: boolean;
}

export const useAccessibility = () => {
  const theme = useTheme();
  const [accessibilityState, setAccessibilityState] = useState<AccessibilityState>({
    preferences: {
      reducedMotion: false,
      highContrast: false,
      fontSize: 'medium',
      screenReader: false,
      keyboardNavigation: false,
    },
    isKeyboardUser: false,
    focusVisible: false,
  });

  useEffect(() => {
    // Detect user preferences from system and localStorage
    const detectPreferences = () => {
      const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      const highContrast = window.matchMedia('(prefers-contrast: high)').matches;
      const storedFontSize = localStorage.getItem('accessibility-font-size') as AccessibilityPreferences['fontSize'] || 'medium';
      const storedKeyboardNav = localStorage.getItem('accessibility-keyboard') === 'true';

      setAccessibilityState(prev => ({
        ...prev,
        preferences: {
          ...prev.preferences,
          reducedMotion,
          highContrast,
          fontSize: storedFontSize,
          keyboardNavigation: storedKeyboardNav,
        },
      }));
    };

    detectPreferences();

    // Listen for preference changes
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const contrastQuery = window.matchMedia('(prefers-contrast: high)');

    const handleMotionChange = (e: MediaQueryListEvent) => {
      setAccessibilityState(prev => ({
        ...prev,
        preferences: { ...prev.preferences, reducedMotion: e.matches },
      }));
    };

    const handleContrastChange = (e: MediaQueryListEvent) => {
      setAccessibilityState(prev => ({
        ...prev,
        preferences: { ...prev.preferences, highContrast: e.matches },
      }));
    };

    motionQuery.addEventListener('change', handleMotionChange);
    contrastQuery.addEventListener('change', handleContrastChange);

    return () => {
      motionQuery.removeEventListener('change', handleMotionChange);
      contrastQuery.removeEventListener('change', handleContrastChange);
    };
  }, []);

  useEffect(() => {
    // Detect keyboard users
    let isUsingKeyboard = false;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Tab') {
        isUsingKeyboard = true;
        setAccessibilityState(prev => ({ ...prev, isKeyboardUser: true }));
        document.body.classList.add('keyboard-user');
      }
    };

    const handleMouseDown = () => {
      if (isUsingKeyboard) {
        isUsingKeyboard = false;
        setAccessibilityState(prev => ({ ...prev, isKeyboardUser: false }));
        document.body.classList.remove('keyboard-user');
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleMouseDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, []);

  useEffect(() => {
    // Apply accessibility styles to document
    const { reducedMotion, highContrast, fontSize } = accessibilityState.preferences;

    // Font size
    const fontSizeMap = {
      small: '14px',
      medium: '16px',
      large: '18px',
      xl: '20px',
    };
    document.documentElement.style.setProperty('--base-font-size', fontSizeMap[fontSize]);

    // Reduced motion
    if (reducedMotion) {
      document.documentElement.style.setProperty('--animation-duration', '0.01ms');
      document.documentElement.style.setProperty('--transition-duration', '0.01ms');
    } else {
      document.documentElement.style.setProperty('--animation-duration', '');
      document.documentElement.style.setProperty('--transition-duration', '');
    }

    // High contrast
    if (highContrast) {
      document.body.classList.add('high-contrast');
    } else {
      document.body.classList.remove('high-contrast');
    }
  }, [accessibilityState.preferences]);

  const updateFontSize = (size: AccessibilityPreferences['fontSize']) => {
    localStorage.setItem('accessibility-font-size', size);
    setAccessibilityState(prev => ({
      ...prev,
      preferences: { ...prev.preferences, fontSize: size },
    }));
  };

  const toggleKeyboardNavigation = () => {
    const newValue = !accessibilityState.preferences.keyboardNavigation;
    localStorage.setItem('accessibility-keyboard', newValue.toString());
    setAccessibilityState(prev => ({
      ...prev,
      preferences: { ...prev.preferences, keyboardNavigation: newValue },
    }));
  };

  const announceToScreenReader = (message: string) => {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.style.position = 'absolute';
    announcement.style.left = '-10000px';
    announcement.style.width = '1px';
    announcement.style.height = '1px';
    announcement.style.overflow = 'hidden';
    announcement.textContent = message;

    document.body.appendChild(announcement);

    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  const getAccessibleProps = (element: 'button' | 'link' | 'input' | 'dialog') => {
    const baseProps: any = {};

    if (accessibilityState.isKeyboardUser) {
      baseProps.onFocus = (e: React.FocusEvent) => {
        e.target.classList.add('keyboard-focus');
      };
      baseProps.onBlur = (e: React.FocusEvent) => {
        e.target.classList.remove('keyboard-focus');
      };
    }

    switch (element) {
      case 'button':
        return {
          ...baseProps,
          role: 'button',
          tabIndex: 0,
        };
      case 'link':
        return {
          ...baseProps,
          role: 'link',
          tabIndex: 0,
        };
      case 'input':
        return {
          ...baseProps,
          'aria-required': true,
        };
      case 'dialog':
        return {
          ...baseProps,
          role: 'dialog',
          'aria-modal': true,
        };
      default:
        return baseProps;
    }
  };

  return {
    ...accessibilityState,
    updateFontSize,
    toggleKeyboardNavigation,
    announceToScreenReader,
    getAccessibleProps,
  };
};

export default useAccessibility;
