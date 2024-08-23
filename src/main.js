import Vue from 'vue'
import Main from './Main.vue'
import router from './router'
import ViewUI from 'view-design';

// import style
import 'view-design/dist/styles/iview.css';

Vue.use(ViewUI);

new Vue({
  router,
  render: h => h(Main)
}).$mount('#root')