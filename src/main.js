import { createApp } from "vue";
import './style.css'; // Move this up to load global styles first
import App from "./App.vue";
import router from "./router";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
import zhCn from 'element-plus/dist/locale/zh-cn.mjs';
zhCn.el.table.emptyText = 'Loading...';
createApp(App).use(router).use(ElementPlus, { locale: zhCn }).mount("#app");
