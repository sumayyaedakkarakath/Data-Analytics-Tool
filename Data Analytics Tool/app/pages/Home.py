import streamlit as st
import pandas as pd
from app.utils.validate import validation 

st.set_page_config(layout="wide")


st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color: #EDEDED; }
.stAppHeader { background-color: #00488e; }
.stAppHeader * { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.title("HOME")
st.write("Upload CSV or Excel files.")


REQUIRED_COLUMN1 = ["Distributor Code", "Seller Code", "Customer Category"]
REQUIRED_COLUMN2 = ["Customer Code", "Sale Quantity", "Sale Amount"]
COMBINED_REQS = ['Distributor Code', 'Seller Code', 'Customer Code', 'Customer Address', 'Customer Category', 'Date', 'Product Code', 'Sale Quantity', 'Sale Amount']


if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0


def clear_datasets():
    st.session_state["dataset_1"] = None
    st.session_state["dataset_2"] = None
    st.session_state.uploader_key += 1

option = st.pills(
    "Select an option",
    ["Customer & Sales in single file", "Customer & Sales in Separate files"],
    default="Customer & Sales in Separate files",
    on_change=clear_datasets # Clear state when user toggles option
)

# Initialize session state keys 
if "dataset_1" not in st.session_state: 
    st.session_state["dataset_1"] = None
if "dataset_2" not in st.session_state: 
    st.session_state["dataset_2"] = None

#fileoption2 - 2 files
if option == "Customer & Sales in Separate files":
    col1, col2 = st.columns(2)
    
    with col1:
        file_1 = st.file_uploader("Upload Customer Master", type=["csv", "xlsx"], key=f"file1_{st.session_state.uploader_key}")
        if file_1:
            raw_df1 = pd.read_csv(file_1) if file_1.name.endswith(".csv") else pd.read_excel(file_1)
            valid_df1, missing1, mismatch1 = validation(raw_df1, REQUIRED_COLUMN1)
            
            if missing1: 
                st.error(f"Missing: {', '.join(missing1)}")
            if mismatch1:
                for act, exp in mismatch1: 
                    st.warning(f"'{act}' should be '{exp}'")
            
            if not missing1 and not mismatch1:
                st.session_state["dataset_1"] = valid_df1
            else:
                st.session_state["dataset_1"] = None
            
    with col2:
        file_2 = st.file_uploader("Upload Sales file", type=["csv", "xlsx"], key=f"file2_{st.session_state.uploader_key}")
        if file_2:
            raw_df2 = pd.read_csv(file_2) if file_2.name.endswith(".csv") else pd.read_excel(file_2)
            valid_df2, missing2, mismatch2 = validation(raw_df2, REQUIRED_COLUMN2)
            
            if missing2: 
                st.error(f"Missing: {', '.join(missing2)}")
            if mismatch2:
                for act, exp in mismatch2: 
                    st.warning(f"'{act}' should be '{exp}'")
            
            if not missing2 and not mismatch2:
                st.session_state["dataset_2"] = valid_df2
            else:
                st.session_state["dataset_2"] = None

#fileoption1 - single file
else:
    combined_file = st.file_uploader("Upload Combined file", type=["csv", "xlsx"], key=f"filecombined_{st.session_state.uploader_key}")
    if combined_file:
        raw_file = pd.read_csv(combined_file) if combined_file.name.endswith(".csv") else pd.read_excel(combined_file)
        valid_data, missing, mismatch = validation(raw_file, COMBINED_REQS)

        if missing: st.error(f"Missing: {', '.join(missing)}")
        if mismatch:
            for act, exp in mismatch: st.warning(f"'{act}' should be '{exp}'")
            
        if not missing and not mismatch:
            potential_d1 = [
                'Distributor Code', 'Seller Code', 'Customer Code', 
                'Customer Category', 'Customer Address', 'Distributor Name', 
                'Seller Name', 'Customer Name', 'latitude', 'longitude'
            ]
            
            
            actual_d1 = [col for col in potential_d1 if col in valid_data.columns]
            st.session_state["dataset_1"] = valid_data[actual_d1].copy()
            
            
            potential_d2 = [
                'Date', 'Customer Code', 'Customer Category', 'Product Code', 
                'Sale Quantity', 'Sale Amount', 'Distributor Code', 'Seller Code', 
                'Product Name', 'Product Width', 'Product Height', 'Product Depth'
            ]
            
            
            actual_d2 = [col for col in potential_d2 if col in valid_data.columns]
            st.session_state["dataset_2"] = valid_data[actual_d2].copy()
            
        else:
            st.session_state["dataset_1"] = None
            st.session_state["dataset_2"] = None




d1 = st.session_state["dataset_1"]
d2 = st.session_state["dataset_2"]

if d1 is not None and d2 is not None:
    st.divider()
    p_col1, p_col2 = st.columns(2)
    
    with p_col1:
        st.subheader("Preview: Customer Master")
        st.dataframe(d1.head())
        st.caption(f"Shape: {d1.shape}")
    with p_col2:
        st.subheader("Preview: Sales")
        st.dataframe(d2.head())
        st.caption(f"Shape: {d2.shape}")

    if st.button("Reload Data"):
        st.session_state["dataset_1"] = None
        st.session_state["dataset_2"] = None
        st.session_state.uploader_key += 1
        st.rerun()
else:
    st.divider()
    

 
    if option == "Customer & Sales in Separate files":
        template_col1 = ['Distributor Code', 'Distributor Name','Seller Code','Seller Name','Customer Code','Customer Name',
                         'Customer Address',	'Customer Category','Latitude','Longitude']
        template_col2 = ['Date','Customer Code'	,'Distributor Code'	,'Seller Code'	,'Customer Category','Product Code'	,'Product Name'	,'Product Width',
                         'Product Height',	'Product Depth','Sale Quantity','Sale Amount']

        template_df1 = pd.DataFrame(
            [{col: "" for col in template_col1} for _ in range(3)]
        )
        template_df2 = pd.DataFrame(
            [{col: "" for col in template_col2} for _ in range(3)]
        )
        cols = st.columns(2)
        with cols[0]:
           st.subheader("Customer Master Sample")
           st.dataframe(template_df1, use_container_width=True) 
        with cols[1]:
            st.subheader("Sales Sample")
            st.dataframe(template_df2, use_container_width=True) 

    else:
        template_col = ['Distributor Code', 'Distributor Name','Seller Code','Seller Name',
                        'Customer Code','Customer Name','Customer Address',	'Customer Category',
                        'Latitude','Longitude','Date','Product Code','Product Name',
                        'Product Width','Product Height','Product Depth','Sale Quantity','Sale Amount']


        template_df = pd.DataFrame(
            [{col: "" for col in template_col} for _ in range(3)]
        )
        st.subheader("Customer & Sales Sample")
        st.dataframe(template_df, use_container_width=True)


    if option == "Customer & Sales in Separate files":
        if not (file_1 and file_2):
            st.warning("Upload required files to see data preview")
    else:
        if not combined_file:
            st.warning("Upload required file to see data preview")
 
        


