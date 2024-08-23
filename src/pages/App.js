
import {Message } from "view-design";
import Utils from '@/../libs/utils'
import initQueue from '@/../libs/task_queue'
export default {
    name:"app",
    data(){
        let defaultStatus = {
                temp_dir:"",
                actionType:"new",
                newFilePath:"",
                continueDir:"",
                role_name:"zh-CN-YunxiNeural",
                rate:"+10%",
                volume:"+0%",
                source_file_name: "",
                source_file_path: "",
                sce_file_path: "",
                create_dttm: "",
                end_dttm: "",
                scene_split_chars: 0,
                current_stage: "",
                current_stage_descr: ",参数: 同时处理个数:10,角色:zh-CN-YunxiNeural,音量:+0%,语速:+10%",
                sce_count: 0,
                mp3_done_count: 0,
                gpt_done_count: 0,
                tutu_done_count: 0,
                mp4_done_count: 0,
                seconds_per_tutu: 0,
                work_dir:"",
            };
        let status = {};
        Utils.copyValues(defaultStatus, status);
        return {
            step:0,
            stepNames:['开始','转语音','推理提示词','AI生图','合成视频','输出视频'],
            refreshTimer:null,
            defaultStatus:defaultStatus,
            status:status,
            continueList:[],
            ruleInline0:{

            },
            options:{

            },
            loading:{
                next0:false,
                next1:false,
                next2:false,
                next3:false,
                next4:false,
                next5:false,
                next6:false,
                prompt_save:false,
                prompt_regen:false,
                tutu_regen:false,
            },
            sces:[],
            aicolumns:[
                {
                    title: '序号',
                    key: 'seqnum',
                    width:150,
                },
                {
                    title: '场景内容',
                    key: 'text',
                    render: (h, params) => {
                        let text = params.row.text;
                        if(text.length > 100){
                            text = text.substring(0,100) + "...";
                        }
                        let vue = this;
                        return h('a', {
                            class:"column-text",
                            props: {},
                            on:{
                                click:()=>{
                                    vue.openTextModal(params.row)
                                }
                            },
                        },
                        [
                            h('span', text)
                        ]);
                    }
                },
                {
                    title: '提示词',
                    key: 'prompt',
                    render: (h, params) => {
                        let prompt = params.row.prompt;
                        if(prompt.length > 200){
                            prompt = prompt.substring(0,200) + "...";
                        }
                        let vue = this;
                        return h('a', {
                            class:"column-prompt",
                            props: {},
                            on:{
                                click:()=>{
                                    vue.openPromptModal(params.row)
                                }
                            },
                        },
                        [
                            h('span', prompt)
                        ]);
                    }
                },
                {
                    title: '重新推理',
                    key: 'actions',
                    width:80,
                    render: (h, params) => {
                        let vue = this;
                        if(vue.status.current_stage == "aiprompt_done"){
                            return h('Button', {
                                class:"column-regen-prompt",
                                props: {
                                    type:"info",
                                    icon:"md-refresh",
                                    shape:"circle",
                                    loading:vue.redoArr.includes(`p_${params.row.seqnum}`),
                                },
                                on:{
                                    click:()=>{
                                        vue.doRegenPrompt(this,params.row)
                                    }
                                },
                            });
                        }else{
                            return h("div","");
                        }
                    }
                },],
            aitableHeight:200,
            promptModal:{
                show:false,
                row:{},
                readonly:false,
            },
            tutuModal:{
                show:false,
                row:{},
                tutu:{},
            },
            taskQueue:null,
            redoArr: [],
            tutuMode: "table",
            tutucolumns:[
                {
                    title: '序号',
                    key: 'seqnum',
                    width:150,
                },
                {
                    title: '场景内容',
                    key: 'text',
                    render: (h, params) => {
                        let text = params.row.text;
                        if(text.length > 100){
                            text = text.substring(0,100) + "...";
                        }
                        let vue = this;
                        return h('a', {
                            class:"column-text",
                            props: {},
                            on:{
                                click:()=>{
                                    vue.openTutuTextModal(params.row)
                                }
                            },
                        },
                        [
                            h('span', text)
                        ]);
                    }
                },
                {
                    title: '图图们',
                    key: 'tutus',
                    render: (h, params) => {
                        let vue = this;
                        let tutuArr = [];
                        for(let tutu of params.row.tutu){
                            let subs = [h("img",{
                                attrs:{
                                    src:tutu.src
                                },
                                on:{
                                    click:()=>{
                                        vue.tutuModalShow(this,params.row,tutu);
                                    }
                                }
                            })];
                            if(vue.status.current_stage == "aitutu_done"){
                                subs.push(h("Button",{
                                    props: {
                                        type:vue.redoArr.includes(`p_${params.row.seqnum}:${tutu.id}`)?"error":"info",
                                        icon:"md-refresh",
                                        shape:"circle",
                                        loading:vue.redoArr.includes(`p_${params.row.seqnum}:${tutu.id}`),
                                    },
                                    on:{
                                        click:()=>{
                                            vue.doRegenTutu(this,params.row,tutu)
                                        }
                                    },
                                }));
                            }
                            let tutuDiv = h("div",{
                                class:"tutu-div",
                            },subs);
                            tutuArr.push(tutuDiv);
                        }
                        return h("div",{
                            class:"tutu-column-div",
                        },tutuArr);
                    }
                },],
        }
    },
    computed:{
        cal_step_status(){
            let ss = 0;
            switch(this.status.current_stage){
                case "split_start":
                case "split_ing":
                case "split_done":
                case "tts_start":
                case "tts_ing":
                case "tts_done":
                    ss = 1;
                    break;
                case "aiprompt_start":
                case "aiprompt_ing":
                case "aiprompt_done":
                    ss = 2;
                    break;
                case "aitutu_start":
                case "aitutu_ing":
                case "aitutu_done":
                    ss = 3;
                    break;
                case "video_start":
                case "video_ing":
                case "video_done":
                    ss = 4;
                    break;
                case "merge_video_start":
                case "merge_video_ing":
                case "merge_video_done":
                    ss = 5;
                    break;
                default:
                    ss = 0;
                    break;
            }
            return ss;
        },
    },
    methods:{
        initApp(){
            let vue = this;
            Utils.ipcSend('get-config');
            Utils.ipcReceive('get-config-done', (data) => {
                this.status.work_dir =   data.config.work_dir;
                if(!!!data.config.work_dir){
                    vue.$Modal.info({
                        title: "警告",
                        content: "请先设置工作目录",
                        onOk:()=>{
                            Utils.ipcSend("to-open-setting-page");
                        }
                    });
                    return;
                }
                vue.options = data.options;
            });
        },
        changeActionType(){

            if(!!!this.status.work_dir){
                this.$Modal.info({
                    title: "警告",
                    content: "请先设置工作目录",
                    onOk:()=>{
                        Utils.ipcSend("to-open-setting-page");
                    }
                });
                return;
            }
            this.status.newFilePath = "";
            this.status.temp_dir = "";
            this.status.role_name = "";
            this.status.rate = "";
            this.status.volume = "";

            if(this.status.actionType == "new"){
                Utils.copyValues(this.defaultStatus,this.status);
            }
            if(this.status.actionType == "continue"){
                Utils.ipcSend("get-temp-dirs");
                Utils.ipcReceive('get-temp-dirs-done', (data) => {
                    this.continueList = data.dirs;
                });
            }
        },
        toSelectNewFile(){
            this.$refs['ltext-file'].click();
        },
        selectNewFile(e){
            if(this.$refs['ltext-file'].files.length > 0){
                this.status.newFilePath = this.$refs['ltext-file'].files[0].path;
            }
        },
        selectContinueDir(){
            Utils.ipcSend("get-continue-status",this.status.continueDir);
            Utils.ipcReceive('get-continue-status-done', (data) => {
                    Utils.copyValues(data.status, this.status);
                });
        },
        refreshCurrentStatus(){
            if(!!!this.status.temp_dir){
                return;
            }
            let vue = this;
            Utils.ipcSend("refresh-status",vue.status.temp_dir);
            Utils.ipcReceive('refresh-status-done', (data) => {
                console.log("refreshCurrentStatus");
                console.log(data);
                if(data.rslt){
                    Utils.copyValues(data.status, vue.status);
                    if(!!data.status.sces){
                        vue.sces = data.status.sces;
                    }
                }
            });

        },
        autoRefreshCurrentStatus(){
            let vue = this;
            vue.refreshCurrentStatus();
            if(!!vue.refreshTimer){
                clearTimeout(vue.refreshTimer);
            }
            vue.refreshTimer = setTimeout(() => {
                vue.autoRefreshCurrentStatus();
            }, 2000);
        },
        async next0(){

            if(!!!this.status.work_dir){
                this.$Modal.info({
                    title: "警告",
                    content: "请先设置工作目录",
                    onOk:()=>{
                        Utils.ipcSend("to-open-setting-page");
                    }
                });
                return;
            }
            if(this.status.actionType == "new"){
                if(!!!this.status.newFilePath){
                    Message.error("请选择文件。");
                    return;
                }
            }else{
                if(!!!this.status.continueDir){
                    Message.error("请选择要继续处理的目录。");
                    return;
                }
            }
            if(!!!this.status.role_name){
                Message.error("请选择解说角色。");
                return;
            }
            if(!!!this.status.rate){
                Message.error("请选择语速。");
                return;
            }
            if(!!!this.status.volume){
                Message.error("请选择音量。");
                return;
            }
            if(this.status.actionType == "new"){
                this.loading.next0 = true;
                this.status.temp_dir = Utils.generateTimestampedRandomString();
                Utils.ipcSend("run-split",this.status);
                Utils.ipcReceive('split-done', (data) => {
                    if(data.code !=0){
                        Message.error("执行失败，请查看日志");
                        return;
                    }
                    this.step = 1;
                    this.loading.next0 = false;
                });
            }else{
                let vue = this;
                vue.loading.next0 = true;
                vue.refreshCurrentStatus();
                vue.loading.next0 = false;
                vue.step = vue.cal_step_status;
            }
        },
        async next1_start(){
            this.loading.next1 = true;
            Utils.ipcSend("run-batch-tts",this.status);
            this.autoRefreshCurrentStatus();
            let vue = this;
            Utils.ipcReceive('run-batch-tts-done', (data) => {
                console.log('run-batch-tts-done');
                console.log(data);
                if(data.code !=0){
                    Message.error("执行失败，请查看日志");
                    return;
                }
                if(!!vue.refreshTimer){
                    clearTimeout(vue.refreshTimer);
                }
                Utils.copyValues(data.rslt.status, vue.status);
                if(!!data.rslt.status.sces){
                    vue.sces = data.rslt.status.sces;
                }
                vue.loading.next1 = false;
            });
        },
        async next1_stop(){
            this.step = 2;
            console.log(this.status)
            console.log(this.sces)
        },
        async next2_start(){
            this.loading.next2 = true;
            Utils.ipcSend("run-ai-prompt",this.status);
            this.autoRefreshCurrentStatus();
            let vue = this;
            Utils.ipcReceive('run-ai-prompt-done', (data) => {
                console.log('run-ai-prompt-done');
                console.log(data);
                if(data.code !=0){
                    Message.error("执行失败，请查看日志");
                    return;
                }
                if(!!vue.refreshTimer){
                    clearTimeout(vue.refreshTimer);
                }
                Utils.copyValues(data.rslt.status, vue.status);
                if(!!data.rslt.status.sces){
                    vue.sces = data.rslt.status.sces;
                }
                vue.loading.next2 = false;
            });
        },
        async next2_stop(){
            this.step = 3;
            console.log(this.status)
            console.log(this.sces)
        },
        async openTextModal(row){
            this.$Modal.info({
                content: row.text
            });
        },
        async openPromptModal(row){
            this.promptModal.row = row;
            this.promptModal.show = true;
            this.promptModal.readonly = false;
        },
        async prompt_save(){
            let sces = this.sces;
            for(let sce of sces){
                if(sce.seqnum == this.promptModal.row.seqnum){
                    Utils.copyValues(this.promptModal.row, sce);
                }
            }
            this.loading.prompt_save = true;
            Utils.ipcSend("run-prompt-save",this.status);
            let vue = this;
            Utils.ipcReceive('run-prompt-save-done', (data) => {
                if(data.code !=0){
                    Message.error("执行失败，请查看日志");
                    vue.loading.prompt_save = false;
                    return;
                }
                if(!!vue.refreshTimer){
                    clearTimeout(vue.refreshTimer);
                }
                Utils.copyValues(data.rslt.status, vue.status);
                if(!!data.rslt.status.sces){
                    vue.sces = data.rslt.status.sces;
                }
                vue.loading.prompt_save = false;
                vue.promptModal.show = false;
            });
        },
        async prompt_regen(){
            this.loading.prompt_regen = true;
            Utils.ipcSend("run-regen-prompt",{
                status:this.status,
                sce:this.promptModal.row,
            });
            let vue = this;
            Utils.ipcReceive('run-regen-prompt-done', (data) => {
                if(data.code !=0){
                    Message.error("执行失败，请查看日志");
                    vue.loading.prompt_regen = false;
                    return;
                }
                if(!!vue.refreshTimer){
                    clearTimeout(vue.refreshTimer);
                }
                Utils.copyValues(data.rslt.status, vue.status);
                if(!!data.rslt.status.sces){
                    vue.sces = data.rslt.status.sces;
                }
                vue.loading.prompt_regen = false;
                vue.promptModal.show = false;
            });
        },
        async regenPromptTask(data){
            console.log("开始执行这次任务");
            Utils.ipcSend("run-regen-prompt",data);

            let vue = this;

            Utils.ipcReceive('run-regen-prompt-done', (data) => {
                console.log("queue done run-regen-prompt-done");
                console.log(data);
                if(data.code !=0){
                    Message.error("执行失败，请查看日志");
                }else{
                    if(!!vue.refreshTimer){
                        clearTimeout(vue.refreshTimer);
                    }
                    Utils.copyValues(data.rslt.status, vue.status);
                    if(!!data.rslt.status.sces){
                        vue.sces = data.rslt.status.sces;
                        for(let i = vue.redoArr.length - 1 ; i>=0;i--){
                            if(vue.redoArr[i] == `p_${data.seqnum}`){
                                vue.redoArr.splice(i,1);
                            }
                        }
                    }
                }
                console.log("调用doneProcessing")
                vue.taskQueue.doneProcessing();
            });
        },
        async doRegenPrompt(e,row){
            this.redoArr.push(`p_${row.seqnum}`);
            this.taskQueue.addQueue(this.regenPromptTask,{
                status:this.status,
                sce:row,
            });
        },
        async prompt_return(){
            this.promptModal.show = false;
            this.promptModal.row = {};
        },
        resetAitableSize(){
            this.aitableHeight = window.innerHeight - 290;
            console.log(this.aitableHeight);
        },

        async next3_start(){
            this.loading.next3 = true;
            Utils.ipcSend("run-ai-tutu",this.status);
            this.autoRefreshCurrentStatus();
            let vue = this;
            Utils.ipcReceive('run-ai-tutu-done', (data) => {
                console.log('run-ai-tutu-done');
                console.log(data);
                if(data.code !=0){
                    Message.error("执行失败，请查看日志");
                    return;
                }
                if(!!vue.refreshTimer){
                    clearTimeout(vue.refreshTimer);
                }
                Utils.copyValues(data.rslt.status, vue.status);
                if(!!data.rslt.status.sces){
                    vue.sces = data.rslt.status.sces;
                }
                vue.loading.next3 = false;
            });
        },
        async next3_stop(){
            this.step = 4;
            console.log(this.status)
            console.log(this.sces)
        },
        async tutu_regen(){
            this.loading.tutu_regen = true;
            let tutuid = `${this.tutuModal.row.seqnum}:${this.tutuModal.tutu.id}`;
            Utils.ipcSend("run-regen-tutu",{
                status:this.status,
                tutuid,
            });
            let vue = this;
            Utils.ipcReceive('run-regen-tutu-done', (data) => {
                if(data.code !=0){
                    Message.error("执行失败，请查看日志");
                    vue.loading.tutu_regen = false;
                    return;
                }
                if(!!vue.refreshTimer){
                    clearTimeout(vue.refreshTimer);
                }
                Utils.copyValues(data.rslt.status, vue.status);
                if(!!data.rslt.status.sces){
                    vue.sces = data.rslt.status.sces;
                }
                vue.loading.tutu_regen = false;
                vue.tutuModal.show = false;
            });
        },
        async regenTutuTask(data){
            console.log("开始执行这次任务");
            Utils.ipcSend("run-regen-tutu",data);

            let vue = this;

            Utils.ipcReceive('run-regen-tutu-done', (data) => {
                console.log("queue done run-regen-tutu-done");
                console.log(data);
                if(data.code !=0){
                    Message.error("执行失败，请查看日志");
                }else{
                    if(!!vue.refreshTimer){
                        clearTimeout(vue.refreshTimer);
                    }
                    Utils.copyValues(data.rslt.status, vue.status);
                    if(!!data.rslt.status.sces){
                        vue.sces = data.rslt.status.sces;
                        for(let i = vue.redoArr.length - 1 ; i>=0;i--){
                            if(vue.redoArr[i] == `p_${data.tutuid}`){
                                vue.redoArr.splice(i,1);
                            }
                        }
                    }
                }
                console.log("调用doneProcessing")
                vue.taskQueue.doneProcessing();
            });
        },
        async doRegenTutu(e,row,tutu){
            let tutuid = `${row.seqnum}:${tutu.id}`;
            this.redoArr.push(`p_${tutuid}`);
            this.taskQueue.addQueue(this.regenTutuTask,{
                status:this.status,
                tutuid,
            });
        },
        async openTutuTextModal(row){
            this.promptModal.row = row;
            this.promptModal.show = true;
            this.promptModal.readonly = true;
        },
        async tutuModalShow(e,row,tutu){
            this.tutuModal.show = true;
            this.tutuModal.row = row;
            this.tutuModal.tutu = tutu;
        },
        async tutuModalReturn(){
            this.tutuModal.show = false;
            this.tutuModal.row = {};
            this.tutuModal.tutu = {};
        },
        async tutu_next(){
            let crtRow = this.tutuModal.row;
            let crtTutu = this.tutuModal.tutu;
            let sces = this.sces;

            if(crtTutu.id + 1 >= crtRow.tutu.length){
                //已经是本场景最后一张图片，取下一个场景第一张图片
                if(crtRow.seqnum >= sces.length){
                    //已经是最后一个场景了
                    Message.error("没有下一个了。");
                    return;

                }else{
                    let nextSce = sces[crtRow.seqnum]
                    let tutu = nextSce.tutu[0];
                    this.tutuModal.row = nextSce;
                    this.tutuModal.tutu = tutu;
                }
            }else{
                //取本场景下一张图片
                let nextSce = crtRow;
                let tutu = nextSce.tutu[crtTutu.id+1];
                this.tutuModal.row = nextSce;
                this.tutuModal.tutu = tutu;
            }
        },
        async tutu_last(){
            let crtRow = this.tutuModal.row;
            let crtTutu = this.tutuModal.tutu;
            let sces = this.sces;

            if(crtTutu.id == 0){
                //已经是本场景第一张图片，取上一个场景最后一张图片
                if(crtRow.seqnum == 1){
                    //已经是第一个场景了
                    Message.error("没有上一个了。");
                    return;

                }else{
                    let lastSce = sces[crtRow.seqnum-2]
                    let tutu = lastSce.tutu[lastSce.tutu.length-1];
                    this.tutuModal.row = lastSce;
                    this.tutuModal.tutu = tutu;
                }
            }else{
                //取本场景上一张图片
                let lastSce = crtRow;
                let tutu = lastSce.tutu[crtTutu.id-1];
                this.tutuModal.row = lastSce;
                this.tutuModal.tutu = tutu;
            }

        },
        async next4_start(){
            this.loading.next4 = true;
            Utils.ipcSend("run-gen-video",this.status);
            this.autoRefreshCurrentStatus();
            let vue = this;
            Utils.ipcReceive('run-gen-video-done', (data) => {
                console.log('run-gen-video-done');
                console.log(data);
                if(data.code !=0){
                    Message.error("执行失败，请查看日志");
                    return;
                }
                if(!!vue.refreshTimer){
                    clearTimeout(vue.refreshTimer);
                }
                Utils.copyValues(data.rslt.status, vue.status);
                if(!!data.rslt.status.sces){
                    vue.sces = data.rslt.status.sces;
                }
                vue.loading.next4 = false;
            });
        },
        async next4_stop(){
            this.step = 5;
            console.log(this.status)
            console.log(this.sces)
        },
        async showVideo(row){
            if(!!row.mp4aufile){
                window.open(row.mp4aufile);
            }
        },
        async next5_start(){
            this.loading.next5 = true;
            Utils.ipcSend("run-merge-mp4",this.status);
            this.autoRefreshCurrentStatus();
            let vue = this;
            Utils.ipcReceive('run-merge-mp4-done', (data) => {
                console.log('run-merge-mp4-done');
                console.log(data);
                if(data.code !=0){
                    Message.error("执行失败，请查看日志");
                    return;
                }
                if(!!vue.refreshTimer){
                    clearTimeout(vue.refreshTimer);
                }
                Utils.copyValues(data.rslt.status, vue.status);
                if(!!data.rslt.status.sces){
                    vue.sces = data.rslt.status.sces;
                }
                vue.loading.next5 = false;
            });
        },
        async next5_stop(){
            Utils.ipcSend('open-directory', `${this.status.work_dir}\\cache\\${this.status.temp_dir}`);
        },
        async playVideo(){
            let url = `${this.status.work_dir}/cache/${this.status.temp_dir}/${this.status.source_file_name}.mp4`
            console.log(url)
            window.open(url)
        },
    },
    created(){
        this.initApp();
    },
    mounted(){
        this.taskQueue = initQueue();
        this.resetAitableSize();
        window.addEventListener('resize', this.resetAitableSize);
    },
    beforeDestroy() {
      window.removeEventListener('resize', this.resetAitableSize);
    },
}
