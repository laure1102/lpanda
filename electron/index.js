const { app,Menu,dialog, BrowserWindow, ipcMain  } = require('electron')
const path = require('path')
const { setupIpcActions } = require('./ipc_actions');


function createWindow () {
  const win = new BrowserWindow({
    width: 1200,
    height: 960,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: false, // 禁用同源策略（不推荐，除非完全了解风险）  
      allowLocalFilesAccess: true, // 允许访问本地文件
      nodeIntegration: true, // 允许在渲染进程中使用 Node.js  
      //contextIsolation: false, // 如果 nodeIntegration 为 true，则必须设置此选项为 false  
   
    }
  })
  // 创建自定义菜单栏  
  const template = [  
    {  
      label: '文件',  
      submenu: [  
        {  
          label: '重新加载',  
          click: function() {  
            if (BrowserWindow.getFocusedWindow()) {  
              BrowserWindow.getFocusedWindow().reload();  
            }  
          }  
        }  ,
        {  
          label: '退出',  
          click: function() {  
            app.quit();  
          }  
        }
      ]  
    },  
    {  
      label: '设置',  
      submenu: [  
        {  
          label: '设置',  
          click: function() {
            // 发送事件到渲染进程  
            win.webContents.send('open-setting-page'); 
          }  
        },
      ]
    },
    // ... 其他菜单项 
    {  
      label: '帮助',  
      submenu: [  
        {  
          label: '控制台',  
          click: function() {
            win.webContents.toggleDevTools();
          }  
        },
        {  
          label: '关于',  
          click: function() {
            dialog.showMessageBox({  
              type: 'info',  
              message: '这是帮助信息',  
              detail: '你可以在这里添加详细的帮助内容。'  
            });  
          }  
        }
      ]  
    },    
  ];  
  
  const menu = Menu.buildFromTemplate(template);  
  Menu.setApplicationMenu(menu);


  let url = process.env.NODE_ENV === 'development' ?
  'http://localhost:3000' :
  'file://' + path.join(__dirname, '../dist/index.html');

  win.loadURL( url )
}

app.whenReady().then( async () => {
  createWindow();
  setupIpcActions();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
    }
  })

})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})


