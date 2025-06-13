// /src/router/index.js
import component from 'element-plus/es/components/tree-select/src/tree-select-option.mjs';
import { createRouter, createWebHistory } from 'vue-router';
  


const routes = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { layout: false } },
  { path: '/', component: () => import('../views/Home.vue') },
  { path: '/customers', component: () => import('../views/Customers.vue') },
  { path: '/customers/add', component: () => import('../views/CustomerAddPage.vue') },
  { path: '/leads', component: () => import('../views/LeadsList.vue') },
  { path: '/leads/add', component: () => import('../views/LeadsAdd.vue') },
  { path: '/orders', name: 'OrdersList', component: () => import('../views/OrdersList.vue') },
  { path: '/funnel', component: () => import('../views/SalesFunnel.vue') },
  { path: '/reports', component: () => import('../views/Reports.vue') },
  { path: '/dashboard', component: () => import('../views/Dashboard.vue') },



];

export default createRouter({
  history: createWebHistory(),
  routes
});