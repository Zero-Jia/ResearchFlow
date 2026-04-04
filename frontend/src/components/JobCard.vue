<template>
    <div class="job-card">
      <h3>{{ job.job_name }}</h3>
      <p><strong>匹配分数：</strong>{{ job.score }}</p>
  
      <div class="section">
        <strong>已匹配技能：</strong>
        <span
          v-for="skill in job.matched_skills"
          :key="skill"
          class="tag success"
        >
          {{ skill }}
        </span>
        <span v-if="!job.matched_skills || job.matched_skills.length === 0">暂无</span>
      </div>
  
      <div class="section">
        <strong>缺失技能：</strong>
        <span
          v-for="skill in job.missing_skills"
          :key="skill"
          class="tag warning"
        >
          {{ skill }}
        </span>
        <span v-if="!job.missing_skills || job.missing_skills.length === 0">暂无</span>
      </div>
  
      <div class="section">
        <strong>推荐课程：</strong>
        <span
          v-for="course in job.recommended_courses"
          :key="course"
          class="tag info"
        >
          {{ course }}
        </span>
        <span v-if="!job.recommended_courses || job.recommended_courses.length === 0">暂无</span>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "JobCard",
    props: {
      job: {
        type: Object,
        required: true,
      },
    },
  };
  </script>
  
  <style scoped>
  .job-card {
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 16px;
    margin-top: 16px;
    background: #fcfcfd;
  }
  
  .job-card h3 {
    margin-top: 0;
    margin-bottom: 10px;
  }
  
  .section {
    margin-top: 12px;
    line-height: 2;
  }
  
  .tag {
    display: inline-block;
    margin-right: 8px;
    margin-top: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    background: #e5e7eb;
    font-size: 13px;
  }
  
  .success {
    background: #d1fae5;
  }
  
  .warning {
    background: #fef3c7;
  }
  
  .info {
    background: #dbeafe;
  }
  </style>