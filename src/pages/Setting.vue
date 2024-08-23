<template>
    <div class="container-setting">
      <Form ref="settingForm" :rules="ruleInline" :model="setting" label-position="top" @submit.native.prevent>
        <Row>
            <Col span="24">
                <Card title="基本设置">
                    <Row>
                        <Col span="12">
                            <FormItem label="工作目录" prop="work_dir">
                                <Input  v-model="setting.work_dir">
                                </Input>
                            </FormItem>
                        </Col>
                        <Col span="6">
                            <FormItem label="分镜拆分字数(一个分镜一张图片)" prop="scene_split_chars">
                                <InputNumber  v-model="setting.scene_split_chars" :max="500" :min="50" :step="10">
                                </InputNumber>
                            </FormItem>
                        </Col>
                        <Col span="6">
                            <FormItem label="转语音并发数" prop="tts_batch_cnt">
                                <InputNumber  v-model="setting.tts_batch_cnt" :max="50" :min="1" :step="10">
                                </InputNumber>
                            </FormItem>
                        </Col>
                    </Row>
                </Card>
            </Col>
        </Row>
        <Row>
            <Col span="24">
                <Card title="推理设置">
                    <Row>
                        <Col span="6">
                            <FormItem label="推理类型" prop="chat_type">
                                <RadioGroup v-model="setting.chat_type">
                                    <Radio label="gpt">Chat-gpt</Radio>
                                    <Radio label="glm">Chat-glm</Radio>
                                </RadioGroup>
                            </FormItem>
                        </Col>
                        <Col span="12" v-if="setting.chat_type=='gpt'">
                            <FormItem label="GPT服务器地址/代理地址" prop="gpt_api_url">
                                <Input  v-model="setting.gpt_api_url">
                                </Input>
                            </FormItem>
                        </Col>
                        <Col span="6" v-if="setting.chat_type=='gpt'">
                            <FormItem label="GPT key" prop="gpt_api_key">
                                <Input  v-model="setting.gpt_api_key">
                                </Input>
                            </FormItem>
                        </Col>
                        <Col span="12" v-if="setting.chat_type=='glm'">
                            <FormItem label="GLM服务器地址" prop="glm_api_url">
                                <Input  v-model="setting.glm_api_url">
                                </Input>
                            </FormItem>
                        </Col>
                    </Row>
                    <Row>
                        <Col span="24">
                            <FormItem label="推理魔法" prop="chat_magic_text">
                                <Input v-model="setting.chat_magic_text" type="textarea" :rows="5"/>
                            </FormItem>
                        </Col>
                    </Row>
                </Card>
            </Col>
        </Row>
        <Row>
            <Col span="24">
                <Card title="SD绘图设置">
                    <Row>
                        <Col span="20">
                            <FormItem label="SD服务器地址" prop="sd_url">
                                <Input  v-model="setting.sd_url">
                                </Input>
                            </FormItem>
                        </Col>
                        <Col span="4">
                            <FormItem label="测试连通性">
                                <Button @click="refreshOptions" type="success" :loading="refresh_loading">抓取模型列表</Button>
                            </FormItem>
                        </Col>
                    </Row>
                    <Row>
                        <Col span="4">
                            <FormItem label="图片高度" prop="height">
                                <InputNumber  v-model="setting.height"  :min="100" :step="100">
                                </InputNumber>
                            </FormItem>
                        </Col>
                        <Col span="4">
                            <FormItem label="图片宽度" prop="width">
                                <InputNumber  v-model="setting.width"  :min="100" :step="100">
                                </InputNumber>
                            </FormItem>
                        </Col>
                        <Col span="4">
                            <FormItem label="SD并发数" prop="tutu_batch_cnt">
                                <InputNumber  v-model="setting.tutu_batch_cnt"  :min="1" :step="1">
                                </InputNumber>
                            </FormItem>
                        </Col>
                        <Col span="4">
                            <FormItem label="单图持续秒数" prop="seconds_per_tutu">
                                <InputNumber  v-model="setting.seconds_per_tutu"  :min="0" :step="1">
                                </InputNumber>
                            </FormItem>
                        </Col>
                        <Col span="4">
                            <FormItem label="采样方法" prop="sampler_index">
                                <Select
                                    filterable
                                    v-model="setting.sampler_index"
                                >
                                    <Option
                                    v-for="item in options.sd_samplers"
                                    :value="item.name"
                                    :key="item.name"
                                    >{{ item.name }}</Option>
                                </Select>
                            </FormItem>
                        </Col>
                    </Row>
                    <Row>
                        <Col span="12">
                            <FormItem label="SD模型" prop="sd_model_checkpoint">
                                <Select
                                    filterable
                                    v-model="setting.sd_model_checkpoint"
                                >
                                    <Option
                                    v-for="item in options.sd_models"
                                    :value="item.model_name"
                                    :key="item.model_name"
                                    >{{ item.model_name }}</Option>
                                </Select>
                            </FormItem>
                        </Col>
                        <Col span="12">
                            <FormItem label="SD VAE" prop="sd_vae">
                                <Select
                                    filterable
                                    v-model="setting.sd_vae"
                                >
                                    <Option
                                    v-for="item in options.sd_vaes"
                                    :value="item.model_name"
                                    :key="item.model_name"
                                    >{{ item.model_name }}</Option>
                                </Select>
                            </FormItem>
                        </Col>
                    </Row>
                    <Row>
                        <Col span="24">
                            <FormItem label="追加的正向提示词-前置" prop="add_prompt_bef">
                                <Input v-model="setting.add_prompt_bef" type="textarea" :rows="5"/>
                            </FormItem>
                        </Col>
                    </Row>
                    <Row>
                        <Col span="24">
                            <FormItem label="追加的正向提示词-后置" prop="add_prompt">
                                <Input v-model="setting.add_prompt" type="textarea" :rows="5"/>
                            </FormItem>
                        </Col>
                    </Row>
                    <Row>
                        <Col span="24">
                            <FormItem label="反向提示词" prop="negative_prompt">
                                <Input v-model="setting.negative_prompt" type="textarea" :rows="5"/>
                            </FormItem>
                        </Col>
                    </Row>
                </Card>
            </Col>
        </Row>
        <Row>
            <Col span="24">
                <Card title="视频设置">
                    <Row>
                        <Col span="12">
                            <FormItem label="水印图片路径" prop="watermark_image">
                                <Input  v-model="setting.watermark_image">
                                </Input>
                            </FormItem>
                        </Col>
                        <Col span="6">
                            <FormItem label="水印位置" prop="watermark_position">
                                <Select
                                    v-model="setting.watermark_position"
                                >
                                    <Option
                                    v-for="item in options.watermark_position_list"
                                    :value="item"
                                    :key="item"
                                    >{{ item }}</Option>
                                </Select>
                            </FormItem>
                        </Col>
                        <Col span="6">
                            <FormItem label="FPS" prop="fps">
                                <InputNumber  v-model="setting.fps"  :min="10" :step="5">
                                </InputNumber>
                            </FormItem>
                        </Col>
                    </Row>
                </Card>
            </Col>
        </Row>
        <Row class="footer">
            <Col span="24" class="buttons">
                <Button  @click="doSave" :loading="saveLoading" icon="ios-checkmark" type="primary">保存</Button>
                <Button  @click="doCancel" icon="ios-list" type="success">取消</Button>
            </Col>
        </Row>
      </Form>
    </div>
