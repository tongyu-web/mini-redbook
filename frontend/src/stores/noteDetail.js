import { defineStore } from "pinia"
import { ref } from "vue"

export const useNoteDetailStore = defineStore("noteDetail", () => {
  const isOpen = ref(false)
  const currentNoteId = ref(null)

  function open(noteId) {
    currentNoteId.value = noteId
    isOpen.value = true
    document.body.style.overflow = "hidden"
  }

  function close() {
    isOpen.value = false
    currentNoteId.value = null
    document.body.style.overflow = ""
  }

  return { isOpen, currentNoteId, open, close }
})
