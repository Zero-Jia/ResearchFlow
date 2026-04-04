<template>
    <div class="state-card error">
      <p>{{ text }}</p>
    </div>
  </template>
  
  <script>
  export default {
    name: "ErrorState",
    props: {
      text: {
        type: String,
        default: "请求失败，请稍后重试。",
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
  }
  
  .error {
    color: #c0392b;
  }
  </style>