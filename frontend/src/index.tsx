import React from 'react';
import { createRoot } from 'react-dom/client';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';

import App from './App';
import { store } from './store';
import AuthProvider from './components/Auth/AuthProvider';
import { ThemeProvider as ISOThemeProvider } from './theme/ThemeProvider';
import './index.css';

const container = document.getElementById('root');
if (!container) throw new Error('Failed to find the root element');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <ISOThemeProvider>
          <AuthProvider>
            <App />
          </AuthProvider>
        </ISOThemeProvider>
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
); 