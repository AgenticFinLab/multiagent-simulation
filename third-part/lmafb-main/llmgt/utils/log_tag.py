# ========================================
# 🏷️  Emoji Tag System - Full & Unified
# 一个面向日志、AI Agent、多系统协作的完整 emoji 标签库
# 支持：流程、通信、数据、金融、调试、错误、AI Agent、组织等
# ========================================

BLOCK_INDENT = "   - "


# 🔄 流程控制 | Flow Control
START_TAG = "🚀"  # Start operation
PROCESS_TAG = "🔄"  # In progress / processing
COMPLETE_TAG = "✅"  # Completed successfully
TERMINAL_TAG = "🏁"  # End of process
WAIT_TAG = "⏳"  # Waiting for response or resource


# 💭 思考与决策 | Thinking & Decision
THINK_TAG = "🤔"  # Thinking / reasoning
IDEA_TAG = "💡"  # Idea / suggestion / tip
DECISION_TAG = "📝"  # Decision recorded
TARGET_TAG = "🎯"  # Goal / target set


# 📢 通信与网络 | Communication & Networking
MESSAGE_TAG = "📨"  # General message
SEND_TAG = "📤"  # Send data/message
RECEIVE_TAG = "📥"  # Receive data/response
CALL_TAG = "📞"  # Remote procedure call
CONNECT_TAG = "🔗"  # Connection established
API_TAG = "🛰️"  # API request/response
NETWORK_TAG = "🌐"  # Network operation


# 📁 数据与存储 | Data & Storage
CONTENT_TAG = "📋"  # Content / payload / details
FILE_TAG = "📁"  # Configuration file
FOLDER_TAG = "📂"  # Directory / log folder
SAVE_TAG = "💾"  # Save result / persist
DATABASE_TAG = "🗃️"  # Database operation
CLOUD_TAG = "☁️"  # Cloud storage / sync
ATTACH_TAG = "📎"  # Attachment / linked file
TEXT_TAG = "📄"  # Text document / file


# 🔐 编码与安全 | Encoding & Security
LOCK_TAG = "🔒"  # Lock / encrypt / secure
UNLOCK_TAG = "🔓"  # Unlock / decrypt
ENCODE_TAG = "📦"  # Encode / pack data
DECODE_TAG = "📬"  # Decode / unpack data


# 📊 分析与搜索 | Analytics & Search
SEARCH_TAG = "🔍"  # Search / query
STATISTICS_TAG = "📊"  # Statistics / metrics
TRACE_TAG = "🧭"  # Trace / call path
TEST_TAG = "🧪"  # Unit test / experiment


# 💰 金融与市场 | Finance & Market
MONEY_TAG = "💰"  # Money / price / cost
PRICE_UP_TAG = "📈"  # Price increase
PRICE_DOWN_TAG = "📉"  # Price decrease
MARKET_TAG = "🏪"  # Market / exchange


# 👥 人员与角色 | People, Roles & Collaboration

## 👤 个人 | Individuals
USER_TAG = "👤"  # End user
PERSON_TAG = "🧍"  # Generic person (standing)
EXPERT_TAG = "👨‍💼"  # Domain expert / professional
DEVELOPER_TAG = "👩‍💻"  # Developer / engineer

## 👥 团队与群组 | Teams & Groups
TEAM_TAG = "🤝"  # Teamwork / collaboration
GROUP_TAG = "👥"  # Group of people
CHAT_GROUP_TAG = "💬"  # Chat group / discussion
FRIENDS_TAG = "👯"  # Informal peer group
PARTICIPANTS_TAG = "👥"

## 🤖 AI Agent 角色 | AI Agents & Roles
AGENT_TAG = "🤖"  # Generic AI agent
PLANNER_AGENT = "🧠"  # Planning / reasoning agent
EXECUTOR_AGENT = "🔧"  # Execution / task agent
CRITIC_AGENT = "📝"  # Critic / reviewer agent
RESEARCHER_AGENT = "🔬"  # Research / info-gathering agent
CODER_AGENT = "👨‍💻"  # Code-writing agent
MODERATOR_AGENT = "⚖️"  # Moderation / governance agent
AUTOMATION_AGENT = "⚙️"  # Automation / workflow agent


