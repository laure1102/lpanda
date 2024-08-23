<template>
    <div class="app">
        <Row>
            <Col span="4">
                <Row>
                    <h1>LPANDA</h1>
                </Row>
                <Row>
                    <Steps :current="step" direction="vertical">
                        <Step v-for="(item,i) in stepNames" :title="item"></Step>
                    </Steps>
                </Row>
            </Col>
            <Col span="20">
                <Row v-if="step==0">
                    <Col span="24"><Form ref="form0" :rules="ruleInline0" :model="status" @submit.native.prevent>
                        <Row>
                            <Col span="12">
                                <FormItem prop="actionType">
                                    <RadioGroup v-model="status.actionType"  @on-change="changeActionType">
                                        <Radio label="new">新的处理</Radio>
                                        <Radio label="continue">继续之前的处理</Radio>
                                    </RadioGroup>
                                </FormItem>
                            </Col>
                            <Col span="12">
                            </Col>
                        </Row>
                        <Row>
                            <Col span="12" v-if="status.actionType=='new'" class="new-file-col">
                                <FormItem label="选择文件" prop="newFilePath">
                                    <Input v-model="status.newFilePath">
                                        <template slot="prefix">
                                            <Button icon="ios-document-outline" ghost type="info" @click="toSelectNewFile"></Button>
                                        </template>
                                    </Input>
                                </FormItem>
                                <input type="file" ref="ltext-file" @change="selectNewFile" v-show="false"/>
                            </Col>
                            <Col span="12" v-else>
                                <FormItem label="中断后继续处理，请选择中间目录" prop="continueDir">
                                    <Select
                                        filterable
                                        v-model="status.continueDir" transfer @on-change="selectContinueDir"
                                    >
                                        <Option
                                        v-for="item in continueList"
                                        :value="item"
                                        :key="item"
                                        >{{ item }}</Option>
                                    </Select>
                                </FormItem>
                            </Col>
                            <Col span="12">
                                <FormItem label="解说角色" prop="role_name">
                                    <Select
                                        filterable
                                        v-model="status.role_name" transfer
                                        :disabled="status.actionType != 'new'"
                                    >
                                        <Option
                                        v-for="item in options.rolenames"
                                        :value="item"
                                        :key="item"
                                        >{{ item }}</Option>
                                    </Select>
                                </FormItem>
                            </Col>
                            <Col span="12">
                                <FormItem label="语速" prop="rate">
                                    <Select
                                        filterable
                                        v-model="status.rate" transfer
                                        :disabled="status.actionType != 'new'"
                                    >
                                    <Option
                                        v-for="item in options.rates"
                                        :value="item"
                                        :key="item"
                                        >{{ item }}</Option>
                                    </Select>
                                </FormItem>
                            </Col>
                            <Col span="12">
                                <FormItem label="音量" prop="volume">
                                    <Select
                                        filterable
                                        v-model="status.volume" transfer
                                        :disabled="status.actionType != 'new'"
                                    >
                                    <Option
                                        v-for="item in options.volumes"
                                        :value="item"
                                        :key="item"
                                        >{{ item }}</Option>
                                    </Select>
                                </FormItem>
                            </Col>
                            <Col span="12" v-if="status.actionType == 'new'">
                                <FormItem label="缓存目录" prop="temp_dir">
                                    <Input v-model="status.temp_dir" disabled>
                                    </Input>
                                </FormItem>
                            </Col>
                            <Col span="12" v-if="status.actionType == 'continue'">
                                <FormItem label="当前状态">
                                    <Input :value="stepNames[cal_step_status]" disabled></Input>
                                </FormItem>
                            </Col>
                        </Row>
                    </Form></Col>
                    <Row>
                        <Col>
                            <ButtonGroup>
                                <Button type="primary" icon="ios-skip-forward" @click="next0" :loading="loading.next0">
                                    <span v-if="status.actionType=='new'">下一步</span>
                                    <span v-if="status.actionType=='continue'">继续处理</span>
                                </Button>
                            </ButtonGroup>
                        </Col>
                    </Row>
                </Row>
                <Row v-if="step!=0">
                    <Col span="24">
                        <Row><Col span="24"><Form ref="form1" :model="status" @submit.native.prevent><Row>
                            <Col span="6">
                                <FormItem label="缓存目录" prop="temp_dir">
                                    <Input v-model="status.temp_dir" disabled>
                                    </Input>
                                </FormItem>
                            </Col>
                            <Col span="6">
                                <FormItem label="解说角色" prop="role_name">
                                    <Select
                                        filterable
                                        v-model="status.role_name" transfer
                                        disabled
                                    >
                                        <Option
                                        v-for="item in options.rolenames"
                                        :value="item"
                                        :key="item"
                                        >{{ item }}</Option>
                                    </Select>
                                </FormItem>
                            </Col>
                            <Col span="6">
                                <FormItem label="语速" prop="rate">
                                    <Select
                                        filterable
                                        v-model="status.rate" transfer
                                        disabled
                                    >
                                    <Option
                                        v-for="item in options.rates"
                                        :value="item"
                                        :key="item"
                                        >{{ item }}</Option>
                                    </Select>
                                </FormItem>
                            </Col>
                            <Col span="6">
                                <FormItem label="音量" prop="volume">
                                    <Select
                                        filterable
                                        v-model="status.volume" transfer
                                        disabled
                                    >

                                    <Option
                                        v-for="item in options.volumes"
                                        :value="item"
                                        :key="item"
                                        >{{ item }}</Option>
                                    </Select>
                                </FormItem>
                            </Col>
                        </Row></Form></Col></Row>
                    </Col>
                </Row>
                <Row v-if="step == 1">
                    <Col span="24">
                        <div>{{ status.current_stage_descr }}</div>
                        <div>当前进度:{{ status.mp3_done_count }} / {{ status.sce_count }}</div>
                    </Col>
                    <Col span="24">
                        <Progress :percent="Math.floor(status.mp3_done_count *100 / status.sce_count)" :stroke-width="20" text-inside />
                    </Col>
                    <Col span="24" class="next-buttons">
                        <Button type="primary" icon="md-bulb" @click="next1_start" :loading="loading.next1"
                            :disabled = "status.current_stage =='tts_done'">开始处理</Button>
                        <Button type="primary" icon="ios-skip-forward" @click="next1_stop"
                        v-if = "status.current_stage =='tts_done'">下一步</Button>
                    </Col>
                </Row>
                <Row v-if="step == 2">
                        <Col span="24" v-if="taskQueue.length() == 0"><Row>
                        <Col span="24">
                            <div>{{ status.current_stage_descr }}</div>
                            <div>当前进度:{{ status.gpt_done_count }} / {{ status.sce_count }}</div>
                        </Col>
                        <Col span="24">
                            <Progress :percent="Math.floor(status.gpt_done_count *100 / status.sce_count)" :stroke-width="20" text-inside />
                        </Col>
                    </Row></Col>
                    <Col span="24" v-else><Row>
                        <Col span="24">
                            <div>重新生成中</div>
                            <div>队列任务数量:{{ taskQueue.length() }}</div>
                        </Col>
                    </Row></Col>
                    <Col span="24" class="next-buttons">
                        <Button type="primary" icon="md-bulb" @click="next2_start" :loading="loading.next2"
                            :disabled = "status.current_stage =='aiprompt_done'">开始处理</Button>
                        <Button type="primary" icon="ios-skip-forward" @click="next2_stop" :disabled="taskQueue.length() > 0"
                        v-if = "status.current_stage =='aiprompt_done'">下一步</Button>
                    </Col>
                    <Col span="24">
                        <Table :height="aitableHeight" :columns="aicolumns" :data="sces"></Table>
                    </Col>
                </Row>
                <Row v-if="step == 3">
                        <Col span="24" v-if="taskQueue.length() == 0"><Row>
                        <Col span="24">
                            <div>{{ status.current_stage_descr }}</div>
                            <div>当前进度:{{ status.tutu_done_count }} / {{ status.sce_count }}</div>
                        </Col>
                        <Col span="24">
                            <Progress :percent="Math.floor(status.tutu_done_count *100 / status.sce_count)" :stroke-width="20" text-inside />
                        </Col>
                    </Row></Col>
                    <Col span="24" v-else><Row>
                        <Col span="24">
                            <div>重新生成中</div>
                            <div>队列任务数量:{{ taskQueue.length() }}</div>
                        </Col>
                    </Row></Col>
                    <Col span="24" class="next-buttons">
                        <Button type="primary" icon="md-bulb" @click="next3_start" :loading="loading.next3"
                            :disabled = "status.current_stage =='aitutu_done'">开始处理</Button>
                        <Button type="primary" icon="ios-skip-forward" @click="next3_stop" :disabled="taskQueue.length() > 0"
                        v-if = "status.current_stage =='aitutu_done'">下一步</Button>
                        <RadioGroup v-model="tutuMode" type="button" button-style="solid" class="tutu-mode">
                            <Radio label="table"><Icon type="md-list"></Icon></Radio>
                            <Radio label="list"><Icon type="ios-apps"></Icon></Radio>
                        </RadioGroup>
                    </Col>
                    <Col span="24" v-if="tutuMode=='table'">
                        <Table :height="aitableHeight" :columns="tutucolumns" :data="sces"></Table>
                    </Col>
                    <Col span="24" v-if="tutuMode=='list'">
                        <div class="tutu-list-container">
                            <template v-for="(row,i) in sces">
                                <div v-for="(tutu,t) in row.tutu" class="tutu-list-div">
                                    <img :src="tutu.src" @click="tutuModalShow(this,row,tutu)">
                                    <Button :type='redoArr.includes(`p_${row.seqnum}:${tutu.id}`)?"error":"info"' icon="md-refresh" shape="circle" :loading="redoArr.includes(`p_${row.seqnum}:${tutu.id}`)"
                                    @click="doRegenTutu(this,row,tutu)"
                                    v-if="status.current_stage == 'aitutu_done'"></Button>
                                </div>
                            </template>
                        </div>
                    </Col>
                </Row>
                <Row v-if="step == 4">
                        <Col span="24"><Row>
                        <Col span="24">
                            <div>{{ status.current_stage_descr }}</div>
                            <div>当前进度:{{ status.mp4_done_count }} / {{ status.sce_count }}</div>
                        </Col>
                        <Col span="24">
                            <Progress :percent="Math.floor(status.mp4_done_count *100 / status.sce_count)" :stroke-width="20" text-inside />
                        </Col>
                    </Row></Col>
                    <Col span="24" class="next-buttons">
                        <Button type="primary" icon="md-bulb" @click="next4_start" :loading="loading.next4"
                            :disabled = "status.current_stage =='video_done'">开始处理</Button>
                        <Button type="primary" icon="ios-skip-forward" @click="next4_stop"
                        v-if = "status.current_stage =='video_done'">下一步</Button>
                    </Col>
                    <Col span="24">
                        <div class="videos-container">
                            <div v-for="(row,i) in sces" class="video-sce-div" :class="!!row.mp4aufile?'done':'undo'"
                            @click="showVideo(row)"
                            :style="!!row.mp4aufile?'background-image: url(\'' + row.tutu[0].src.replaceAll('\\','/') + '\');':''">
                                <Icon type="md-play" size="40" color="#ffffff" v-if="row.mp4aufile"/>
                            </div>
                        </div>
                    </Col>
                </Row>
                <Row v-if="step == 5">
                        <Col span="24"><Row>
                        <Col span="24">
                            <div>{{ status.current_stage_descr }}</div>
                        </Col>
                    </Row></Col>
                    <Col span="24" class="next-buttons">
                        <Button type="primary" icon="md-bulb" @click="next5_start" :loading="loading.next5"
                            :disabled = "status.current_stage =='merge_video_done'">开始合并视频</Button>
                        <Button type="primary" icon="ios-skip-forward" @click="next5_stop"
                        v-if = "status.current_stage =='merge_video_done'">打开视频文件目录</Button>
                    </Col>
                    <Col span="24">
                        <div class="videos-container">
                            <div v-if="status.current_stage == 'merge_video_done' && !!sces[0]"  class="video-merge-done"
                            >
                                <video width="768" height="500" controls>
                                    <source :src="status.work_dir +'/cache/' + status.temp_dir +'/' +status.source_file_name+'.mp4'" type="video/mp4">

                                </video>
                            </div>
                            <div v-else>
                                合并中...
                            </div>
                        </div>
                    </Col>
                </Row>
            </Col>
        </Row>
        <Modal v-model="promptModal.show" footer-hide :title="'序号:'+promptModal.row.seqnum" :width="60" :mask-closable="false" :closable="false">
            <Row><Col span="24"><Form ref="promptModalForm" :model="promptModal.row" @submit.native.prevent>
                <Row>
                    <Col span="24">
                        <FormItem label="内容">
                            <Input v-model="promptModal.row.text" type="textarea" disabled :rows="10"/>
                        </FormItem>
                    </Col>
                    <Col span="24">
                        <FormItem label="提示词">
                            <Input v-model="promptModal.row.prompt" type="textarea" :disabled="promptModal.readonly" :rows="10"/>
                        </FormItem>
                    </Col>
                </Row>
                <Row>
                    <Col span="24" class="modal-buttons">
                        <Button type="info" icon="ios-list" @click="prompt_return"  :disabled="loading.prompt_save || loading.prompt_regen">返回</Button>
                        <Button type="primary" icon="md-checkmark" v-if="!promptModal.readonly" @click="prompt_save" :loading="loading.prompt_save" :disabled="loading.prompt_regen">修改提示词</Button>
                        <Button type="success" icon="md-bulb" v-if="!promptModal.readonly" @click="prompt_regen" :loading="loading.prompt_regen"
                          :disabled="loading.prompt_save || status.current_stage != 'aiprompt_done'">重新生成提示词</Button>
                    </Col>
                </Row>
            </Form></Col></Row>
        </Modal>


        <Modal v-model="tutuModal.show" footer-hide :title="'序号:'+tutuModal.row.seqnum +':'+tutuModal.tutu.id" :width="830" :mask-closable="false" :closable="false">
            <Row><Col span="24"><Form ref="tutuModalForm" :model="tutuModal.row" @submit.native.prevent>
                <Row>
                    <Col span="24">
                        <img :src="tutuModal.tutu.src" width="768">
                    </Col>
                </Row>
                <Row>
                    <Col span="24" class="modal-buttons">
                        <Button type="info" icon="ios-list" @click="tutuModalReturn"  :disabled="loading.tutu_regen">返回</Button>
                        <Button type="success" icon="md-bulb" @click="tutu_regen" :loading="loading.tutu_regen"
                         :disabled="status.current_stage != 'aitutu_done'">重新生成图片</Button>
                        <Button class="tutu_next_btn" type="dashed" icon="ios-arrow-dropright" @click="tutu_next"
                          :disabled="loading.tutu_regen || status.current_stage != 'aitutu_done'">下一张</Button>
                        <Button class="tutu_last_btn" type="dashed" icon="ios-arrow-dropleft" @click="tutu_last"
                          :disabled="loading.tutu_regen || status.current_stage != 'aitutu_done'">上一张</Button>
                    </Col>
                </Row>
            </Form></Col></Row>
        </Modal>
    </div>
