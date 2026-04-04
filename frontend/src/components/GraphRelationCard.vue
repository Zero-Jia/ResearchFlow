<template>
    <div class="graph-card">
      <div class="job-box">
        <h2>{{ data.job_name }}</h2>
        <p><strong>类别：</strong>{{ data.category }}</p>
        <p><strong>描述：</strong>{{ data.description }}</p>
      </div>
  
      <div class="arrow">↓ requires</div>
  
      <div class="skills-grid">
        <div v-for="skill in data.skills" :key="skill.name" class="skill-card">
          <div class="skill-name">{{ skill.name }}</div>
          <div class="arrow-small">↓ teaches</div>
          <div class="course-list">
            <span
              v-for="course in skill.courses"
              :key="course"
              class="course-tag"
            >
              {{ course }}
            </span>
  
            <span
              v-if="!skill.courses || skill.courses.length === 0"
              class="course-empty"
            >
              暂无课程
            </span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "GraphRelationCard",
    props: {
      data: {
        type: Object,
        required: true,
      },
    },
  };
  </script>
  
  <style scoped>
  .graph-card {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  
  .job-box {
    background: #eef6ff;
    border: 1px solid #cfe3f8;
    border-radius: 12px;
    padding: 18px;
  }
  
  .arrow,
  .arrow-small {
    text-align: center;
    color: #555;
    font-weight: 600;
  }
  
  .skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 16px;
  }
  
  .skill-card {
    background: #fffdf5;
    border: 1px solid #f1e2a8;
    border-radius: 12px;
    padding: 16px;
  }
  
  .skill-name {
    font-weight: 700;
    font-size: 16px;
    text-align: center;
    margin-bottom: 8px;
  }
  
  .course-list {
    margin-top: 8px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .course-tag {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: #dbeafe;
    font-size: 13px;
  }
  
  .course-empty {
    color: #888;
    font-size: 13px;
  }
  </style>