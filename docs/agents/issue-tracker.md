# 问题跟踪器：GitHub

本仓库的问题和 PRD 存放在 GitHub Issues 中。所有操作均使用 `gh` CLI。

## 操作约定

- **创建 Issue**：`gh issue create --title "..." --body "..."`。多行正文使用 heredoc。
- **读取 Issue**：`gh issue view <编号> --comments`，同时获取标签，并在需要时使用 `jq` 过滤评论。
- **列出 Issue**：使用 `gh issue list --state open --json number,title,body,labels,comments`，并根据任务添加适当的 `--label` 和 `--state` 过滤条件。
- **评论 Issue**：`gh issue comment <编号> --body "..."`
- **添加或移除标签**：`gh issue edit <编号> --add-label "..."` 或 `--remove-label "..."`
- **关闭 Issue**：`gh issue close <编号> --comment "..."`

仓库信息从 `git remote -v` 推断。在仓库克隆目录内运行时，`gh` 会自动识别当前仓库。

## 是否将 Pull Request 作为分流入口

**不将 PR 作为请求入口。**

如需让外部 PR 与 Issue 使用相同的分流标签及状态，可将此配置改为“是”；`triage` 技能将读取该配置。

启用后使用对应的 `gh pr` 命令：

- **读取 PR**：`gh pr view <编号> --comments`，并通过 `gh pr diff <编号>` 获取差异。
- **列出待分流的外部 PR**：使用 `gh pr list` 获取作者关系，只保留 `CONTRIBUTOR`、`FIRST_TIME_CONTRIBUTOR` 或 `NONE`。
- **评论、添加标签或关闭**：使用 `gh pr comment`、`gh pr edit` 和 `gh pr close`。

GitHub 的 Issue 与 PR 共用编号空间，因此 `#42` 可能是 Issue，也可能是 PR。先执行 `gh pr view 42`；如果失败，再执行 `gh issue view 42`。

## 当技能要求“发布到问题跟踪器”时

创建一个 GitHub Issue。

## 当技能要求“获取相关工单”时

执行：

`gh issue view <编号> --comments`

## Wayfinder 操作约定

`wayfinder` 使用一个主 Issue 作为地图，并使用子 Issue 表示具体工单。

- **地图**：带有 `wayfinder:map` 标签的单个 Issue，用于记录笔记、已有决策和未知事项。
- **子工单**：作为地图 Issue 的 GitHub 子 Issue。标签格式为 `wayfinder:<类型>`，其中类型包括 `research`、`prototype`、`grilling` 和 `task`。
- **兼容方式**：如果仓库未启用子 Issue，则在地图正文中使用任务列表，并在子工单正文顶部添加 `Part of #<地图编号>`。
- **阻塞关系**：优先使用 GitHub 原生 Issue 依赖关系。如果不可用，则在工单正文顶部添加 `Blocked by: #<编号>`。
- **查找可执行工单**：列出地图下所有未关闭的子工单，排除仍有未关闭阻塞项或已有负责人者，然后按地图中的顺序选择第一个。
- **认领工单**：`gh issue edit <编号> --add-assignee @me`
- **完成工单**：添加结果评论、关闭 Issue，并在地图的已有决策中追加上下文链接。
