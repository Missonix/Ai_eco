<template>
  <!-- 电脑端导航栏 -->
  <nav class="hidden md:block bg-white shadow">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex justify-between h-16">
        <div class="flex">
          <router-link
            to="/"
            class="flex items-center px-4"
            :class="
              $route.path === '/' ? 'text-indigo-600 border-b-2 border-indigo-600' : 'text-gray-600'
            "
          >
            首页
          </router-link>
        </div>
        <div class="flex">
          <router-link
            to="/user"
            class="flex items-center px-4"
            :class="
              $route.path === '/user'
                ? 'text-indigo-600 border-b-2 border-indigo-600'
                : 'text-gray-600'
            "
          >
            我的
          </router-link>
        </div>
      </div>
    </div>
  </nav>

  <!-- 移动端底部导航栏 -->
  <nav class="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t">
    <div class="grid grid-cols-2 h-14">
      <router-link
        to="/"
        class="flex flex-col items-center justify-center"
        :class="$route.path === '/' ? 'text-indigo-600' : 'text-gray-600'"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
          />
        </svg>
        <span class="text-xs mt-1">首页</span>
      </router-link>
      <router-link
        to="/user"
        class="flex flex-col items-center justify-center"
        :class="$route.path === '/user' ? 'text-indigo-600' : 'text-gray-600'"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
          />
        </svg>
        <span class="text-xs mt-1">我的</span>
      </router-link>
    </div>
  </nav>
</template>

<script setup lang="ts">
// Navigation component
</script>
