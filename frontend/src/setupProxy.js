// const { createProxyMiddleware } = require('http-proxy-middleware');

// module.exports = function(app) {
//   console.log('Setting up proxy middleware...');
  
//   app.use(
//     '/api/v1',
//     createProxyMiddleware({
//       target: 'http://localhost:8000/api/v1/',
//       changeOrigin: true,
//       secure: false,
//       logLevel: 'debug',
//       onProxyReq: (proxyReq, req, res) => {
//         // Ensure the full path is preserved
//         if (!proxyReq.path.startsWith('/api/v1')) {
//           proxyReq.path = '/api/v1' + proxyReq.path;
//         }
//         console.log('🚀 Proxying request:', req.method, req.url, '→', proxyReq.path);
//         console.log('🎯 Target URL:', proxyReq.getHeader('host'));
//       },
//       onError: (err, req, res) => {
//         console.error('❌ Proxy error:', err.message);
//         console.error('🔍 Error details:', err);
//       },
//       onProxyRes: (proxyRes, req, res) => {
//         console.log('✅ Proxy response:', proxyRes.statusCode, req.url);
//       }
//     })
//   );
  
//   console.log('✅ Proxy middleware setup complete');
// };


const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  console.log('Setting up proxy middleware...');

  app.use(
    '/api/v1',
    createProxyMiddleware({
      target: 'http://iso-backend:8000', // 🔥 Docker service name
      changeOrigin: true,
      logLevel: 'debug',
    })
  );

  console.log('✅ Proxy middleware setup complete');
};