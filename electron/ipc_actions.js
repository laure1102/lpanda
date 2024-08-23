
const { ipcMain,BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const winston = require('winston');
const { exec } = require('child_process');  
const customFormat = winston.format.printf(({ timestamp, level, message, label, ...rest }) => {  
    return `${timestamp} ${level}: ${message}`;  
  });

function getRelateFileConfigPath(filename){
    if(fs.existsSync("./pscripts/init_env.py")){
        //dev
        return `../${filename}`;
    }else{
        //release
        return `../../../${filename}`;
    }
}

let logger = null;
// 创建一个日志记录器
function initLogger(){
    let config =  getJson(getRelateFileConfigPath("conf/config.json"));
    let work_dir = config.work_dir;
    logger = winston.createLogger({  
        level: 'info', // 设置日志级别，可以是 'error', 'warn', 'info', 'http', 'verbose', 'debug', 'silly'  
        format: winston.format.combine(  
            winston.format.timestamp(), // 添加时间戳   
            winston.format.errors({ stack: true }), // 包含错误堆栈（可选）  
            customFormat // 自定义格式化输出  
        ),   
        transports: [  
          new winston.transports.File({ filename: work_dir + '/logs/ipc.log' }), // 将日志写入文件  
          new winston.transports.Console({  
            format: winston.format.combine(  
                winston.format.colorize(), // 可选，为控制台输出添加颜色  
                customFormat // 使用自定义格式化程序，包含时间戳  
              ),  
          }),  
        ],  
      }); 
}
/**
 * 
 * @param {*} scriptName 放在pscripts目录下的python脚本名字
 * @param {*} params 传递给脚本的参数数组
 */
function runScript(scriptName,params){
    if(!!!logger) initLogger();
    //检查是不是发行版本，发行版本运行exe，开发版本运行.py
    logger.info("run script:" + scriptName);
    if(fs.existsSync("./pscripts/init_env.py")){
        logger.info("dev env");
        const pythonExecutable = path.join(__dirname, '../py/Scripts/python.exe');
        const scriptPath = path.join(__dirname, '../pscripts/' + scriptName +".py");
        params.unshift(scriptPath);
        return spawn(pythonExecutable, params);
    }else{
        logger.info("package env");
        const exePath = path.join(__dirname, '../lexe/' + scriptName +".exe");
        return spawn(exePath, params);
    }
}

function getJson(filename) {
    let filepath = path.join(__dirname, filename);
    try {
        const data = fs.readFileSync(filepath, 'utf8');
        const jsonData = JSON.parse(data);
        return jsonData;
    } catch (error) {
        console.error('Error reading or parsing JSON file:', error);
        console.error("读取文件失败:" + filepath)
        throw error;
    }
};

function getJsonAbsFile(filename) {
    try {
        const data = fs.readFileSync(filename, 'utf8');
        const jsonData = JSON.parse(data);
        return jsonData;
    } catch (error) {
        console.error('Error reading or parsing JSON file:', error);
        console.error("读取文件失败:" + filename)
        throw error;
    }
};

function addStaticOptions(options){
    let rates = ["-10%","-20%","-30%","-40%","-50%","-100%","+0%","+10%","+20%","+30%","+40%","+50%","+100%"];
    let volumes = ["-10%","-20%","-30%","-40%","-50%","-100%","+0%","+10%","+20%","+30%","+40%","+50%","+100%"];
    let watermark_position_list = ["topleft","topright"];
    options.rates = rates;
    options.volumes = volumes;
    options.watermark_position_list = watermark_position_list;
}

function getNewStatus(temp_dir){
    let config = getJson(getRelateFileConfigPath("conf/config.json"));
    let work_dir = config.work_dir;
    let filePath = `${work_dir}/cache/${temp_dir}/status.json`;
    let rslt = true;
    let status = null;
    try{
        status = getJsonAbsFile(filePath);
        //增加各场景的参数
        const sceData = getJsonAbsFile(status.sce_file_path);
        status.sces = sceData.objs;
    }catch(error){
        logger.error("error:" + error);
        rslt = false;
    }
    status.work_dir = work_dir;
    return {
        rslt,
        status
    }
}


function setupIpcActions() {
    ipcMain.on('to-open-setting-page', (event) => {
        event.reply('open-setting-page', {
            rlst:0
        });
    });
    ipcMain.on('reload-app', (event) => {
        if (BrowserWindow.getFocusedWindow()) {  
            BrowserWindow.getFocusedWindow().reload();  
          } 
    });
    ipcMain.on('get-config', (event) => {
        let config = getJson(getRelateFileConfigPath("conf/config.json"));
        let options = getJson(getRelateFileConfigPath("conf/options.json"));
        addStaticOptions(options);
        event.reply('get-config-done', {
            config,
            options
        });
    });
    ipcMain.on('get-options', (event) => {
        let options = getJson(getRelateFileConfigPath("conf/options.json"));
        addStaticOptions(options);
        event.reply('get-options-done', {
            options
        });
    });

    ipcMain.on('refresh-options', (event) => {
        if(!!!logger) initLogger();
        logger.info("ipc run refresh-options");
        const script = runScript("refresh_options",[]);

        script.stdout.on('data', (data) => {
            logger.info(`stdout: ${data}`);
        });

        script.stderr.on('data', (data) => {
            logger.error(`stderr: ${data}`);
        });

        script.on('close', (code) => {
            logger.info(`子进程退出，退出码 ${code}`);
            let options = getJson(getRelateFileConfigPath("conf/options.json"));
            addStaticOptions(options);
            event.reply('refresh-options-done', {
                code,
                options
            });
        });
    });


    ipcMain.on('save-config', async (event,config) => {
        let rslt = true;
        const jsonString = JSON.stringify(config, null, 2); // 第二个参数是缩进，用于美化输出，这里设置为2

        // 将字符串写入文件
        let filepath = path.join(__dirname, getRelateFileConfigPath("conf/config.json"));
        fs.writeFile(filepath, jsonString, 'utf8', (err) => {
            if (err) {
                console.error('Error writing file:', err);
                rslt = false;
            }
            event.reply('save-config-done', {
                rslt
            });
        });
    });

    ipcMain.on('get-temp-dirs', (event) => {
        let config = getJson(getRelateFileConfigPath("conf/config.json"));
        let work_dir = config.work_dir;
        // 使用 fs.readdirSync() 获取目录下的所有文件和子目录
        directoryPath = work_dir + "/cache";
        const items = fs.readdirSync(directoryPath);
        const subdirectories = [];
        // 遍历每个项目，检查是否为目录
        items.forEach(item => {
            const itemPath = path.join(directoryPath, item);
            // 使用 fs.statSync() 获取项目的状态
            const itemStats = fs.statSync(itemPath);
            if (itemStats.isDirectory()) {
                subdirectories.push(item);
            }
        });
        event.reply('get-temp-dirs-done', {
            dirs:subdirectories
        });
    });

    ipcMain.on('get-continue-status', (event, temp_dir) => {
        let config = getJson(getRelateFileConfigPath("conf/config.json"));
        let work_dir = config.work_dir;
        // 使用 fs.readdirSync() 获取目录下的所有文件和子目录
        let filePath = `${work_dir}/cache/${temp_dir}/status.json`;
        let status = getJsonAbsFile(filePath);
        event.reply('get-continue-status-done', {
            status
        });
    });

    ipcMain.on('refresh-status', (event, temp_dir) => {
        rslt = getNewStatus(temp_dir);
        event.reply('refresh-status-done', rslt);
    });
    
    ipcMain.on('run-split', (event, data) => {
        if(!!!logger) initLogger();
        let {newFilePath, temp_dir,role_name,rate,volume} = data;
        logger.info("newFilePath:"+newFilePath)
        let filePath = newFilePath;
        logger.info("ipc run run-split");
        logger.info(filePath);
        const script = runScript("split_file", [filePath,temp_dir,role_name,rate,volume]);

        script.stdout.on('data', (data) => {
            logger.info(`stdout: ${data}`);
        });

        script.stderr.on('data', (data) => {
            logger.error(`stderr: ${data}`);
        });

        script.on('close', (code) => {
            logger.info(`子进程退出，退出码 ${code}`);
            event.reply('split-done', {
                code,
                filePath,
                temp_dir
            });
        });
    });

    
    ipcMain.on('run-batch-tts', (event, data) => {
        let temp_dir = data.temp_dir;
        if(!!!logger) initLogger();
        logger.info("ipc run run-batch-tts");
        logger.info(temp_dir);
        
        const script = runScript("batch_tts", [temp_dir]);

        script.stdout.on('data', (data) => {
            logger.info(`stdout: ${data}`);
        });

        script.stderr.on('data', (data) => {
            logger.error(`stderr: ${data}`);
        });

        script.on('close', (code) => {
            logger.info(`子进程退出，退出码 ${code}`);
            rslt = getNewStatus(temp_dir);
            event.reply('run-batch-tts-done', {
                code,
                rslt
            });
        });
    });

    ipcMain.on('run-ai-prompt', (event, data) => {
        let temp_dir = data.temp_dir;
        if(!!!logger) initLogger();
        logger.info("ipc run run-ai-prompt")
        logger.info(temp_dir)
        
        const script = runScript("ai_prompt", ["all",temp_dir,""]);

        script.stdout.on('data', (data) => {
            logger.info(`stdout: ${data}`);
        });

        script.stderr.on('data', (data) => {
            logger.error(`stderr: ${data}`);
        });

        script.on('close', (code) => {
            logger.info(`子进程退出，退出码 ${code}`);
            rslt = getNewStatus(temp_dir);
            event.reply('run-ai-prompt-done', {
                code,
                rslt
            });
        });
    });

    ipcMain.on('run-prompt-save', (event, data) => {
        let sce_file_path = data.sce_file_path;
        let sces = data.sces;
        let rootObject = {
            objs:sces
        };
        if(!!!logger) initLogger();
        logger.info("ipc run run-prompt-save")
        
        const jsonString = JSON.stringify(rootObject, null, 2); // 第二个参数是缩进，用于美化输出，这里设置为2

        try {  
            fs.writeFileSync(sce_file_path, jsonString, 'utf8');  
            rslt = getNewStatus(data.temp_dir);
            event.reply('run-prompt-save-done', {
                code:0,
                rslt
            });
        } catch (err) {  
            logger.info("error occured:" + err) 
            event.reply('run-prompt-save-done', {
                code:1,
            });
        }
    });

    ipcMain.on('run-regen-prompt', (event, data) => {
        if(!!!logger) initLogger();
        logger.info("ipc run run-regen-prompt")
        let temp_dir = data.status.temp_dir;
        let seqnum = data.sce.seqnum;
        logger.info(seqnum)
        
        const script = runScript("ai_prompt", ["regen",temp_dir,seqnum]);
        script.stdout.on('data', (data) => {
            // logger.info(`stdout: ${data}`);
        });

        script.stderr.on('data', (data) => {
            // logger.error(`stderr: ${data}`);
        });

        script.on('close', (code) => {
            logger.info(`子进程退出，退出码 ${code}`);
            rslt = getNewStatus(temp_dir);
            event.reply('run-regen-prompt-done', {
                code,
                rslt,
                seqnum,
            });
        });
    });

    
    ipcMain.on('run-ai-tutu', (event, data) => {
        let temp_dir = data.temp_dir;
        if(!!!logger) initLogger();
        logger.info("ipc run run-ai-tutu")
        logger.info(temp_dir)
        
        const script = runScript("ai_tutu", ["all",temp_dir,""]);

        script.stdout.on('data', (data) => {
            logger.info(`stdout: ${data}`);
        });

        script.stderr.on('data', (data) => {
            logger.error(`stderr: ${data}`);
        });

        script.on('close', (code) => {
            logger.info(`子进程退出，退出码 ${code}`);
            rslt = getNewStatus(temp_dir);
            event.reply('run-ai-tutu-done', {
                code,
                rslt
            });
        });
    });

    ipcMain.on('run-regen-tutu', (event, data) => {
        if(!!!logger) initLogger();
        logger.info("ipc run run-regen-tutu")
        let temp_dir = data.status.temp_dir;
        let tutuid = data.tutuid;
        logger.info(tutuid)
        
        const script = runScript("ai_tutu", ["regen",temp_dir,tutuid]);
        script.stdout.on('data', (data) => {
            logger.info(`stdout: ${data}`);
        });

        script.stderr.on('data', (data) => {
            logger.error(`stderr: ${data}`);
        });

        script.on('close', (code) => {
            rslt = getNewStatus(temp_dir);
            event.reply('run-regen-tutu-done', {
                code,
                rslt,
                tutuid
            });
        });
    });

    
    ipcMain.on('run-gen-video', (event, data) => {
        if(!!!logger) initLogger();
        let temp_dir = data.temp_dir;
        logger.info("ipc run run-gen-video")
        logger.info(temp_dir)
        
        const script = runScript("gen_video", [temp_dir]);

        script.stdout.on('data', (data) => {
            logger.info(`stdout: ${data}`);
        });

        script.stderr.on('data', (data) => {
            logger.error(`stderr: ${data}`);
        });

        script.on('close', (code) => {
            logger.info(`子进程退出，退出码 ${code}`);
            rslt = getNewStatus(temp_dir);
            event.reply('run-gen-video-done', {
                code,
                rslt,
                temp_dir
            });
        });
    });

    
    
    ipcMain.on('run-merge-mp4', (event, data) => {
        if(!!!logger) initLogger();
        let temp_dir = data.temp_dir;
        logger.info("ipc run run-merge-mp4")
        logger.info(temp_dir)
        const script = runScript("merge_mp4", [temp_dir]);

        script.stdout.on('data', (data) => {
            logger.info(`stdout: ${data}`);
        });

        script.stderr.on('data', (data) => {
            logger.error(`stderr: ${data}`);
        });

        script.on('close', (code) => {
            logger.info(`子进程退出，退出码 ${code}`);
            rslt = getNewStatus(temp_dir);
            event.reply('run-merge-mp4-done', {
                code,
                rslt,
                temp_dir
            });
        });
    });
    // 打开目录的 IPC 消息处理函数  
    ipcMain.on('open-directory', (event, directoryPath) => {  
        if(!!!logger) initLogger();
        logger.info(`open directory: ${directoryPath}`);
        const os = require('os');  
        let command;  
        if (os.platform() === 'win32') {  
        command = `explorer "${directoryPath}"`; // Windows 命令  
        } else if (os.platform() === 'darwin') {  
        command = `open -R "${directoryPath}"`; // macOS 命令  
        } else {  
        command = `xdg-open "${directoryPath}"`; // 其他 Linux 发行版可能使用 xdg-open  
        }  
        exec(command);  
    }); 

};

module.exports = { setupIpcActions };