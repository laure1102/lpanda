<template>
    <div id="root" class="root">
        <Layout>
            <Content>
                <router-view></router-view>
            </Content>
        </Layout>
        <Modal v-model="settingModal" fullscreen footer-hide :closable="false">
            <Setting :closeModal="closeModal"></Setting>
        </Modal>
    </div>
</template>

<script>
import Utils from '@/../libs/utils'
import Setting from './pages/Setting.vue'
export default {
    name: 'Main',
    components:{Setting},
    data(){
        return {
            activeMenu:"app",
            settingModal:false,
        }
    },
    created(){
        Utils.ipcReceiveAways('open-setting-page', (event) => {  
            this.settingModal = true;
        });
    },
    methods:{
        closeModal(){
            this.settingModal = false;
        }
    },
}
</script>

<style lang="scss" scoped>
.ivu-layout-header{
    background: none;
    padding: 0 10px;
}
</style>
