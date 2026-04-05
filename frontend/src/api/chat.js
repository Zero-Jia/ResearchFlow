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

// 原来的普通发送接口先保留
export function sendMessage(sessionId, data) {
  return request.post(`/chat/sessions/${sessionId}/messages`, data);
}

// 新增：流式发送接口
export async function streamMessage(sessionId, data) {
  const token = localStorage.getItem("jobkg_token");

  const response = await fetch(
    `http://127.0.0.1:8000/api/chat/sessions/${sessionId}/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    }
  );

  if (!response.ok) {
    let detail = "发送失败";
    try {
      const err = await response.json();
      detail = err.detail || detail;
    } catch (e) {
      // 忽略 JSON 解析失败
    }
    throw new Error(detail);
  }

  return response;
}