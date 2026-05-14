# Data-Analytics-Tool
## About the project
This Data Analytics tool is designed to help FMCG businesses dervie actionable insights from customers and sales data. Built with python, pandas and streamlit, it offers an interactive dashboard experience - letting users upload their data, explore distributor and seller-level performance and uncover key trends.

## Workflow
The workflow of this tool guides users through a seamless process of login to in-depth analysis.
1. Login with provided credentials\             
   Use the username 'admin' and password 'password' to access the system.
2. Upload customer and sales files\
   Upload either a combined customer-sales file or seperate customer and sales files using the provided interface.
3. Preview the data on the home page\
   Once uploaded, a preview table will show key columns, allowing verification of data structure.
4. Navigate to dashboard to see summaries\
   Navigate through tabs to see distributor-level summaries, seller insights, and seasonal trends.

## Installation
1. To install the tool, ensure you have python installed.\
2. Clone this repository to your local machine.\
3. Navigate to the project directory and run 'pip install -r requirements.txt' to install dependencies.\
4. Once installed, you can run the app by executing 'python run.py'.\

## Special Features
key features include:
1. **Customizable data template:**
   Provides a sample file so users know exactly which columns are required
2. **Flexible file upload options:**
   Users can upload either a single combined file or seperate files for customer and sales data.
3. **Built-in data validation:**
   Ensures that all required columns are present, alerting users to any issues before analysis
4. **Insightful log-based messages summarizing each chart:**
   Each graph is accomponied by a summary message highlighting key contributors
5. **Trend drill-down:**
   Users can explore monthly trends and drill down to daily patterns for more granular insights.
