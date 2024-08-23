const fs = require('fs');  
const path = require('path'); 
const { spawn } = require('child_process');

function deleteDirectory(dirPath) {  
    if (fs.existsSync(dirPath)) {  
        fs.readdirSync(dirPath).forEach(function(file, index) {  
        const curPath = path.join(dirPath, file);  
        if (fs.lstatSync(curPath).isDirectory()) { // 如果是文件夹，递归删除  
            deleteDirectory(curPath);  
        } else { // 如果是文件，直接删除  
            fs.unlinkSync(curPath);  
        }  
        });  
        fs.rmdirSync(dirPath); // 删除目录本身  
    } else {  
        console.log(`目录 ${dirPath} 不存在`);  
    }  
}  

function copyFile(sourceFilePath,targetDir,targetFilename){
    // 目标文件路径（包含文件名）  
    const targetFilePath = path.join(targetDir, targetFilename);  
    
    fs.copyFile(sourceFilePath, targetFilePath, (err) => {  
    if (err) {  
        console.error('复制文件时出错:', err);  
    } else {  
        console.log('文件复制成功:', targetFilePath);  
    }  
    });
}

//删除out目录
const distDir = "./out";
deleteDirectory(distDir);

let appName="lpanda";
let version = "1.0.0"
let platform = "win32";
let arch = "x64";
let appDir = `${distDir}/${appName}-${platform}-${arch}`;

// 获取当前进程的环境变量  
const env = Object.assign({}, process.env);  
  
let params = ["electron-packager",".",appName, `--platform=${platform}`, `--arch=${arch}`,
 `--out=${distDir}`, `--app-version=${version}`,"--icon=icon.ico",
 "--overwrite",  "--ignore=cache", "--ignore=logs",
  "--ignore=build", "--ignore=pscripts", "--ignore=py", "--ignore=release",  "--ignore=src", "--ignore=config.json",
  "--ignore=options.json", "--electron-version 28.1.3"];

const script = spawn("npx",params,
    {
        shell:true, 
        env: env, // 使用修改后的环境变量  
        stdio: 'inherit' // 继承父进程的 stdio  
    }
);

script.on('close', (code) => {
    console.log(`子进程退出，退出码 ${code}`);
    console.log("复制文件到" + appDir);
    fs.mkdirSync(`${appDir}/conf`);
    copyFile("./conf/config-default.json",appDir+"/conf","config.json");
    copyFile("./conf/options-default.json",appDir+"/conf","options.json");
});
