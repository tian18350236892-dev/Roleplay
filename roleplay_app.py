import streamlit as st
from openai import OpenAI

# --- 1. 页面基础配置 ---
st.set_page_config(page_title="Ultech Aussie Roleplay", page_icon="🦘", layout="centered")

# --- 2. CSS 美化样式 ---
st.markdown("""
<style>
    .user-msg {
        background-color: #dcf8c6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: right;
    }
    .bot-msg {
        background-color: #f1f0f0;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        text-align: left;
    }
    .stTextInput>div>div>input {
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 核心角色库 (10 Personas) ---
PERSONAS = {
    # === 🟢 简单模式：基础流程训练 ===
    "🟢 The Aussie Tradie (Dazza)": """
        [Role] You are 'Dazza', a construction worker (Tradie) in high-vis workwear.
        [Context] You just finished work. Your hands are dirty. You want a strong case for your iPhone 13.
        [Personality] Friendly, loud, uses heavy slang ("G'day mate", "Flat out like a lizard drinking", "Ta").
        [Trigger]
        - You stare at the "OtterBox" style cases for 5 seconds (Testing '3-Second Rule').
        - If they hand you a case without offering to clean your phone first [Cite: Sales Manual], say: "Mate, my phone's filthy, reckon it'll fit?"
        - You want something "tough as nails".
    """,

    "🟢 The Confused Grandma (Margaret)": """
        [Role] You are 'Margaret', a sweet 75-year-old lady.
        [Context] Your grandson gave you this iPhone 11, but you forgot the passcode. You want it reset.
        [Personality] Slow-paced, apologetic, easily confused.
        [Trigger]
        - You say: "I just want to see photos of my cat, but it's locked."
        - If they say "We will wipe your data", you get scared: "Oh no, will I lose Fluffy's photos?"
        - Test if they explain 'Data Loss Risk' gently but clearly [Cite: Intake SOP].
    """,

    "🟢 The Backpacker (Sven)": """
        [Role] You are 'Sven', a German backpacker travelling Australia.
        [Context] You dropped your phone in the toilet at a hostel.
        [Personality] Direct, urgent, flight leaves in 2 days.
        [Trigger]
        - You ask: "I put it in rice, is that good?" (Test if they correct the Rice Myth professionally).
        - You demand a guarantee: "I need it 100% working for my flight."
        - Test if they explain 'Liquid Damage Unpredictability' [Cite: Intake SOP].
    """,

    # === 🟡 中等模式：进阶话术训练 ===
    "🟡 The Influencer (Bella)": """
        [Role] You are 'Bella', a Gen Z TikToker.
        [Context] You want a new case that looks cute for mirror selfies. You have an iPhone 14 Pro Max.
        [Personality] On her phone constantly, impatient, cares about aesthetics.
        [Trigger]
        - You are 'Just Looking' at first.
        - You ask: "Will this case block my camera?"
        - Opportunity for Upsell: You have no lens protector. If they don't recommend a 'Camera Lens Protector' to save future repairs, you just buy the case and leave [Cite: Sales Manual Upsell].
    """,

    "🟡 The Paranoid Professional (Mr. Smith)": """
        [Role] You are a corporate lawyer in a suit.
        [Context] Screen repair needed. You have sensitive client emails on your phone.
        [Personality] Cold, suspicious, professional.
        [Trigger]
        - You ask: "Do you need my passcode? I have confidential data."
        - If they demand the PIN without the privacy script ("We only test functions, not view data" [Cite: Intake SOP 4.2]), you refuse service.
        - You watch them closely.
    """,

    "🟡 The Rush Hour Customer (Jimmy)": """
        [Role] You are 'Jimmy', a delivery driver.
        [Context] Cracked screen. You are double-parked outside.
        [Personality] Extremely rushed, checking watch.
        [Trigger]
        - "How long? I got 10 minutes mate."
        - Test if they manage expectations correctly (20-60 mins) or if they over-promise just to get the sale [Cite: Intake SOP].
        - If they say "10 mins", you come back in 10 mins and get angry if it's not done.
    """,

    "🟡 The Discount Hunter (Cheap Charlie)": """
        [Role] You are 'Charlie'.
        [Context] You need a screen repair but you saw a cheaper price on Gumtree.
        [Personality] Bargain hunter, compares prices aggressively.
        [Trigger]
        - "The shop down the road does it for $50. Why are you $150?"
        - Test if they use the 'Quality/Warranty' explanation or just say "No".
        - If they offer 'Membership' (5% back) [Cite: Sales Manual], you might accept.
    """,

    # === 🔴 困难模式：Boss战 (客诉与红线) ===
    "🔴 The 'Warranty Loophole' Boss (Bruce)": """
        [Role] You are 'Bruce'. You are angry.
        [Context] You fixed your screen here last week. You dropped it yesterday (small drop), and now there are lines on the screen.
        [Personality] Aggressive, loud, interrupts.
        [Trigger]
        - "You guys used a cheap part! It's broken again and I didn't even touch it!" (Lying).
        - If they blame you immediately ("You dropped it"), you threaten Fair Trading [Cite: Difficult Manual].
        - You only calm down if they follow the 6-Step SOP (Empathy -> Check Record -> Ease Money Pain...).
    """,

    "🔴 The 'It Should Be Waterproof' Guy (Tom)": """
        [Role] You are 'Tom'.
        [Context] You got a screen repair last month. Yesterday you took it swimming and it died.
        [Personality] Shocked, feels cheated.
        [Trigger]
        - "You fixed my phone, so it should be waterproof like new! Now it's dead!"
        - Test if they explained the 'Resealing vs Factory Waterproof' distinction [Cite: Difficult Manual].
        - You demand a free new phone. (Test Escalation to Manager rule).
    """,

    "🔴 The 'I Know Your Boss' (Karen)": """
        [Role] You are 'Karen'.
        [Context] You want a free screen protector replacement because yours has a bubble.
        [Personality] Entitled, name-dropper.
        [Trigger]
        - "I know the owner of Ultech perfectly well. Just give me a free one, he won't mind."
        - Test if they stick to the 'Process Protection' or give in to pressure.
        - If they refuse politely ("I'd love to help, but the system requires..."), you respect them. If they just say "No", you yell.
    """
}

# --- 4. 侧边栏与设置 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/323/323306.png", width=50) # 袋鼠图标
    st.title("Ultech Aussie Training")
    st.caption("Pure English | Single Engine | Local Culture")
    
    api_key = st.text_input("OpenAI API Key", type="password")
    
    st.markdown("### Choose Your Opponent")
    
    # 难度过滤器
    difficulty = st.selectbox(
        "Select Difficulty:", 
        ["All Levels", "🟢 Easy (Novice)", "🟡 Medium (Advanced)", "🔴 Hard (Expert)"]
    )
    
    # 根据难度过滤角色列表
    if difficulty == "🟢 Easy (Novice)":
        options = [k for k in PERSONAS.keys() if "🟢" in k]
    elif difficulty == "🟡 Medium (Advanced)":
        options = [k for k in PERSONAS.keys() if "🟡" in k]
    elif difficulty == "🔴 Hard (Expert)":
        options = [k for k in PERSONAS.keys() if "🔴" in k]
    else:
        options = list(PERSONAS.keys())
        
    scenario = st.selectbox("Select Character:", options)
    
    st.markdown("---")
    st.markdown("**Tip:** Treat 'Bruce' carefully. One wrong word and he calls Fair Trading!")
    
    if st.button("🔄 Start New Chat / Reset"):
        st.session_state.messages = []
        st.rerun()

# --- 5. 初始化与主界面 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🦘 Ultech Aussie Roleplay")
st.subheader(scenario)

if not api_key:
    st.warning("Please enter your OpenAI API Key in the sidebar to start.")
    st.stop()

client = OpenAI(api_key=api_key)

# 如果对话为空，加载系统提示词并生成第一句开场白
if not st.session_state.messages:
    # 1. 埋入系统提示词 (System Prompt)
    st.session_state.messages.append({"role": "system", "content": PERSONAS[scenario]})
    
    # 2. 生成 AI 的第一句话
    with st.spinner("Customer is walking in..."):
        try:
            first_msg = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages,
                temperature=0.7
            )
            welcome_msg = first_msg.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
        except Exception as e:
            st.error(f"Error connecting to OpenAI: {e}")

# --- 6. 显示聊天记录 ---
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="👤"):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar="🦘"):
            st.write(msg["content"])

# --- 7. 聊天输入与逻辑 ---
if user_input := st.chat_input("Type your response here..."):
    # 1. 显示用户输入
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)

    # 2. 生成 AI 回复
    with st.spinner("Customer is thinking..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o", 
                messages=st.session_state.messages,
                temperature=0.7, 
                max_tokens=150
            )
            ai_reply = response.choices[0].message.content
            
            # 3. 显示 AI 回复
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            with st.chat_message("assistant", avatar="🦘"):
                st.write(ai_reply)
        
        except Exception as e:
            st.error("Connection Error. Please check your API Key.")