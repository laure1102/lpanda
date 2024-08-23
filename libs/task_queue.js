class TaskQueue {  
    constructor() {  
        this.queue = [];  
        this.isProcessing  = null;  
    }  
  
    addQueue(task,data) {
        let taskId = new Date().getTime();
        this.queue.push({
            taskId,
            task,
            data,
        });
        console.log(`加入任务到队列${taskId}`);
        console.log(`queue length:${this.queue.length}`);
        console.log(this.queue);
        console.log("this.isProcessing");
        console.log(this.isProcessing);
        if (this.isProcessing == null) { 
            this.tryToRun(); // 尝试运行队列中的任务  
        }
        return taskId; 
    }  
  
    length() {
        if(this.isProcessing == null)  {
            return this.queue.length;  
        }else{
            return this.queue.length + 1;
        }
    }  
  
    async tryToRun() {  
        console.log("tryToRun...");
        if (this.queue.length === 0) {  
            return; // 队列为空，不执行任何任务  
        }  
  
        // 等待当前处理的任务完成  
        if(this.isProcessing == null){
            // 获取队列中的第一个任务并移除它  
            const taskQ = this.queue.shift();  
            this.isProcessing = taskQ;
            let task = taskQ.task;
            console.log(`开始执行任务${this.isProcessing.taskId}`);
            console.log(this.isProcessing);
            await task(taskQ.data);
        }  
    }

    async doneProcessing(){
        if(!!this.isProcessing){
            this.isProcessing = null;
            console.log("doneProcessing...");
            console.log("set doneProcessing = null");
   
            this.tryToRun();  
        }
    }
}  

function initQueue(){
    return new TaskQueue();
}

export default initQueue;