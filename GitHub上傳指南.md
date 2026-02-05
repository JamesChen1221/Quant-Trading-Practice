# GitHub 上傳指南

## ✅ 準備工作已完成

你的專案已經準備好上傳到 GitHub！

- ✅ Git 倉庫已初始化
- ✅ Excel 資料檔案已從追蹤中移除
- ✅ .gitignore 已正確設定
- ✅ 所有程式碼和文件已提交
- ✅ 提交歷史清晰完整

---

## 🚀 上傳到 GitHub 的步驟

### 步驟 1：在 GitHub 建立新倉庫

1. 登入 [GitHub](https://github.com)
2. 點擊右上角的 `+` → `New repository`
3. 填寫倉庫資訊：
   - **Repository name**: `quant-trading-rsi-adx`（或你喜歡的名稱）
   - **Description**: `美股當沖量化交易 RSI/ADX 指標計算系統`
   - **Public/Private**: 選擇 Public（公開）或 Private（私人）
   - **不要勾選** "Initialize this repository with a README"
4. 點擊 `Create repository`

### 步驟 2：連接本地倉庫到 GitHub

複製 GitHub 提供的倉庫 URL，然後執行：

```bash
# 新增遠端倉庫（替換 URL 為你的倉庫位址）
git remote add origin https://github.com/你的使用者名稱/quant-trading-rsi-adx.git

# 確認遠端倉庫已新增
git remote -v
```

### 步驟 3：推送到 GitHub

```bash
# 推送主分支
git push -u origin master

# 如果遇到錯誤，可能需要先拉取
git pull origin master --allow-unrelated-histories
git push -u origin master
```

### 步驟 4：驗證上傳

1. 重新整理 GitHub 頁面
2. 確認所有檔案都已上傳
3. **確認 `量化交易.xlsx` 不在列表中** ✓

---

## 🔒 安全檢查清單

上傳前請確認：

- ✅ `量化交易.xlsx` 不在 Git 追蹤中
- ✅ `.gitignore` 包含 `*.xlsx`
- ✅ 沒有其他敏感資訊（API 金鑰、密碼等）
- ✅ 提交歷史中沒有敏感資料

### 驗證指令

```bash
# 確認 Excel 檔案不被追蹤
git ls-files | findstr xlsx
# 應該沒有任何輸出

# 查看 .gitignore 內容
type .gitignore | findstr xlsx
# 應該看到 *.xlsx

# 查看即將推送的檔案
git ls-files
```

---

## 📝 完整指令範例

```bash
# 1. 新增遠端倉庫
git remote add origin https://github.com/JamesChen/quant-trading-rsi-adx.git

# 2. 確認遠端倉庫
git remote -v

# 3. 推送到 GitHub
git push -u origin master

# 4. 推送標籤（如果有）
git tag v1.0.0
git push --tags
```

---

## 🌿 使用 SSH 連接（推薦）

如果你有設定 SSH 金鑰，可以使用 SSH URL：

```bash
# 使用 SSH URL
git remote add origin git@github.com:JamesChen/quant-trading-rsi-adx.git

# 推送
git push -u origin master
```

### 設定 SSH 金鑰

如果還沒設定 SSH：

1. 生成 SSH 金鑰：
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. 複製公鑰：
   ```bash
   type ~/.ssh/id_ed25519.pub
   ```

3. 在 GitHub 新增 SSH 金鑰：
   - Settings → SSH and GPG keys → New SSH key
   - 貼上公鑰內容

---

## 🔄 日常更新流程

### 本地修改後推送到 GitHub

```bash
# 1. 查看變更
git status
git diff

# 2. 加入變更
git add .

# 3. 提交
git commit -m "修正: 改善 RSI 計算精度"

# 4. 推送到 GitHub
git push origin master
```

### 從 GitHub 拉取更新

```bash
# 拉取最新變更
git pull origin master
```

---

## 📋 .gitignore 內容確認

確保你的 `.gitignore` 包含：

```gitignore
# Python
__pycache__/
*.py[cod]
*.so
venv/
env/

# Excel 臨時檔案
~$*.xlsx
~$*.xls

# 資料檔案（避免上傳敏感資料到 GitHub）
量化交易.xlsx
交易資料*.xlsx
*.xlsx

# 但保留範例檔案（如果有的話）
!範例*.xlsx
!example*.xlsx

# IDE
.vscode/
.idea/
*.swp

# 其他
*.log
*.tmp
.DS_Store
```

---

## 🎯 GitHub 倉庫設定建議

### 1. 新增 README 徽章

在 README.md 頂部加入：

```markdown
# 美股當沖量化交易 - RSI & ADX 指標計算系統

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)
```

### 2. 設定 Topics

在 GitHub 倉庫頁面：
- 點擊 "Add topics"
- 新增：`python`, `trading`, `quantitative-analysis`, `rsi`, `adx`, `technical-indicators`

### 3. 新增 LICENSE

建議新增 MIT License：

```bash
# 在 GitHub 網頁上：
# Add file → Create new file
# 檔名：LICENSE
# 選擇 MIT License 範本
```

### 4. 設定 .github/workflows（可選）

如果想要 CI/CD，可以新增 GitHub Actions。

---

## 🆘 常見問題

### Q: 推送時要求輸入帳號密碼？

A: GitHub 已不支援密碼驗證，請使用：
- **Personal Access Token**（推薦）
- **SSH 金鑰**

建立 Personal Access Token：
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token
3. 選擇 `repo` 權限
4. 複製 token（只會顯示一次）
5. 推送時使用 token 作為密碼

### Q: 推送失敗：rejected (non-fast-forward)

A: 遠端有你本地沒有的提交：

```bash
# 先拉取遠端變更
git pull origin master --rebase

# 再推送
git push origin master
```

### Q: 不小心推送了敏感資料怎麼辦？

A: 需要從歷史中移除：

```bash
# 使用 git filter-branch（複雜）
# 或使用 BFG Repo-Cleaner（推薦）

# 最簡單的方法：刪除倉庫重新建立
```

### Q: 如何更改遠端 URL？

```bash
# 查看目前的遠端 URL
git remote -v

# 更改 URL
git remote set-url origin 新的URL

# 驗證
git remote -v
```

---

## 📚 GitHub 功能建議

### 1. Issues（問題追蹤）

用於追蹤 bug 和功能請求：
- 在 GitHub 倉庫頁面點擊 "Issues"
- 建立 issue 範本

### 2. Projects（專案管理）

用於管理開發進度：
- 建立看板
- 追蹤任務狀態

### 3. Wiki（文件）

用於詳細文件：
- 使用指南
- API 文件
- 常見問題

### 4. Releases（版本發布）

發布穩定版本：

```bash
# 建立標籤
git tag -a v1.0.0 -m "版本 1.0.0: 初始發布"

# 推送標籤
git push --tags
```

然後在 GitHub 上建立 Release。

---

## 🎉 完成後的檢查

上傳完成後，確認：

1. ✅ 所有程式碼檔案都已上傳
2. ✅ 所有文件檔案都已上傳
3. ✅ `量化交易.xlsx` **不在** GitHub 上
4. ✅ README.md 正確顯示
5. ✅ .gitignore 正常運作
6. ✅ 提交歷史清晰

---

## 🔗 有用的連結

- [GitHub 官方文件](https://docs.github.com/)
- [Git 官方文件](https://git-scm.com/doc)
- [GitHub Desktop](https://desktop.github.com/)（圖形化介面）
- [GitHub CLI](https://cli.github.com/)（命令列工具）

---

## 💡 最佳實踐

1. **定期推送**
   - 每天結束工作時推送
   - 重要功能完成後推送

2. **清晰的提交訊息**
   - 使用有意義的提交訊息
   - 遵循提交訊息規範

3. **保護主分支**
   - 在 GitHub 設定分支保護規則
   - 要求 Pull Request 審查

4. **定期備份**
   - GitHub 是備份，但不是唯一備份
   - 定期備份重要資料到其他位置

5. **文件更新**
   - 保持 README 更新
   - 記錄重要變更

---

## 🚀 準備好了嗎？

執行以下指令開始上傳：

```bash
# 1. 新增遠端倉庫（替換為你的 URL）
git remote add origin https://github.com/你的使用者名稱/倉庫名稱.git

# 2. 推送到 GitHub
git push -u origin master

# 3. 推送標籤（可選）
git push --tags
```

**祝你上傳順利！** 🎉

如有問題，請參考 [Git使用指南.md](Git使用指南.md) 或 GitHub 官方文件。
