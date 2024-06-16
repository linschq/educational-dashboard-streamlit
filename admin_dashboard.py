import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Set Streamlit page configuration
st.set_page_config(layout="wide")

# Load data
# FILE_JUNIOR_PROCESSED = 'Processed_Log_Problem_Junior.parquet.gzip'
# FILE_LOG_PROCESSED = 'Processed_Log_Problem.parquet.gzip'
# FILE_USER_PROCESSED = 'Processed_Info_UserData.parquet.gzip'
# FILE_CONTENT_PROCESSED = 'Processed_Info_Content.parquet.gzip'

# df_user = pd.read_parquet(FILE_USER_PROCESSED)
# df_content = pd.read_parquet(FILE_CONTENT_PROCESSED)
# df_log = pd.read_parquet(FILE_LOG_PROCESSED)
# df_junior = pd.read_parquet(FILE_JUNIOR_PROCESSED)

@st.cache_data
def data_ready():
    df_final_uuid_rating = pd.read_parquet('final_uuid_rating.parquet.gzip')
    df_userdata_named = pd.read_parquet('UserData_named_ID_EN.parquet.gzip')
    df_final_upid_rating = pd.read_parquet('final_upid_rating.parquet.gzip')
    return df_final_uuid_rating, df_userdata_named, df_final_upid_rating

df_final_uuid_rating, df_userdata_named, df_final_upid_rating = data_ready()

# Merge dataframes
merged_df = pd.merge(df_final_uuid_rating, df_userdata_named, on='uuid', how='inner')

st.title('Admin Dashboard')

# Filter out students with a rating of zero
non_zero_ratings_df = merged_df[merged_df['final_curr'] > 0]

# Calculate average rating and student count per city
city_counts = non_zero_ratings_df['user_city'].value_counts().reset_index()
city_counts.columns = ['City', 'Student Count']

city_ratings = non_zero_ratings_df.groupby('user_city')['final_curr'].mean().reset_index()
city_ratings.columns = ['City', 'Average Rating']

city_data = pd.merge(city_counts, city_ratings, on='City')

# Create the dual-axis bar chart
fig = go.Figure()

# Add bar chart for student count
fig.add_trace(go.Bar(
    x=city_data['City'],
    y=city_data['Student Count'],
    name='Student Count',
    marker=dict(color='rgba(0, 0, 139, 0.7)')  # Dark blue color
))

# Add line chart for average rating
fig.add_trace(go.Scatter(
    x=city_data['City'],
    y=city_data['Average Rating'],
    name='Average Rating',
    yaxis='y2',
    mode='lines+markers',
    marker=dict(color='rgba(255, 0, 0, 0.7)'),  # Red color
    line=dict(color='rgba(255, 0, 0, 0.7)')
))

# Create axis objects
fig.update_layout(
    title={'text': 'Distribution of Students Home Cities and Average Ratings', 'x': 0.5, 'xanchor': 'center'},
    xaxis=dict(title='City'),
    yaxis=dict(
        title='Student Count',
        titlefont=dict(color='rgba(0, 0, 139, 0.7)'),
        tickfont=dict(color='rgba(0, 0, 139, 0.7)')
    ),
    yaxis2=dict(
        title='Average Rating',
        titlefont=dict(color='rgba(255, 0, 0, 0.7)'),
        tickfont=dict(color='rgba(255, 0, 0, 0.7)'),
        overlaying='y',
        side='right'
    ),
    legend=dict(x=0.1, y=1.1, orientation='h'),
    plot_bgcolor='rgba(255, 255, 255, 0.9)',
    paper_bgcolor='rgba(240, 240, 240, 0.9)',
    height=600  # Adjust height to align with annotation box
)

# Display the chart and annotation in Streamlit with 3:1 ratio
col1, col2 = st.columns([3, 1])

