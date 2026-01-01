import streamlit as st
from openai import OpenAI
import datetime

# --- 1. 页面配置 ---
st.set_page_config(page_title="Ultech 实战考核系统", page_icon="🎓", layout="wide")

# --- 2. 样式优化 ---
st.markdown("""
<style>
    .user-msg { background-color: #dcf8c6; padding: 10px; border-radius: 10px; margin-bottom: 10px; text-align: right; color: black; }
    .bot-msg { background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin-bottom: 10px; text-align: left; color: black; }
    .score-box { border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #e8f5e9; margin-top: 20px; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. 角色库 (保持原有的丰富性) ---
PERSONAS = {
    "🟢 The Aussie Tradie (Dazza)": """
        [Role] You are 'Dazza', a construction worker. [Personality] Friendly, heavy slang ("G'day", "Reckon").
        [Trigger] Hands dirty. Want tough case. Test if they clean phone before trying case.
    """,
    "🟢 The Confused Grandma (Margaret)": """
        [Role] 'Margaret', 75yo. [Context] Forgot passcode. [Trigger] Scared of data loss. Test data privacy explanation.
    """,
    "🟢 The Backpacker (Sven)": """
        [Role] 'Sven', German. [Context] Dropped in toilet. [Trigger] Asks about rice myth. Demands 100% guarantee.
    """,
    "🟡 The Influencer (Bella)": """
        [Role] 'Bella', Gen Z. [Context] Wants cute case. [Trigger] Upsell opportunity (Lens protector). Impatient.
    """,
    "🟡 The Paranoid Professional (Mr. Smith)": """
        [Role] Lawyer. [Context] Sensitive data. [Trigger] Refuse PIN unless privacy script used correctly.
    """,
    "🟡 The Rush Hour Customer (Jimmy)": """
        [Role] Delivery driver. [Context] In a rush. [Trigger] Test expectation management (Time quote).
    """,
    "🟡 The Discount Hunter (Charlie)": """
        [Role] Bargain hunter. [Trigger] Compares price with Gumtree. Test Membership/Quality value prop.
    """,
    "🔴 The 'Warranty Loophole' Boss (Bruce)": """
        [Role] Angry Bruce. [Context] Screen broke again. [Trigger] Blames quality. Test empathy & non-confrontation.
    """,
    "🔴 The 'It Should Be Waterproof' Guy (Tom)": """
        [Role] Shocked Tom. [Context] Water damage after repair. [Trigger] Test waterproof vs water resistant explanation.
    """,
    "🔴 The 'I Know Your Boss' (Karen)": """
        [Role] Entitled Karen. [Trigger] Demands freebie. Test adherence to process vs pressure.
    """
}

# --- 4. 初始化 ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "report" not in st.session_state:
    st.session_state.report = None

# --- 5. 侧边栏：控制台 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.title("Ultech 考核系统")
    st.caption("实战演练 -> 智能评分 -> 导出报告")
    
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.markdown("### 1. 选择考题")
    difficulty = st.selectbox("难度筛选:", ["全部", "🟢 简单", "🟡 进阶", "🔴 困难"])
    
    # 筛选逻辑
    if difficulty == "🟢 简单":
        options = [k for k in PERSONAS.keys() if "🟢" in k]
    elif difficulty == "🟡 进阶":
        options = [k for k in PERSONAS.keys() if "🟡" in k]
    elif difficulty == "🔴 困难":
        options = [k for k in PERSONAS.keys() if "🔴" in k]
    else:
        options = list(PERSONAS.keys())
        
    scenario = st.selectbox("当前角色:", options)
    
    st.markdown("---")
    st.markdown("### 2. 结束与重置")
    
    # 结束考核按钮
    if st.button("🏁 结束对话并评分 (Finish & Grade)"):
        if not api_key:
            st.error("请先输入 API Key")
        elif len(st.session_state.messages) < 3:
            st.warning("对话太短，无法评分。请多聊几句。")
        else:
            with st.spinner("AI 考官正在分析你的表现..."):
                client = OpenAI(api_key=api_key)
                # 提取纯对话文本
                conversation_text = ""
                for m in st.session_state.messages:
                    if m["role"] != "system":
                        conversation_text += f"{m['role'].upper()}: {m['content']}\n"
                
                # 考官 Prompt
                eval_prompt = f"""
                你是一位资深的门店培训主管。请根据以下对话记录，对员工的表现进行严厉但客观的考核。
                
                【当前场景角色】: {scenario}
                【SOP 考核点】:
                1. 销售场景: 是否确认型号？是否做 Upsell？态度是否自然（非强推）？
                2. 维修场景: 是否提示风险（数据/FaceID/进水）？是否打破期望（Timeline/Price）？
                3. 客诉场景: 是否先共情？是否避免直接反驳？是否遵循 Escalation 流程？
                
                【输出要求】:
                请生成一份中文报告，包含：
                1. **最终得分** (0-100分)
                2. **亮点 (Highlights)**
                3. **不足 (Weaknesses)** - 指出具体哪句话说错了或遗漏了什么 SOP。
                4. **改进建议 (Action Plan)**
                
                【对话记录】:
                {conversation_text}
                """
                
                try:
                    res = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role": "system", "content": eval_prompt}],
                        temperature=0.7
                    )
                    st.session_state.report = res.choices[0].message.content
                except Exception as e:
                    st.error(f"评分失败: {e}")

    # 重置按钮
    if st.button("🔄 开启新一轮 (Reset)"):
        st.session_state.messages = []
        st.session_state.report = None
        st.rerun()

# --- 6. 主界面 ---
st.title("🎓 Ultech 实战考核")
st.subheader(f"正在对战: {scenario}")

if not api_key:
    st.info("👈 请在左侧侧边栏输入 API Key 以开始。")
    st.stop()

client = OpenAI(api_key=api_key)

# 自动开场
if not st.session_state.messages:
    st.session_state.messages.append({"role": "system", "content": PERSONAS[scenario]})
    try:
        first_msg = client.chat.completions.create(
            model="gpt-4o",
            messages=st.session_state.messages
        )
        st.session_state.messages.append({"role": "assistant", "content": first_msg.choices[0].message.content})
    except:
        pass

# 显示对话区（两栏布局：左边对话，右边如果生成了报告则显示报告）
col1, col2 = st.columns([2, 1])

with col1:
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"<div class='user-msg'>👤 <b>You:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
            elif msg["role"] == "assistant":
                st.markdown(f"<div class='bot-msg'>🦘 <b>{scenario.split('(')[0]}:</b><br>{msg['content']}</div>", unsafe_allow_html=True)

    # 输入框
    if user_input := st.chat_input("请输入英文回复..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

# AI 回复逻辑 (在重运行后触发)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with col1:
        with st.spinner("对方正在输入..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=st.session_state.messages,
                    temperature=0.7
                )
                ai_reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.rerun()
            except Exception as e:
                st.error(f"连接错误: {e}")

# --- 7. 评分报告区 (右侧) ---
with col2:
    if st.session_state.report:
        st.markdown("### 📝 考核成绩单")
        st.markdown(f"<div class='score-box'>{st.session_state.report}</div>", unsafe_allow_html=True)
        
        # 生成可下载的文本内容
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        log_content = f"Ultech Training Report\nTime: {timestamp}\nScenario: {scenario}\n\n"
        log_content += "="*20 + "\nFULL CHAT LOG\n" + "="*20 + "\n\n"
        
        for m in st.session_state.messages:
            if m["role"] != "system":
                role = "Staff" if m["role"] == "user" else "Customer"
                log_content += f"[{role}]: {m['content']}\n"
        
        log_content += "\n\n" + "="*20 + "\nEVALUATION\n" + "="*20 + "\n\n"
        log_content += st.session_state.report
        
        # 下载按钮
        st.download_button(
            label="📥 下载完整报告 (发给主管)",
            data=log_content,
            file_name=f"Training_Report_{timestamp.replace(':', '-')}.txt",
            mime="text/plain"
        )
    else:
        st.info("💡 提示：\n完成对话后，点击左侧侧边栏的 **“🏁 结束对话并评分”** 按钮，即可查看分数和下载报告。")
