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
        
        # Display the table
        st.subheader("Parsed User Table")
        st.dataframe(df, use_container_width=True)
        
        # Optional: Show raw count
        st.info(f"Total users parsed: {len(users)}")
    else:
        st.warning("No valid user entries found. Ensure the content is in the correct /etc/passwd format.")
else:
    st.info("Paste the content and click the button to parse.")
