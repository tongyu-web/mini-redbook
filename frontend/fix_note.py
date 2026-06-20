import re
with open('src/views/NoteDetail.vue', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace(
    'type="primary" :loading="commenting" @click="submitComment" :disabled="!commentContent.trim() && !commentFile"',
    'class="send-btn-red" :loading="commenting" @click="submitComment" :disabled="!commentContent.trim() && !commentFile"'
)

old_css = '.compose-body :deep(.el-textarea__inner) {\n  font-size: 14px;\n  border-radius: 8px;\n  min-height: 80px !important;\n}'
new_css = old_css + '\n.compose-body :deep(.el-textarea__inner:focus) {\n  border-color: #ff2442 !important;\n  box-shadow: 0 0 0 1px #ff2442 inset !important;\n}'
content = content.replace(old_css, new_css)

old_btn = '.follow-btn-red { background: #ff2442 !important; border-color: #ff2442 !important; }\n.follow-btn-red:hover { background: #d61e38 !important; border-color: #d61e38 !important; }'
new_btn = old_btn + '\n.send-btn-red { background: #ff2442 !important; border-color: #ff2442 !important; }\n.send-btn-red:hover { background: #d61e38 !important; border-color: #d61e38 !important; }'
content = content.replace(old_btn, new_btn)

with open('src/views/NoteDetail.vue', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')
