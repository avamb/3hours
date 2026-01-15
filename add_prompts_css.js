const fs = require('fs');
const path = 'C:/Projects/3hours/admin/static/styles.css';
let content = fs.readFileSync(path, 'utf8');

const newCss = `
/* Prompts Page */
.prompts-container {
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 20px;
    height: calc(100vh - 180px);
    min-height: 500px;
}

.prompts-list {
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.prompts-list h3 {
    padding: 16px 20px;
    margin: 0;
    font-size: 16px;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-color);
}

.prompts-list-items {
    flex: 1;
    overflow-y: auto;
}

.prompt-item {
    padding: 14px 20px;
    border-bottom: 1px solid var(--border-color);
    cursor: pointer;
    transition: background-color 0.2s;
}

.prompt-item:hover {
    background-color: var(--bg-color);
}

.prompt-item.active {
    background-color: rgba(79, 70, 229, 0.1);
    border-left: 3px solid var(--primary-color);
}

.prompt-item-key {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 4px;
    color: var(--text-color);
}

.prompt-item-status {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: var(--text-muted);
}

.prompt-version-badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 500;
    background: rgba(79, 70, 229, 0.1);
    color: var(--primary-color);
}

.prompts-editor {
    background: var(--card-bg);
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.prompts-editor-header {
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-color);
    background: var(--bg-color);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.prompts-editor-header h3 {
    margin: 0;
    font-size: 16px;
}

.prompts-editor-actions {
    display: flex;
    gap: 8px;
}

.prompts-editor-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 20px;
    overflow-y: auto;
}

.prompt-textarea {
    width: 100%;
    min-height: 300px;
    padding: 16px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 13px;
    line-height: 1.6;
    resize: vertical;
    background: var(--bg-color);
    color: var(--text-color);
}

.prompt-textarea:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
}

.prompt-notes-input {
    width: 100%;
    padding: 10px 14px;
    margin-top: 12px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-size: 14px;
}

.prompt-notes-input:focus {
    outline: none;
    border-color: var(--primary-color);
}

.prompt-empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    color: var(--text-muted);
    text-align: center;
    padding: 40px;
}

.prompt-empty-state p {
    font-size: 16px;
    margin-bottom: 8px;
}

.prompt-empty-state small {
    font-size: 13px;
    opacity: 0.8;
}

/* Version History */
.version-history {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid var(--border-color);
}

.version-history h4 {
    margin: 0 0 12px 0;
    font-size: 14px;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.version-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-height: 200px;
    overflow-y: auto;
}

.version-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: var(--bg-color);
    border-radius: 8px;
    border: 1px solid var(--border-color);
}

.version-item.active {
    border-color: var(--success-color);
    background: rgba(16, 185, 129, 0.05);
}

.version-header {
    display: flex;
    align-items: center;
    gap: 10px;
}

.version-number {
    font-weight: 600;
    font-size: 14px;
    color: var(--text-color);
}

.version-active-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    background: rgba(16, 185, 129, 0.1);
    color: var(--success-color);
}

.version-meta {
    font-size: 12px;
    color: var(--text-muted);
}

.version-actions {
    display: flex;
    gap: 6px;
}

`;

// Insert before /* Responsive */
content = content.replace('/* Responsive */', newCss + '/* Responsive */');
fs.writeFileSync(path, content);
console.log('CSS added successfully');
