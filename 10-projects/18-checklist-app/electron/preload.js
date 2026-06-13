const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  // 기존
  toggleMain:       ()         => ipcRenderer.send('toggle-main'),
  syncNotes:        (data)     => ipcRenderer.invoke('sync-notes', data),
  onNoteResult:     (cb)       => ipcRenderer.on('note-result', (_, v) => cb(v)),
  getFloatPos:      ()         => ipcRenderer.invoke('get-float-pos'),
  setFloatPos:      (x, y)     => ipcRenderer.send('set-float-pos', x, y),
  updateFloatTimer: (data)     => ipcRenderer.send('update-float-timer', data),
  onFloatTimer:     (cb)       => ipcRenderer.on('float-timer', (_, v) => cb(v)),

  // Google 인증
  openAuth:         ()         => ipcRenderer.invoke('open-auth'),
  getToken:         ()         => ipcRenderer.invoke('get-token'),
  clearToken:       ()         => ipcRenderer.invoke('clear-token'),
  onAuthResult:     (cb)       => ipcRenderer.on('auth-result', (_, v) => cb(v)),

  // 온보딩
  setOnboarded:     ()         => ipcRenderer.invoke('set-onboarded'),
  onShowHint:       (cb)       => ipcRenderer.on('show-hint', cb),
  onHideHint:       (cb)       => ipcRenderer.on('hide-hint', cb),
});
