import axios from "axios";

const request = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  timeout: 30000,
});

export function createJobTask(data) {
  return request.post("/job/task/create", data);
}

export function getJobTaskView(taskId) {
  return request.get(`/job/task/view/${taskId}`);
}