import { ref } from "vue"

export const loginDialogVisible = ref(false)

export function openLoginDialog() {
  loginDialogVisible.value = true
}

export function closeLoginDialog() {
  loginDialogVisible.value = false
}
