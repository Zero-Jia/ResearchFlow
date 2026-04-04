import axios from "axios";

const request = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  timeout: 60000,
});

export function createJobTask(data) {
  return request.post("/job/task/create", data);
}

export function getJobTaskView(taskId) {
  return request.get(`/job/task/view/${taskId}`);
}

export function getJobTaskHistory(userId) {
  return request.get(`/job/task/history/${userId}`);
}

export function getJobTaskDetail(taskId) {
  return request.get(`/job/task/detail/${taskId}`);
}