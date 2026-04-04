import axios from "axios";

const request = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
  timeout: 60000,
});

export function getJobGraphView(jobName) {
  return request.get(`/graph/job/${encodeURIComponent(jobName)}`);
}