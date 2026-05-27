<template>
  <div class="todo-list-card">
    <div class="list-header">
      <h3>
        任务列表
        <span class="count-badge">{{ todos.length }}</span>
      </h3>
      <span class="progress-text">
        {{ completedCount }}/{{ todos.length }} 已完成
      </span>
    </div>

    <div v-if="todos.length === 0" class="empty">
      <span class="empty-icon">📭</span>
      <p>暂无任务，快来添加吧</p>
    </div>

    <TransitionGroup name="list" tag="ul" class="todo-list">
      <li v-for="todo in todos" :key="todo.id" class="todo-item">
        <label class="todo-label" :class="{ completed: todo.completed }">
          <input
            type="checkbox"
            :checked="todo.completed"
            class="checkbox"
            @change="$emit('toggle', todo.id)"
          />
          <span class="checkmark"></span>
          <span class="todo-title">{{ todo.title }}</span>
        </label>
        <div class="todo-actions">
          <button class="icon-btn edit-btn" @click="$emit('edit', todo)" title="编辑">
            ✏️
          </button>
          <button class="icon-btn delete-btn" @click="$emit('delete', todo.id)" title="删除">
            🗑️
          </button>
        </div>
      </li>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  todos: { type: Array, required: true }
})

defineEmits(['edit', 'delete', 'toggle'])

const completedCount = computed(() => props.todos.filter(t => t.completed).length)
</script>

<style scoped>
.todo-list-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.list-header h3 {
  font-size: 16px;
  color: #444;
}

.count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #e8f0fe;
  color: #1a73e8;
  font-size: 12px;
  font-weight: 600;
  min-width: 22px;
  height: 22px;
  border-radius: 11px;
  padding: 0 6px;
  margin-left: 6px;
}

.progress-text {
  font-size: 13px;
  color: #999;
}

.empty {
  text-align: center;
  padding: 40px 0;
  color: #bbb;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.empty p {
  font-size: 14px;
}

.todo-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-radius: 8px;
  background: #fafafa;
  transition: background 0.2s;
}

.todo-item:hover {
  background: #f0f5ff;
}

.todo-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  flex: 1;
  min-width: 0;
}

.todo-label.completed .todo-title {
  text-decoration: line-through;
  color: #bbb;
}

.checkbox {
  display: none;
}

.checkmark {
  width: 20px;
  height: 20px;
  border: 2px solid #ccc;
  border-radius: 4px;
  display: inline-block;
  position: relative;
  flex-shrink: 0;
  transition: all 0.2s;
}

.todo-label.completed .checkmark {
  background: #1a73e8;
  border-color: #1a73e8;
}

.todo-label.completed .checkmark::after {
  content: '';
  position: absolute;
  left: 5px;
  top: 1px;
  width: 6px;
  height: 11px;
  border: solid #fff;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.todo-title {
  font-size: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.todo-actions {
  display: flex;
  gap: 4px;
  flex-shrink: 0;
}

.icon-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: background 0.2s;
  line-height: 1;
}

.edit-btn:hover {
  background: #e8f0fe;
}

.delete-btn:hover {
  background: #fce8e6;
}

.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}

.list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>
