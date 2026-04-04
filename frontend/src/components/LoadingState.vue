<template>
    <div class="state-card">
      <p>{{ text }}</p>
    </div>
  </template>
  
  <script>
  export default {
    name: "LoadingState",
    props: {
      text: {
        type: String,
        default: "加载中...",
      },
    },
  };
  </script>
  
  <style scoped>
  .state-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
    text-align: center;
    color: #444;
  }
  </style>