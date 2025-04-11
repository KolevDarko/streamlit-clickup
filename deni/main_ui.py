import streamlit as st
import pandas as pd
from clickup_automation import import_to_clickup
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="ClickUp Task Importer",
    page_icon="📋",
    layout="wide"
)


# Initialize user_lists in session state if not already present
if 'user_lists' not in st.session_state:
    st.session_state.user_lists = None

if 'selected_list' not in st.session_state:
    st.session_state.selected_list = None

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #7B68EE;
        color: white;
    }
    .stButton>button:hover {
        background-color: #6A5ACD;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and description
st.title("📋 ClickUp Task Importer")
st.markdown("""
    Upload a CSV file to import tasks into ClickUp. The CSV should have the following columns:
    - name: Task name
    - description: Task description
""")

# Create two columns for layout
col1, col2 = st.columns([2, 1])
selected_list = None
list_id = None
with col1:
    with st.form("task_import_form"):
        # API Key Input
        api_key = st.text_input("Enter your ClickUp API Key", type="default", help="Your ClickUp API key should start with 'pk_'")
        list_id = st.text_input("Enter your ClickUp List ID")
        uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
        custom_prompt = st.text_area("Enter the custom prompt for this brand")
        form_submitted = st.form_submit_button("Import Tasks to ClickUp")

    if not api_key.startswith('pk_'):
        st.error("Invalid API key format. ClickUp API keys should start with 'pk_'")
        st.stop()

    if uploaded_file is not None:
        try:
            # Read and display the CSV
            df = pd.read_csv(uploaded_file)
            st.write("Preview of your data:")
            st.dataframe(df.head())

            # Show number of tasks
            st.write(f"Total tasks to import: {len(df)}")

            if form_submitted and list_id is not None:
                with st.spinner("Importing tasks..."):
                    # Save the uploaded file temporarily
                    temp_file = "temp_upload.csv"
                    df.to_csv(temp_file, index=False)

                    # Set the API key in environment for the duration of the import
                    os.environ['CLICKUP_API_KEY'] = api_key

                    # Import tasks
                    import_to_clickup(temp_file, list_id, custom_prompt)

                    # Remove temporary file
                    os.remove(temp_file)

                    st.success("Tasks imported successfully!")
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")


# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