with col1:
    st.header('Student Demographic Data')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.header('Insights')
    st.markdown(
        """
        <div style="background-color: rgba(240, 240, 240, 0.9); padding: 10px; height: 600px;">
            <p style="color: black;">
                1. The majority of students come from 'tp' and 'ntpc', showing the highest counts.<br>
                2. Cities 'tc' and 'ty' stand out with high average ratings despite moderate student counts.<br>
                3. Lower student count cities like 'ttct' and 'kl' exhibit high average ratings, suggesting better performance quality.<br>
                4. There is a notable variability in average ratings across cities, indicating regional differences in student performance.<br>
                5. No clear correlation exists between student count and average rating, implying that quality doesn't always align with quantity.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

st.header('Accuracy Analysis Based on Lesson Category')

# Tab selection
tab1, tab2 = st.tabs(["Student Accuracy", "Problem Accuracy"])

def add_vlines(fig, data, mean_val, median_val, q1_val, q3_val):
    fig.add_vline(x=mean_val, line=dict(color='red', width=2, dash='dash'), annotation_text=f"Mean: {mean_val:.2f}", annotation_position="top right")
    fig.add_vline(x=median_val, line=dict(color='green', width=2, dash='dash'), annotation_text=f"Median: {median_val:.2f}", annotation_position="top right")
    fig.add_vline(x=q1_val, line=dict(color='blue', width=2, dash='dash'), annotation_text=f"Q1: {q1_val:.2f}", annotation_position="top right")
    fig.add_vline(x=q3_val, line=dict(color='purple', width=2, dash='dash'), annotation_text=f"Q3: {q3_val:.2f}", annotation_position="top right")

def plot_accuracy_distribution(data, category):
    fig = go.Figure()
    # Histogram for accuracy
    fig.add_trace(go.Histogram(x=data['accuracy'], nbinsx=50, name='Accuracy', marker=dict(color='rgba(70, 130, 180, 0.7)', line=dict(color='rgba(70, 130, 180, 1)', width=1.5))))
    
    # Statistics
    mean_accuracy = data['accuracy'].mean()
    median_accuracy = data['accuracy'].median()
    q1_accuracy = data['accuracy'].quantile(0.25)
    q3_accuracy = data['accuracy'].quantile(0.75)
    
    add_vlines(fig, data['accuracy'], mean_accuracy, median_accuracy, q1_accuracy, q3_accuracy)
    
    # Update layout
    fig.update_layout(
        title={'text': f'Distribution of {category} Accuracy', 'x': 0.5, 'xanchor': 'center'},
        xaxis=dict(title='Accuracy'),
        yaxis=dict(title='Count'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

with tab1:
    st.subheader('Distribution of Student Accuracy')

    # Filter out students with a rating of zero
    arithmetic_data = merged_df[merged_df['categories'] == 'Arithmetic']
    geometry_data = merged_df[merged_df['categories'] == 'Geometry']
    algebra_data = merged_df[merged_df['categories'] == 'Algebra']

    arithmetic_data_no_zeros = arithmetic_data[arithmetic_data['accuracy'] > 0]
    geometry_data_no_zeros = geometry_data[geometry_data['accuracy'] > 0]
    algebra_data_no_zeros = algebra_data[algebra_data['accuracy'] > 0]

    fig_arithmetic = plot_accuracy_distribution(arithmetic_data_no_zeros, 'Arithmetic')
    fig_geometry = plot_accuracy_distribution(geometry_data_no_zeros, 'Geometry')
    fig_algebra = plot_accuracy_distribution(algebra_data_no_zeros, 'Algebra')

    # Display histograms in three columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(fig_arithmetic, use_container_width=True)
    with col2:
        st.plotly_chart(fig_geometry, use_container_width=True)
    with col3:
        st.plotly_chart(fig_algebra, use_container_width=True)
    
    # Add insights
    st.markdown(
        """
        ### Insights
        1. **Arithmetic**: The majority of students demonstrate strong proficiency in arithmetic, with a high mean accuracy of 0.72, indicating that arithmetic concepts are well-grasped and mastered by most students.
        2. **Geometry**: The mean accuracy of 0.58 in geometry suggests that students find this subject more challenging, with a wider spread in accuracy. This highlights the need for targeted interventions to improve understanding and performance in geometric concepts.
        3. **Algebra**: Students show moderate success in algebra, with a mean accuracy of 0.64. While performance is better than in geometry, there is still room for improvement to achieve higher proficiency levels.
        """
    )

with tab2:
    st.subheader('Distribution of Problem Accuracy')

    # Arithmetic accuracy distribution
    arithmetic_data = df_final_upid_rating[df_final_upid_rating['categories'] == 'Arithmetic']
    arithmetic_data_no_zeros = arithmetic_data[arithmetic_data['accuracy'] > 0]

    fig_arithmetic = plot_accuracy_distribution(arithmetic_data_no_zeros, 'Arithmetic')
    
    # Geometry accuracy distribution
    geometry_data = df_final_upid_rating[df_final_upid_rating['categories'] == 'Geometry']
    geometry_data_no_zeros = geometry_data[geometry_data['accuracy'] > 0]

    fig_geometry = plot_accuracy_distribution(geometry_data_no_zeros, 'Geometry')
    
    # Algebra accuracy distribution
    algebra_data = df_final_upid_rating[df_final_upid_rating['categories'] == 'Algebra']
    algebra_data_no_zeros = algebra_data[algebra_data['accuracy'] > 0]

    fig_algebra = plot_accuracy_distribution(algebra_data_no_zeros, 'Algebra')

    # Display histograms in three columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.plotly_chart(fig_arithmetic, use_container_width=True)
    with col2:
        st.plotly_chart(fig_geometry, use_container_width=True)
    with col3:
        st.plotly_chart(fig_algebra, use_container_width=True)

    st.markdown(
        """
        ### Insights
        1. **Arithmetic**: Problems in this category have a mean accuracy of 0.68, indicating that students generally perform well on arithmetic problems. This reflects a solid understanding and application of arithmetic principles.
        2. **Geometry**: The mean accuracy of 0.52 for geometry problems points to significant variability in student performance, suggesting that some students struggle more with geometry. This underscores the importance of providing additional resources and support for geometry-related topics.
        3. **Algebra**: With a mean accuracy of 0.60, algebra problems see moderate success among students. This suggests a decent grasp of algebraic concepts, but highlights the need for further practice and reinforcement to achieve higher accuracy and mastery.
        """
    )

# Calculate average time spent per session
# df_log['timestamp'] = pd.to_datetime(df_log['timestamp_TW'])
# df_log['date'] = df_log['timestamp'].dt.date
# avg_time_per_day = df_log.groupby('date')['total_sec_taken'].mean().reset_index()

@st.cache_data
def data_ready3():
    avg_time_per_day = pd.read_parquet('time_per_day.parquet.gzip')
    return avg_time_per_day

avg_time_per_day = data_ready3()

# Merge dataframes
merged_df = pd.merge(df_final_uuid_rating, df_userdata_named, on='uuid', how='inner')

# User Engagement Metrics
st.header('User Engagement Metrics: Daily New Users and Average Time Spent on Platform per Day')

# Calculate login counts per day
merged_df['login_date'] = pd.to_datetime(merged_df['first_login_date_TW']).dt.date
login_counts_per_day = merged_df.groupby('login_date').size().reset_index(name='user_count')

# Date range for the slider
min_date = login_counts_per_day['login_date'].min()
max_date = login_counts_per_day['login_date'].max()

# Slider for date range selection
start_date, end_date = st.slider(
    "Select Date Range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

# Filter data based on slider
filtered_login_counts = login_counts_per_day[(login_counts_per_day['login_date'] >= start_date) & (login_counts_per_day['login_date'] <= end_date)]
filtered_avg_time = avg_time_per_day[(avg_time_per_day['date'] >= start_date) & (avg_time_per_day['date'] <= end_date)]

# Plot for daily new users
fig_login = px.line(
    filtered_login_counts, 
    x='login_date', 
    y='user_count', 
    title='Number of Users Registered Per Day',
    line_shape='spline',  
    markers=True  
)

fig_login.update_traces(
    line=dict(color='rgba(0, 0, 139, 0.8)'),  # Dark blue color
    marker=dict(color='rgba(0, 0, 139, 0.8)', size=5)  # Dark blue color
)

fig_login.update_layout(
    title={'text': 'Number of Users Registered Per Day', 'x': 0.5, 'xanchor': 'center'},
    xaxis_title='Date',
    yaxis_title='Number of Users',
    plot_bgcolor='rgba(255, 255, 255, 0.9)',  # Light pastel background color
    paper_bgcolor='rgba(240, 240, 240, 0.9)'  # Light pastel paper background color
)

# Plot for average time spent on platform per day
fig_avg_time = px.line(
    filtered_avg_time,
    x='date',
    y='total_sec_taken',
    title='Average Time Spent on Platform per Day',
    line_shape='spline', 
    markers=True  
)

fig_avg_time.update_traces(
    line=dict(color='rgba(0, 0, 139, 0.8)'),  # Dark blue color
    marker=dict(color='rgba(0, 0, 139, 0.8)', size=5)  # Dark blue color
)

fig_avg_time.update_layout(
    title={'text': 'Average Time Spent on Platform per Day', 'x': 0.5, 'xanchor': 'center'},
    xaxis_title='Date',
    yaxis_title='Average Time (seconds)',
    plot_bgcolor='rgba(255, 255, 255, 0.9)',  
    paper_bgcolor='rgba(240, 240, 240, 0.9)'  
)

# Display the two charts side by side
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(fig_login, use_container_width=True)

with col2:
    st.plotly_chart(fig_avg_time, use_container_width=True)

st.markdown(
    """
    ### Insights
    - **User Registration Trends**: There is a significant spike around early August 2018, likely due to a marketing campaign or product launch.
    - **Gradual Decline**: After the spike, registrations decrease and stabilize with periodic peaks, indicating effective periodic marketing efforts.
    - **Increasing Engagement**: The average time spent on the platform per day increases from August to November 2018, indicating rising user engagement.
    - **Stabilization**: After November, the average time spent on the platform stabilizes between 40 to 50 seconds, reflecting consistent engagement from users.
    """
)

# Filter out students with more than zero activities
merged_df = merged_df[merged_df['num_activities'] > 100]

# Top 5 Students section
st.header('Top 5 Outstanding Students')

cities = ['All Cities'] + merged_df['user_city'].unique().tolist()
selected_city = st.selectbox('Choose Cities:', cities)

if selected_city != 'All Cities':
    filtered_df = merged_df[merged_df['user_city'] == selected_city]
else:
    filtered_df = merged_df

# Group and aggregate data
df_group = filtered_df.groupby(['alias', 'user_city'], observed=True).agg(
    attempt_count=('num_activities', 'sum'),
    average_rating=('final_curr', 'mean')
).reset_index()

# Rank top 10 students by average rating and attempt count
df_rank_rating = df_group.nlargest(5, 'average_rating').sort_values(by='average_rating', ascending=False)
df_rank_attempt = df_group.nlargest(5, 'attempt_count').sort_values(by='attempt_count', ascending=False)

# Plot top 5 students by average rating
rank1, rank2 = st.columns(2)
with rank1:
    fig = px.bar(df_rank_rating, x='alias', y='average_rating', color='user_city',
                 title=f'<span style="text-align:center;">Top 5 Highest Rated Students in {selected_city}</span>',
                 labels={'alias': 'Student Names', 'average_rating': 'Average Rating'},
                 height=600,
                 )
    fig.update_layout(title_x=0.5)  # Center the title
    st.plotly_chart(fig, use_container_width=True)

# Plot top 5 students by attempt count
with rank2:
    fig = px.bar(df_rank_attempt, x='alias', y='attempt_count', color='user_city',
                 title=f'<span style="text-align:center;">Top 5 Most Active Students in {selected_city}</span>',
                 labels={'alias': 'Student Names', 'attempt_count': 'Attempt Count'},
                 height=600,)
    fig.update_layout(title_x=0.5)  # Center the title
    st.plotly_chart(fig, use_container_width=True)

# Top Rated Students
st.markdown(
    f"""
    <div style="text-align: left; font-size: 20px;">
        <p><strong>Top Rated Students</strong></p>
        <ul>
            <li>{df_rank_rating.iloc[0]['alias']} from {df_rank_rating.iloc[0]['user_city']} is leading with an impressive average rating of {df_rank_rating.iloc[0]['average_rating']:.2f}. Their dedication and consistent performance set them apart.</li>
            <li>{df_rank_rating.iloc[1]['alias']} from {df_rank_rating.iloc[1]['user_city']} follows closely with a rating of {df_rank_rating.iloc[1]['average_rating']:.2f}. Their efforts in achieving such high scores are commendable.</li>
            <li>{df_rank_rating.iloc[2]['alias']} from {df_rank_rating.iloc[2]['user_city']} stands out with a rating of {df_rank_rating.iloc[2]['average_rating']:.2f}, showcasing their academic excellence.</li>
            <li>{df_rank_rating.iloc[3]['alias']} from {df_rank_rating.iloc[3]['user_city']} has earned a rating of {df_rank_rating.iloc[3]['average_rating']:.2f}, highlighting their hard work.</li>
            <li>{df_rank_rating.iloc[4]['alias']} from {df_rank_rating.iloc[4]['user_city']} is remarkable with a rating of {df_rank_rating.iloc[4]['average_rating']:.2f}, reflecting their excellence.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

# Most Active Students
st.markdown(
    f"""
    <div style="text-align: left; font-size: 20px;">
        <p><strong>Most Active Students</strong></p>
        <ul>
            <li>{df_rank_attempt.iloc[0]['alias']} from {df_rank_attempt.iloc[0]['user_city']} has the highest attempt count of {df_rank_attempt.iloc[0]['attempt_count']} activities, demonstrating their dedication and persistence.</li>
            <li>{df_rank_attempt.iloc[1]['alias']} from {df_rank_attempt.iloc[1]['user_city']} is highly active with {df_rank_attempt.iloc[1]['attempt_count']} attempts, indicating a strong commitment to their studies.</li>
            <li>{df_rank_attempt.iloc[2]['alias']} from {df_rank_attempt.iloc[2]['user_city']} shows great engagement with {df_rank_attempt.iloc[2]['attempt_count']} attempts, reflecting their determination to improve.</li>
            <li>{df_rank_attempt.iloc[3]['alias']} from {df_rank_attempt.iloc[3]['user_city']} has a notable attempt count of {df_rank_attempt.iloc[3]['attempt_count']}, showcasing their hard work.</li>
            <li>{df_rank_attempt.iloc[4]['alias']} from {df_rank_attempt.iloc[4]['user_city']} is actively participating with {df_rank_attempt.iloc[4]['attempt_count']} attempts, demonstrating their commitment.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True
)

st.header('User Retention')

# Filter log data to include only users in df_final_uuid_rating
# df_log_filtered = df_log[df_log['uuid'].isin(df_final_uuid_rating['uuid'])].copy()

# # Cohort Analysis Preparation
# df_log_filtered['timestamp_TW'] = pd.to_datetime(df_log_filtered['timestamp_TW'])
# df_log_filtered['Order_Mo'] = df_log_filtered['timestamp_TW'].dt.to_period('M').astype(str)
# df_log_filtered['First_Mo'] = df_log_filtered.groupby('uuid')['timestamp_TW'].transform('min').dt.to_period('M').astype(str)
# df_cohort = df_log_filtered.groupby(['First_Mo', 'Order_Mo']).agg(n_customers=('uuid', 'nunique')).reset_index(drop=False)
# df_cohort['period_number'] = (pd.to_datetime(df_cohort['Order_Mo']).dt.to_period('M') - pd.to_datetime(df_cohort['First_Mo']).dt.to_period('M')).apply(lambda x: x.n)

@st.cache_data
def data_ready4():
    df_cohort = pd.read_parquet('cohort.parquet.gzip')
    return df_cohort
df_cohort = data_ready4()

cohort_pivot = df_cohort.pivot_table(index='First_Mo', columns='period_number', values='n_customers')

cohort_size = cohort_pivot.iloc[:, 0]
retention_matrix = cohort_pivot.divide(cohort_size, axis=0).round(4) * 100

blue_white_colorscale = [
    [0.0, 'rgba(173, 216, 230, 0.1)'],
    [0.5, 'rgba(173, 216, 230, 0.5)'],  
    [1.0, 'rgba(0, 0, 255, 1)']         
]

fig = px.imshow(
    retention_matrix,
    labels=dict(x="Period Number", y="Cohort Month", color="Retention Rate"),
    x=retention_matrix.columns.astype(str),
    y=retention_matrix.index.astype(str),
    color_continuous_scale='RdYlGn',
    text_auto=True
)

fig.update_layout(
    xaxis_title="Period Number",
    yaxis_title="Cohort Month",
    coloraxis_colorbar=dict(title="Retention Rate"),
    font=dict(color="black"),  # Set text color to black
    plot_bgcolor='rgba(255, 255, 255, 0.9)',
    paper_bgcolor='rgba(240, 240, 240, 0.9)',
    height=1000,  # Adjust the height of the heatmap
    width=1200   # Adjust the width of the heatmap
)
st.plotly_chart(fig, use_container_width=True)

st.subheader('Insights')
st.write("""
1. **Overall Retention Trend**: The overall retention rate declines significantly over time, with the highest retention observed in the initial months. This suggests that users are most engaged shortly after joining but tend to drop off as time progresses.
2. **High Initial Engagement**: The initial retention rates are relatively high across all cohort months, indicating strong initial engagement from new users. This highlights the effectiveness of initial onboarding and user engagement strategies.
3. **Significant Drop-Off**: A noticeable drop in retention is observed after the first few months. For example, the cohort from November 2018 drops from 100% in the first period to around 37.19% in the second period. This pattern is consistent across multiple cohorts, indicating a common challenge in sustaining user interest long-term.
4. **Cohort-Specific Observations**: Certain cohorts, such as those from May 2019 and March 2019, show slightly better retention rates in the mid-periods compared to other months. This may indicate the impact of specific events, features, or campaigns that were particularly effective during those times.
5. **Long-Term Retention Challenges**: Long-term retention rates drop to single digits across all cohorts. By the tenth period, retention rates are generally below 10%, emphasizing the need for targeted strategies to re-engage long-term users and address reasons for churn.
""")
