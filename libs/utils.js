import { Message } from "view-design";
const Utils = {
    clone: function (o) {
      return $.extend(true, {}, o);
    },
    copyValues: function (from, to) {
      for (let key in from) {
        to[key] = from[key];
      }
    },
    dateFormat: function (fmt, date) {
      let ret;
      const opt = {
        "y+": date.getFullYear().toString(), // 年
        "m+": (date.getMonth() + 1).toString(), // 月
        "d+": date.getDate().toString(), // 日
        "H+": date.getHours().toString(), // 时
        "M+": date.getMinutes().toString(), // 分
        "S+": date.getSeconds().toString(), // 秒
        // 有其他格式化字符需求可以继续添加，必须转化成字符串
      };
      for (let k in opt) {
        ret = new RegExp("(" + k + ")").exec(fmt);
        if (ret) {
          fmt = fmt.replace(
            ret[1],
            ret[1].length == 1 ? opt[k] : opt[k].padStart(ret[1].length, "0")
          );
        }
      }
      return fmt;
    },
    //所有form的验证
    validateForm: function (vm, formId) {
      let validate = true;
      vm.$refs[formId].validate((valid) => {
        if (!valid) {
          validate = false;
        }
      });
      return validate;
    },
    ipcSend(channel,data){
      window.electronAPI.send(channel, data);
    },
    ipcReceive: (channel, func) => { 
      window.electronAPI.receive(channel, func);
    },
    ipcReceiveAways: (channel, func) => { 
      window.electronAPI.receiveAways(channel, func);
    },
    
    generateRandomString(length) {  
      const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';  
      let result = '';  
      for (let i = 0; i < length; i++) {  
          result += chars.charAt(Math.floor(Math.random() * chars.length));  
      }  
      return result;  
    },
    generateTimestampedRandomString() {  
      const now = new Date();  
      const year = now.getFullYear();  
      const month = String(now.getMonth() + 1).padStart(2, '0');  
      const day = String(now.getDate()).padStart(2, '0');  
      const hour = String(now.getHours()).padStart(2, '0');  
      const minute = String(now.getMinutes()).padStart(2, '0');  
      const second = String(now.getSeconds()).padStart(2, '0');  
      const timestamp = `${year}_${month}_${day}_${hour}_${minute}_${second}`;  
      const randomString = this.generateRandomString(8);  
      return `${timestamp}_${randomString}`;  
    },    
};

export default Utils;