</template>

<script>
    import { Message, Row } from "view-design";
    import Utils from '@/../libs/utils'
    export default {
        name:"Setting",
        props:{
            closeModal:{
                required:false,
                type:Function
            }
        },
        data(){
            return {
                setting:{
                },
                saveLoading:false,
                ruleInline:{
                    work_dir:[
                        {
                            required:true,
                            message:"不能为空",
                            trigger:"blur",
                        },
                    ],
                },
                options:{
                    sd_samplers:[{
                        name:"1",
                    }],
                    sd_models:[{
                        model_name:"md1",
                    }],
                    sd_vaes:[{
                        model_name:"vae1",
                    }],
                    watermark_position_list:[],
                },
                refresh_loading:false,
            }
        },
        methods:{
            initSetting(){
                Utils.ipcSend('refresh-options');  
                Utils.ipcReceive('refresh-options-done', (data) => {
                    this.options = data.options;
                });  
                Utils.ipcSend('get-config');  
                Utils.ipcReceive('get-config-done', (data) => {
                    this.setting = data.config;
                    this.options = data.options;
                });
            },
            async refreshOptions(){
                
                let valid = Utils.validateForm(this, "settingForm");
                if(!valid){
                    return;
                }
                this.saveLoading = true;
                this.refresh_loading = true;
                Utils.ipcSend('save-config', this.setting); 
                Utils.ipcReceive('save-config-done', (data) => {  
                    this.saveLoading = false;
                    if(data.rslt){
                        Utils.ipcSend('refresh-options');  
                        Utils.ipcReceive('refresh-options-done', (data) => {
                            this.refresh_loading = false;
                            if(data.options.sd_models.length > 0){
                                this.options = data.options;
                                Message.info("拉取模型成功。");
                            }else{
                                Message.error("拉取模型失败，请检查sd配置。");
                            }
                        });
                    }else{                       
                        Message.error("保存失败");
                    }
                });    
            },
            async doCancel(){
                this.closeModal();
            },
            async doSave(){
                let valid = Utils.validateForm(this, "settingForm");
                if(!valid){
                    return;
                }
                this.saveLoading = true;
                Utils.ipcSend('save-config', this.setting); 
                Utils.ipcReceive('save-config-done', (data) => {  
                    this.saveLoading = false;
                    console.log(data)
                    if(data.rslt){
                        Message.success("保存成功");
                        Utils.ipcSend('reload-app'); 
                        this.closeModal();
                    }else{                       
                        Message.error("保存失败");
                    }
                });  
            },
        },
        created(){
            this.initSetting();
        },
    }
</script>

<style>
.footer{
    position: fixed;
    bottom: 2px;
    width: 100%;
}
.footer .buttons{
    background: #f1e7e7;
    padding-right:50px;
}
.footer button{
    float:right;
    margin-right:5px;
}
</style>