# 🏢 组织与机构 | Organizations & Institutions
ORG_TAG = "🏢"  # Organization / company
GOV_TAG = "🏛️"  # Government / regulatory body
BANK_TAG = "🏦"  # Financial institution
HOSPITAL_TAG = "🏥"  # Healthcare organization
SCHOOL_TAG = "🏫"  # Educational institution
DEPT_TAG = "🗂️"  # Department / division
BRANCH_TAG = "📍"  # Branch / regional office
HEADQUARTERS_TAG = "🚩"  # Headquarters / central office
PARTNERSHIP_TAG = "🤝💼"  # Business partnership
ALLIANCE_TAG = "🤝🚀"  # Strategic alliance
REMOTE_TEAM_TAG = "🌍"  # Remote / global team
TIMEZONE_TAG = "🕒"  # Cross-timezone collaboration


# ⚠️ 警告与错误 | Warnings & Errors (General)
WARNING_TAG = "⚠️"  # Warning message
ERROR_TAG = "❌"  # Generic error
ALERT_TAG = "🔔"  # Alert / urgent notification


# 🛠️ 构建与维护 | Build & Maintenance
BUILD_TAG = "🏗️"  # Build / create resource
CLEAN_TAG = "🧹"  # Cleanup / clear cache
DELETE_TAG = "🗑️"  # Delete item
UPDATE_TAG = "🔄"  # Update (shared with process)
RETRY_TAG = "🔁"  # Retry attempt
CONFIG_TAG = "⚙️"  # Configuration / settings
TOOL_TAG = "🧰"  # Tool / utility used


# 🪲 调试与日志 | Debug & Logging
DEBUG_TAG = "🪲"  # Debug mode / bug found
LOG_TAG = "🪵"  # Log output / logging
SCHEDULE_TAG = "📅"  # Scheduled task / cron
BLOCK_TAG = "🧱"  # Code block / module


# 🐞 Bug 与严重性 | Bug Types & Severity
BUG_TAG = "🪲"  # General bug
SPIDER_TAG = "🕷️"  # Hidden / hard-to-find bug
ZOMBIE_TAG = "🧟"  # Zombie process / memory leak
TICKING_BOMB_TAG = "💣"  # Latent critical bug (time bomb)
ROBOT_TAG = "🤖"  # AI/LLM logic error or hallucination (alternative use)

SEV1_TAG = "🔴"  # Severity 1: Critical
SEV2_TAG = "🟠"  # Severity 2: High
SEV3_TAG = "🟡"  # Severity 3: Medium
SEV4_TAG = "⚪"  # Severity 4: Low
INFO_TAG = "🟢"  # Informational (non-error)

IMPACT_CRITICAL = "💥"  # Full system impact
IMPACT_WIDE = "🌪️"  # Wide disruption
IMPACT_MEDIUM = "🔻"  # Medium impact
IMPACT_MINOR = "🔹"  # Minor / single user
BLOCKER_TAG = "🛑"  # Blocks release
DOWNTIME_TAG = "📉"  # Causes downtime
COSTLY_TAG = "💸"  # Financial risk
SECURITY_TAG = "🔐"  # Security vulnerability


# 🧫 异常与修复 | Errors & Fixes
PERMISSION_TAG = "🚫"  # Permission denied
CONNECTION_TAG = "🔌"  # Connection failed
PARSE_ERROR_TAG = "📦❌"  # Parsing error (JSON/XML)
TIMEOUT_TAG = "⏱️"  # Timeout occurred
FROZEN_TAG = "🧊"  # Frozen / deadlock
RATELIMIT_TAG = "📉"  # Rate-limited
STACK_OVERFLOW_TAG = "🧨"  # Stack overflow
CYCLE_TAG = "🔁"  # Infinite loop / cycle

FIXED_TAG = "🛠️"  # Bug fixed
PATCHED_TAG = "🧰"  # Temporary patch
HOTFIX_TAG = "🪲🔥"  # Emergency hotfix
RESOLVED_TAG = "🪲➡️✅"  # Bug resolved (visual flow)