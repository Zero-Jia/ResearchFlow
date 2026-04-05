import request from "./request";

export function listSessions() {
  return request.get("/chat/sessions");
}

export function createSession(data) {
  return request.post("/chat/sessions", data);
}

export function listMessages(sessionId) {
  return request.get(`/chat/sessions/${sessionId}/messages`);
}

export function sendMessage(sessionId, data) {
  return request.post(`/chat/sessions/${sessionId}/messages`, data);
}