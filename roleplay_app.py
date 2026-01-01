import streamlit as st
from openai import OpenAI
import datetime

# --- 1. Page Configuration ---
st.set_page_config(page_title="Ultech Training Pro", page_icon="🎓", layout="wide")

# --- 2. CSS Styling (Dark Mode Fix) ---
# We force text color to BLACK inside the colored boxes so it's readable in Dark Mode.
st.markdown("""
<style>
    /* User Message Box (Green) */
    .user-msg { 
        background-color: #dcf8c6; 
        padding: 10px; 
        border-radius: 10px; 
        margin-bottom: 10px; 
        text-align: right; 
        color: #000000 !important; /* Force Black Text */
    }
    
    /* Bot Message Box (Grey) */
    .bot-msg { 
        background-color: #f0f2f6; 
        padding: 10px; 
        border-radius: 10px; 
        margin-bottom: 10px; 
        text-align: left; 
        color: #000000 !important; /* Force Black Text */
    }
    
    /* Score Report Box (Light Green) */
    .score-box { 
        border: 2px solid #4CAF50; 
        padding: 20px; 
        border-radius: 10px; 
        background-color: #e8f5e9; 
        margin-top: 20px; 
        color: #1b5e20 !important; /* Force Dark Green/Black Text */
    }
    
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. Personas (Scenarios) ---
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

# --- 4. Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "report" not in st.session_state:
    st.session_state.report = None
if "attempt_count" not in st.session_state:
    st.session_state.attempt_count = 0

# --- 5. Sidebar: Settings & Controls ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=50)
    st.title("Ultech Training System")
    st.caption("Roleplay -> AI Grade -> Archive")
    
    api_key = st.text_input("OpenAI API Key", type="password")

    st.markdown("---")
    st.markdown("### 1. Staff Information")
    user_name = st.text_input("Your Name (e.g., Justin)", placeholder="Required for archiving")
    user_role = st.text_input("Role (e.g., Sales)", placeholder="Optional")

    st.markdown("---")
    st.markdown("### 2. Scenario Selection")
    difficulty = st.selectbox("Filter Difficulty:", ["All", "🟢 Easy", "🟡 Medium", "🔴 Hard"])
    
    # Filter Logic
    if difficulty == "🟢 Easy":
        options = [k for k in PERSONAS.keys() if "🟢" in k]
    elif difficulty == "🟡 Medium":
        options = [k for k in PERSONAS.keys() if "🟡" in k]
    elif difficulty == "🔴 Hard":
        options = [k for k in PERSONAS.keys() if "🔴" in k]
    else:
        options = list(PERSONAS.keys())
        
    scenario = st.selectbox("Current Opponent:", options)
    
    st.markdown("---")
    st.markdown("### 3. Controls")
    
    # Finish & Grade Button
    if st.button("🏁 Finish & Grade"):
        if not api_key:
            st.error("Please enter API Key.")
        elif not user_name:
            st.error("⚠️ Please enter your NAME above to save the record.")
        elif len(st.session_state.messages) < 3:
            st.warning("Conversation too short to grade. Please chat more.")
        else:
            # Increment attempt counter
            st.session_state.attempt_count += 1
            
            with st.spinner("AI Supervisor is analyzing your performance..."):
                client = OpenAI(api_key=api_key)
                # Extract text
                conversation_text = ""
                for m in st.session_state.messages:
                    if m["role"] != "system":
                        role_label = "STAFF" if m["role"] == "user" else "CUSTOMER"
                        conversation_text += f"{role_label}: {m['content']}\n"
                
                # Evaluation Prompt (English)
                eval_prompt = f"""
                You are a strict Training Supervisor at a phone repair shop (Ultech). 
                Evaluate the staff's performance based on the chat history below.
                
                [Scenario]: {scenario}
                [SOP Checkpoints]:
                1. Sales: Did they confirm the model? Did they upsell? Was the tone friendly (not pushy)?
                2. Intake: Did they explain risks (Data/FaceID/Liquid)? Did they manage expectations?
                3. Complaint: Did they use Empathy first? Did they avoid arguing? Did they follow escalation rules?
                
                [Output Format]:
                Generate a report in ENGLISH containing:
                1. **Final Score** (0-100)
                2. **Highlights** (What they did well)
                3. **Weaknesses** (Specific mistakes based on SOP)
                4. **Action Plan** (How to improve next time)
                
                [Chat History]:
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
                    st.error(f"Grading Failed: {e}")

    # Reset Button
    if st.button("🔄 Start New Round"):
        st.session_state.messages = []
        st.session_state.report = None
        st.rerun()

# --- 6. Main Interface ---
st.title("🎓 Ultech Training - Live Roleplay")
st.subheader(f"Scenario: {scenario}")

if not api_key:
    st.info("👈 Please enter API Key in the sidebar to start.")
    st.stop()

if not user_name:
    st.warning("👈 Please enter your NAME in the sidebar to ensure your score is recorded.")

client = OpenAI(api_key=api_key)

# Auto-start conversation
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

# Layout: Chat (Left) vs Report (Right)
col1, col2 = st.columns([2, 1])

with col1:
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"<div class='user-msg'>👤 <b>You:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
            elif msg["role"] == "assistant":
                st.markdown(f"<div class='bot-msg'>🦘 <b>Customer:</b><br>{msg['content']}</div>", unsafe_allow_html=True)

    # Chat Input
    # Disable input if name is missing (Optional strict mode, or just warning)
    if user_input := st.chat_input("Type your response here..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.rerun()

# AI Response Logic
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with col1:
        with st.spinner("Customer is replying..."):
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
                st.error(f"Error: {e}")

# --- 7. Grading Report Section (Right) ---
with col2:
    if st.session_state.report:
        st.markdown("### 📝 Performance Report")
        # Apply CSS class 'score-box' which now forces dark text
        st.markdown(f"<div class='score-box'>{st.session_state.report}</div>", unsafe_allow_html=True)
        
        # Prepare File Content
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Safe filename generation
        safe_name = "".join([c for c in user_name if c.isalpha() or c.isdigit() or c==' ']).strip().replace(" ", "_")
        file_name = f"{safe_name}_{current_date}_Attempt-{st.session_state.attempt_count}.txt"
        
        log_content = f"Ultech Training Report\n"
        log_content += f"Staff Name: {user_name}\n"
        log_content += f"Role: {user_role}\n"
        log_content += f"Date: {current_date} Time: {timestamp}\n"
        log_content += f"Scenario: {scenario}\n"
        log_content += "="*30 + "\nEVALUATION\n" + "="*30 + "\n"
        log_content += st.session_state.report + "\n\n"
        log_content += "="*30 + "\nFULL CHAT LOG\n" + "="*30 + "\n"
        
        for m in st.session_state.messages:
            if m["role"] != "system":
                role_label = "STAFF" if m["role"] == "user" else "CUSTOMER"
                log_content += f"[{role_label}]: {m['content']}\n"
        
        # Download Button
        st.download_button(
            label=f"📥 Download Report ({file_name})",
            data=log_content,
            file_name=file_name,
            mime="text/plain"
        )
    else:
        st.info("💡 **Instructions:**\n1. Enter your **Name** in the sidebar.\n2. Complete the roleplay.\n3. Click **'🏁 Finish & Grade'** to see your score.")
