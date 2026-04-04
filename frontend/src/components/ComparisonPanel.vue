<template>
    <div class="comparison-panel">
      <h2>岗位对比结果</h2>
      <p class="multiline">{{ comparison }}</p>
    </div>
  </template>
  
  <script>
  export default {
    name: "ComparisonPanel",
    props: {
      comparison: {
        type: String,
        default: "",
      },
    },
  };
  </script>
  
  <style scoped>
  .comparison-panel {
    background: white;
    border-radius: 12px;
    padding: 22px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  }
  
  .multiline {
    white-space: pre-wrap;
    line-height: 1.8;
  }
  </style>