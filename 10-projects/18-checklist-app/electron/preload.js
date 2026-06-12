const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  toggleMain:       ()         => ipcRenderer.send('toggle-main'),
  syncNotes:        (data)     => ipcRenderer.invoke('sync-notes', data),
  onNoteResult:     (cb)       => ipcRenderer.on('note-result', (_, v) => cb(v)),
  getFloatPos:      ()         => ipcRenderer.invoke('get-float-pos'),
  setFloatPos:      (x, y)     => ipcRenderer.send('set-float-pos', x, y),
  updateFloatTimer: (data)     => ipcRenderer.send('update-float-timer', data),
  onFloatTimer:     (cb)       => ipcRenderer.on('float-timer', (_, v) => cb(v)),
});
