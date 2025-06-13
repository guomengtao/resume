<template>
  <Layout v-if="showLayout">
    <router-view />
  </Layout>
  <router-view v-else />
</template>

<script setup>
import { useRoute } from 'vue-router';
import { computed } from 'vue';
import Layout from './layout/Layout.vue';

const route = useRoute();

const showLayout = computed(() => route.meta.layout !== false);
</script>
