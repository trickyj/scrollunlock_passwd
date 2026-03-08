import streamlit as st
import pandas as pd

# Streamlit app title
st.title("Linux /etc/passwd Parser")
st.write("Paste the contents of your /etc/passwd file below to parse and display user information in a formatted table.")

# Text area for pasting the file content
passwd_content = st.text_area(
    "Paste /etc/passwd content here:",
    height=300,
    placeholder="e.g., root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n..."
)

if st.button("Parse and Display Table") and passwd_content.strip():
    # Parse the content
    lines = passwd_content.strip().split('\n')
    users = []
    
    for line in lines:
        if ':' in line and not line.startswith('#') and line.strip():  # Skip comments and empty lines
            parts = line.split(':')
            if len(parts) >= 7:
                username = parts[0]
                uid = parts[2]
                gid = parts[3]
                gecos = parts[4] if parts[4] else "(empty)"
                home = parts[5]
                shell = parts[6]
                
                # Determine type based on shell and UID
                user_type = "System"
                if shell == "/bin/bash":
                    user_type = "Interactive"
                elif uid == "0":
                    user_type = "Superuser"
                elif shell == "/bin/sync":
                    user_type = "System (sync)"
                elif "systemd" in gecos:
                    user_type = "Systemd"
                elif username in ["www-data", "sshd", "messagebus"]:
                    user_type = username.upper() if username == "sshd" else "System (" + username + ")"
                elif username == "nobody":
                    user_type = "Unprivileged"
                
                users.append({
                    "Username": username,
                    "UID": uid,
                    "GID": gid,
                    "Comment/GECOS": gecos,
                    "Home Directory": home,
                    "Shell": shell,
                    "Type": user_type
                })
    
    if users:
        # Create DataFrame for nice table display
        df = pd.DataFrame(users)

        # Highlight accounts by privilege level
        def highlight_row(row):
            uid = row.get("UID", "")
            username = row.get("Username", "")
            user_type = row.get("Type", "")
            try:
                uid_int = int(uid)
            except ValueError:
                uid_int = None

            # Superuser / root: red background, white text
            if uid_int == 0 or user_type == "Superuser" or username == "root":
                return ["background-color: red; color: white"] * len(row)

            # Extremely low-privilege account (e.g. nobody)
            if user_type == "Unprivileged" or username == "nobody":
                return ["background-color: #006400; color: white"] * len(row)

            # Normal interactive users (least-privilege human accounts)
            if user_type == "Interactive":
                return ["background-color: yellow; color: black"] * len(row)

            # Service / system accounts
            if user_type.startswith("System") or user_type == "Systemd":
                return ["background-color: #1e90ff; color: white"] * len(row)

            # Default: no special styling
            return [""] * len(row)

        styled_df = df.style.apply(highlight_row, axis=1)
        
        # Display the table
        st.subheader("Parsed User Table")
        st.dataframe(styled_df, use_container_width=True)
        
        # Optional: Show raw count
        st.info(f"Total users parsed: {len(users)}")
    else:
        st.warning("No valid user entries found. Ensure the content is in the correct /etc/passwd format.")
else:
    st.info("Paste the content and click the button to parse.")
