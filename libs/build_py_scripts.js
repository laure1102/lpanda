const fs = require('fs');  
const path = require('path'); 
const { spawn } = require('child_process');

function listFiles(dirPath,type) {  
    const files = fs.readdirSync(dirPath);  
    const pyFiles = files.filter(file => path.extname(file) === type);  
    return pyFiles;  
}  

function runBuild(scriptName,params){
    const pythonExecutable = path.join(__dirname, '../py/Scripts/pyinstaller.exe');
    const scriptPath = path.join(__dirname, "../pscripts/"+scriptName);
    params.unshift(scriptPath);
    return spawn(pythonExecutable, params);
}

const dirPath = './pscripts';   
const pythonFiles = listFiles(dirPath,'.py');  

const distDir = "./lexe";
if(fs.existsSync(distDir)){
    console.log("删除以前的发布exe");
    const oldPyeFiles = listFiles(distDir,'.exe');
    
    for(let pye of oldPyeFiles){
        let filepath = `${distDir}/${pye}`;
        try{
            fs.unlinkSync(filepath);
        }catch(err){
            console.log("无法删除文件:" + filepath);
        }
        
    }
}

for(let pyf of pythonFiles){
    const script = runBuild(pyf,["--onefile",`--distpath=${distDir}`,"--specpath=build"]);
    script.on('close', (code) => {
        console.log(`子进程退出，退出码 ${code}`);
    });
}