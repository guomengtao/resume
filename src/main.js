import { createApp } from "vue";
import './style.css'; // Move this up to load global styles first
import App from "./App.vue";
import router from "./router";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";
createApp(App).use(router).use(ElementPlus).mount("#app");