</template>

<script src="./App.js">
</script>

<style lang="scss">
.app{
    background: #fff;
    border-radius: 4px;
    margin: 0 10px;
    padding: 5px;
    border: 1px solid #f3f3f3;
}

.next-buttons{
    margin-top:10px;
}

.next-buttons button{
    margin-right: 5px;
    margin-bottom: 5px;
}
.column-text{
    cursor: pointer;
}

.modal-buttons button{
    margin-right: 5px;
    margin-bottom: 5px;
}
.tutu-column-div{
    display: flex;
    flex-wrap: wrap;
}
.tutu-column-div .tutu-div{
    width: 100px;
    margin-bottom: 5px;
    border: 1px solid #dbd6d6;
    margin-right: 5px;
    text-align: center;
}
.tutu-column-div .tutu-div img{
    width: 100px;
    cursor: pointer;
}
.tutu-column-div .tutu-div button{
    height:22px;
    width:22px;
    font-size: 12px;
    margin-bottom: 2px;
}
.tutu_next_btn{
    float:right
}
.tutu_last_btn{
    float:right
}
.tutu-mode{
    float:right
}
.tutu-list-container{
    display: flex;
    flex-wrap: wrap;
}
.tutu-list-div{
    width: 200px;
    margin-bottom: 5px;
    border: 1px solid #dbd6d6;
    margin-right: 5px;
    text-align: center;
}
.tutu-list-div img{
    width: 200px;
    cursor: pointer;
}
.tutu-list-div button{
    height:22px;
    width:22px;
    font-size: 12px;
    margin-bottom: 2px;
}

.videos-container{
    display: flex;
    flex-wrap: wrap;
}

.video-sce-div{
    width: 100px;
    height: 100px;
    margin: 5px;
    background-repeat: no-repeat; /* 不重复图片 */
    background-size: cover; /* 图片覆盖整个div */
    display: flex;
    align-items: center;
    justify-content: center;
}

.video-sce-div.undo{
    background-color: #e3f8b0;
}
.video-sce-div.done{
    background-color: #9bf59f;
}
.video-sce-div i{
    transition: transform 0.3s ease; /* 平滑过渡效果 */
}
.video-sce-div:hover i{
    /* 鼠标悬停在.a上时，.b的样式 */
    transform: scale(1.5); /* 放大1.5倍 */
}

.video-sce-div.done{
    cursor: pointer;
}
.video-merge-done{
    background-color: #9bf59f;
    width: 768px;
    height: 500px;
    background-repeat: no-repeat; /* 不重复图片 */
    background-size: cover; /* 图片覆盖整个div */
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}
.video-merge-done i{
    transition: transform 0.3s ease; /* 平滑过渡效果 */
}
.video-merge-done:hover i{
    /* 鼠标悬停在.a上时，.b的样式 */
    transform: scale(1.5); /* 放大1.5倍 */
}
</style>
