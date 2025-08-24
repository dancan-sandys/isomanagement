const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Only use proxy in development
  if (process.env.NODE_ENV === 'development') {
    console.log('Setting up proxy middleware for development...');
    
    app.use(
      '/api/v1',
      createProxyMiddleware({
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        logLevel: 'debug',
        onProxyReq: (proxyReq, req, res) => {
          console.log('🚀 Proxying request:', req.method, req.url, '→', proxyReq.path);
          console.log('🎯 Target URL:', proxyReq.getHeader('host'));
        },
        onError: (err, req, res) => {
          console.error('❌ Proxy error:', err.message);
          console.error('🔍 Error details:', err);
        },
        onProxyRes: (proxyRes, req, res) => {
          console.log('✅ Proxy response:', proxyRes.statusCode, req.url);
        }
      })
    );
    
    console.log('✅ Proxy middleware setup complete for development');
  } else {
    console.log('Skipping proxy middleware in production');
  }
};
