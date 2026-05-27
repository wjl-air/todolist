<template>
  <div class="todo-form-card">
    <h3>{{ isEditing ? '编辑任务' : '新增任务' }}</h3>
    <form @submit.prevent="handleSubmit" class="form">
      <input
        v-model="title"
        type="text"
        placeholder="请输入任务名称..."
        class="input"
        maxlength="100"
      />
      <div class="form-actions">
        <button type="submit" class="btn btn-primary" :disabled="!title.trim()">
          {{ isEditing ? '保存修改' : '添加任务' }}
        </button>
        <button
          v-if="isEditing"
          type="button"
          class="btn btn-cancel"
          @click="$emit('cancel')"
        >
          取消
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  editingTodo: { type: Object, default: null }
})

const emit = defineEmits(['add', 'update', 'cancel'])

const title = ref('')
const isEditing = ref(false)

watch(
  () => props.editingTodo,
  (val) => {
    if (val) {
      title.value = val.title
      isEditing.value = true
    } else {
      title.value = ''
      isEditing.value = false
    }
  },
  { immediate: true }
)

function handleSubmit() {
  const trimmed = title.value.trim()
  if (!trimmed) return

  if (isEditing.value) {
    emit('update', { ...props.editingTodo, title: trimmed })
  } else {
    emit('add', trimmed)
  }
  title.value = ''
}
</script>

<style scoped>
.todo-form-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.todo-form-card h3 {
  font-size: 16px;
  margin-bottom: 16px;
  color: #444;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.input:focus {
  border-color: #1a73e8;
}

.form-actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 24px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
}

.btn:active {
  transform: scale(0.97);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: #1a73e8;
  color: #fff;
}

.btn-primary:hover:not(:disabled) {
  background: #1557b0;
}

.btn-cancel {
  background: #f0f0f0;
  color: #666;
}

.btn-cancel:hover {
  background: #e0e0e0;
}
</style>
