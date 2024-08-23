const { contextBridge, ipcRenderer } = require('electron'); 

window.addEventListener('DOMContentLoaded', () => {
  const replaceText = (selector, text) => {
    const element = document.getElementById(selector)
    if (element) element.innerText = text
  }

  for (const type of ['chrome', 'node', 'electron']) {
    replaceText(`${type}-version`, process.versions[type])
  }

  console.log('系统进程：', process.versions);
})


contextBridge.exposeInMainWorld('electronAPI', {  
  send: (channel, data) => {  
    ipcRenderer.send(channel, data);   
  },  
  receive: (channel, func) => { 
    ipcRenderer.once(channel, (event, ...args) => func(...args)); 
  }  ,  
  receiveAways: (channel, func) => { 
    ipcRenderer.on(channel, (event, ...args) => func(...args)); 
  }  
});