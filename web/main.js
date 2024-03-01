const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');


function createWindow() {
  // Crea la ventana del navegador.
  const mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    }
  });

  // Carga el archivo HTML de tu aplicación.
  mainWindow.loadFile(path.join(__dirname, 'public', 'index.html'));

  // Manejar la selección de carpeta y enviar la ruta al proceso de renderizado
  ipcMain.on('open-dialog-select-folder', (event, arg) => {
    const selectedFolderPath = dialog.showOpenDialogSync(mainWindow, {
      properties: ['openDirectory']
    });
    event.reply('selected-folder-path', selectedFolderPath);
  });
}

// Este método se llamará cuando Electron haya terminado
// la inicialización y esté listo para crear ventanas del navegador.
// Algunas APIs pueden usarse solo después de que este evento ocurra.
app.whenReady().then(createWindow);

// Salir cuando todas las ventanas estén cerradas, excepto en macOS. En macOS,
// es común para las aplicaciones y sus barras de menú estar activas hasta que el usuario
// salga explícitamente con Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  // En macOS, es común volver a crear una ventana en la aplicación cuando el
  // icono del muelle se hace clic y no hay otras ventanas abiertas.
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('ready', () => {
    mainWindow = new BrowserWindow({
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
        }
    });
});

// En este archivo, puede incluir el resto del proceso principal de su aplicación.
// También puede ponerlos en archivos separados y requerirlos aquí.
