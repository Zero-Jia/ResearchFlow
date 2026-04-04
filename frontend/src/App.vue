<template>
  <div id="app">
    <header class="app-header">
      <h1>JobKG-Agent</h1>
      <p>基于知识图谱与 LangChain Agent 的智能职位推荐系统</p>

      <nav class="nav-links">
        <button @click="$router.push('/job/recommend')">职位推荐</button>
        <button @click="$router.push('/job/history')">历史记录</button>
        <button @click="$router.push('/graph/view')">图谱展示</button>
      </nav>
    </header>

    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<style>
body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
  background: #f5f7fb;
  color: #222;
}

#app {
  min-height: 100vh;
}

.app-header {
  background: #1f4e79;
  color: white;
  padding: 20px 32px;
}

.app-header h1 {
  margin: 0 0 8px 0;
  font-size: 28px;
}

.app-header p {
  margin: 0 0 14px 0;
  opacity: 0.9;
}

.nav-links {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.nav-links button {
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 8px 14px;
  cursor: pointer;
}

.app-main {
  padding: 24px 32px;
}
</style>