import streamlit as st
import pandas as pd

# ====================== STREAMLIT APP ======================
st.title("🔍 Linux /etc/passwd Parser + Key User Highlighting")
st.write("Paste your `/etc/passwd` content → instantly see **root**, **human users**, and **system accounts** highlighted.")

passwd_content = st.text_area(
    "Paste /etc/passwd content here:",
    height=380,
    placeholder="root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n..."
)

if st.button("🚀 Parse & Highlight Key Users", type="primary") and passwd_content.strip():
    lines = [line.strip() for line in passwd_content.strip().split('\n') 
             if line.strip() and not line.startswith('#')]

    users = []
    interactive_shells = {"/bin/bash", "/bin/zsh", "/usr/bin/bash", "/usr/bin/zsh", "/bin/fish", "/usr/bin/fish"}

    for line in lines:
        parts = line.split(':')
        if len(parts) >= 7:
            username = parts[0]
            uid_str = parts[2]
            gid = parts[3]
            gecos = parts[4] if parts[4] else "(no comment)"
            home = parts[5]
            shell = parts[6]

            # Convert UID safely
            try:
                uid = int(uid_str)
            except ValueError:
                uid = 999999

            # ==================== SMART CLASSIFICATION ====================
            if uid == 0:
                importance = "🔥 ROOT"
                user_type = "Superuser (Critical)"
                highlight = "root"
            elif uid < 1000:
                importance = "⚙️ System"
                user_type = "System Account"
                highlight = "system"
            elif shell in interactive_shells or any(s in shell.lower() for s in ["bash", "zsh", "fish"]):
                importance = "👤 Human"
                user_type = "Regular User"
                highlight = "human"
            else:
                importance = "🛠️ Service"
                user_type = "Service / Daemon"
                highlight = "service"

            # Special known service accounts
            if username in ["www-data", "nginx", "apache", "httpd", "mysql", "postgres", 
                          "redis", "mongodb", "sshd", "git", "docker", "nobody", "postfix"]:
                importance = "🛠️ Service"
                user_type = f"Service ({username})"

            users.append({
                "Username": username,
                "UID": uid_str,
                "Type": user_type,
                "Importance": importance,
                "Full Name": gecos,
                "Home": home,
                "Shell": shell,
                "GID": gid,
                "highlight": highlight   # hidden helper column
            })

    if users:
        df = pd.DataFrame(users)
        
        # Sort by UID
        df['UID_num'] = pd.to_numeric(df['UID'], errors='coerce')
        df = df.sort_values('UID_num').drop(columns=['UID_num', 'highlight']).reset_index(drop=True)

        # ====================== HIGHLIGHTING ======================
        def highlight_key_users(row):
            if "ROOT" in row["Importance"]:
                return ['background-color: #ffdddd; color: #990000; font-weight: bold'] * len(row)
            elif "Human" in row["Importance"]:
                return ['background-color: #ddffdd'] * len(row)
            elif "System" in row["Importance"]:
                return ['background-color: #e6f0ff'] * len(row)
            elif "Service" in row["Importance"]:
                return ['background-color: #fff3cd'] * len(row)
            return [''] * len(row)

        styled_df = df.style.apply(highlight_key_users, axis=1)

        # ====================== DISPLAY ======================
        st.subheader("📊 Parsed Users (Key accounts highlighted)")
        
        # Legend
        st.markdown("""
        **Color Legend**  
        🔴 **Red** = Root / Superuser (highest risk)  
        🟢 **Green** = Human / Regular users  
        🔵 **Blue-gray** = System accounts  
        🟡 **Yellow** = Service accounts
        """, unsafe_allow_html=True)

        st.dataframe(styled_df, use_container_width=True, height=650)

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", len(df))
        with col2:
            st.metric("👤 Human Users", len(df[df['Importance'].str.contains("Human")]))
        with col3:
            st.metric("🔥 Root", len(df[df['UID'] == '0']))
        with col4:
            st.metric("⚙️ System/Service", len(df) - len(df[df['Importance'].str.contains("Human")]) - len(df[df['UID'] == '0']))

        # Quick filter
        if st.checkbox("Show only **key/important** users (root + human)"):
            important = df[df['Importance'].str.contains("ROOT|Human")]
            st.dataframe(important, use_container_width=True)

    else:
        st.warning("No valid user entries found.")
else:
    st.info("👆 Paste your `/etc/passwd` content and click the button above.")
