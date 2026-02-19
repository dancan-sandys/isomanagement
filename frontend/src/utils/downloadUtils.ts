export const downloadFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const getFileIcon = (fileType: string) => {
  const type = fileType?.toLowerCase() || '';
  if (type.includes('pdf')) return '📄';
  if (type.includes('doc')) return '📝';
  if (type.includes('xls')) return '📊';
  if (type.includes('image')) return '🖼️';
  if (type.includes('text')) return '📄';
  return '📄';
}; 