// /src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
  


const routes = [
  { path: '/', component: () => import('../views/Home.vue') },
  { path: '/customers', component: () => import('../views/Customers.vue') },
  { path: '/customers/add', component: () => import('../views/CustomerAddPage.vue') },
  { path: '/login', component: () => import('../views/Login.vue') },
  { path: '/leads', component: () => import('../views/LeadsList.vue') },
  { path: '/leads/add', component: () => import('../views/LeadsAdd.vue') }
];

export default createRouter({
  history: createWebHistory(),
  routes
});