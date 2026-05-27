<template>
  <div class="app">
    <header class="header">
      <h1>📋 Todolist</h1>
      <p class="subtitle">管理你的日常任务</p>
    </header>
    <main class="main">
      <TodoForm
        :editing-todo="editingTodo"
        @add="handleAdd"
        @update="handleUpdate"
        @cancel="handleCancelEdit"
      />
      <div v-if="loading" class="loading">加载中...</div>
      <TodoList
        v-else
        :todos="todos"
        @edit="handleEdit"
        @delete="handleDelete"
        @toggle="handleToggle"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TodoForm from './components/TodoForm.vue'
import TodoList from './components/TodoList.vue'

const API = '/api/todos'

const todos = ref([])
const editingTodo = ref(null)
const loading = ref(true)

function toBool(v) { return typeof v === 'number' ? v !== 0 : Boolean(v) }

async function fetchTodos() {
  loading.value = true
  try {
    const res = await fetch(API)
    const data = await res.json()
    todos.value = data.map(t => ({ ...t, completed: toBool(t.completed) }))
  } catch (e) {
    console.error('获取任务失败', e)
  } finally {
    loading.value = false
  }
}

async function handleAdd(title) {
  try {
    const res = await fetch(API, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, completed: false })
    })
    const todo = await res.json()
    todos.value.unshift({ ...todo, completed: toBool(todo.completed) })
  } catch (e) { console.error('添加失败', e) }
}

function handleEdit(todo) {
  editingTodo.value = { ...todo }
}

async function handleUpdate(todo) {
  try {
    const res = await fetch(`${API}/${todo.id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: todo.title, completed: todo.completed })
    })
    const updated = await res.json()
    const index = todos.value.findIndex(t => t.id === todo.id)
    if (index !== -1) {
      todos.value[index] = { ...updated, completed: toBool(updated.completed) }
    }
    editingTodo.value = null
  } catch (e) { console.error('更新失败', e) }
}

function handleCancelEdit() {
  editingTodo.value = null
}

async function handleDelete(id) {
  try {
    await fetch(`${API}/${id}`, { method: 'DELETE' })
    todos.value = todos.value.filter(t => t.id !== id)
  } catch (e) { console.error('删除失败', e) }
}

async function handleToggle(id) {
  const todo = todos.value.find(t => t.id === id)
  if (!todo) return
  const newCompleted = !todo.completed
  try {
    const res = await fetch(`${API}/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed: newCompleted })
    })
    const updated = await res.json()
    todo.completed = toBool(updated.completed)
  } catch (e) { console.error('切换失败', e) }
}

onMounted(fetchTodos)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
    'Helvetica Neue', Arial, sans-serif;
  background: #f0f2f5;
  color: #333;
  min-height: 100vh;
}

.app {
  max-width: 600px;
  margin: 0 auto;
  padding: 40px 20px;
}

.header {
  text-align: center;
  margin-bottom: 32px;
}

.header h1 {
  font-size: 32px;
  color: #1a73e8;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 14px;
  color: #888;
}

.main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.loading {
  text-align: center;
  padding: 60px 0;
  color: #999;
  font-size: 15px;
}
</style>
