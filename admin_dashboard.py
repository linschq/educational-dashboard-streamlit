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

# Menampilkan judul
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
    title='Distribution of Students Home Cities and Average Ratings',
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
    paper_bgcolor='rgba(240, 240, 240, 0.9)'
)

# Display the bar chart in Streamlit
st.header('Student Demographic Data')
st.plotly_chart(fig, use_container_width=True)

# Distribusi Akurasi Student Berdasarkan Problem
st.header('Accuracy Analysis Based on Lesson Category')
# Menambahkan tab di Streamlit
tab1, tab2 = st.tabs(["Student Accuracy", "Problem Accuracy"])

with tab1:
    st.subheader('Distribution of Student Accuracy')

    # Filter out students with a rating of zero
    arithmetic_data = merged_df[merged_df['categories'] == 'Arithmetic']
    geometry_data = merged_df[merged_df['categories'] == 'Geometry']
    algebra_data = merged_df[merged_df['categories'] == 'Algebra']

    arithmetic_data_no_zeros = arithmetic_data[arithmetic_data['accuracy'] > 0]
    geometry_data_no_zeros = geometry_data[geometry_data['accuracy'] > 0]
    algebra_data_no_zeros = algebra_data[algebra_data['accuracy'] > 0]

    # Arithmetic accuracy distribution
    fig_arithmetic = go.Figure()
    fig_arithmetic.add_trace(
        go.Histogram(
            x=arithmetic_data_no_zeros['accuracy'],
            nbinsx=50,
            marker=dict(color='rgba(70, 130, 180, 0.7)', line=dict(color='rgba(70, 130, 180, 1)', width=1.5))  # Steel blue
        )
    )
    mean_accuracy_arithmetic = arithmetic_data_no_zeros['accuracy'].mean()
    fig_arithmetic.add_vline(
        x=mean_accuracy_arithmetic,
        line=dict(color='red', width=2, dash='dash'),
        annotation_text=f"Mean: {mean_accuracy_arithmetic:.2f}",
        annotation_position="top right"
    )
    fig_arithmetic.update_layout(title_text='Distribution of student accuracy for category: Arithmetic', showlegend=False)

    # Geometry accuracy distribution
    fig_geometry = go.Figure()
    fig_geometry.add_trace(
        go.Histogram(
            x=geometry_data_no_zeros['accuracy'],
            nbinsx=50,
            marker=dict(color='rgba(100, 149, 237, 0.7)', line=dict(color='rgba(100, 149, 237, 1)', width=1.5))  # Cornflower blue
        )
    )
    mean_accuracy_geometry = geometry_data_no_zeros['accuracy'].mean()
    fig_geometry.add_vline(
        x=mean_accuracy_geometry,
        line=dict(color='red', width=2, dash='dash'),
        annotation_text=f"Mean: {mean_accuracy_geometry:.2f}",
        annotation_position="top right"
    )
    fig_geometry.update_layout(title_text='Distribution of student accuracy for category: Geometry', showlegend=False)

    # Algebra accuracy distribution
    fig_algebra = go.Figure()
    fig_algebra.add_trace(
        go.Histogram(
            x=algebra_data_no_zeros['accuracy'],
            nbinsx=50,
            marker=dict(color='rgba(0, 0, 139, 0.7)', line=dict(color='rgba(0, 0, 139, 1)', width=1.5))  # Dark blue
        )
    )
    mean_accuracy_algebra = algebra_data_no_zeros['accuracy'].mean()
    fig_algebra.add_vline(
        x=mean_accuracy_algebra,
        line=dict(color='red', width=2, dash='dash'),
        annotation_text=f"Mean: {mean_accuracy_algebra:.2f}",
        annotation_position="top right"
    )
    fig_algebra.update_layout(title_text='Distribution of student accuracy for category: Algebra', showlegend=False)

    # Display histograms in three columns
    akurasi_container = st.container()
    with akurasi_container:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.plotly_chart(fig_arithmetic, use_container_width=True)

        with col2:
            st.plotly_chart(fig_geometry, use_container_width=True)

        with col3:
            st.plotly_chart(fig_algebra, use_container_width=True)

with tab2:
    st.subheader('Distribution of Problem Accuracy')

    # Arithmetic accuracy distribution
    arithmetic_data = df_final_upid_rating[df_final_upid_rating['categories'] == 'Arithmetic']
    arithmetic_data_no_zeros = arithmetic_data[arithmetic_data['accuracy'] > 0]

    fig_arithmetic = go.Figure()
    fig_arithmetic.add_trace(
        go.Histogram(
            x=arithmetic_data_no_zeros['accuracy'],
            nbinsx=50,
            marker=dict(color='rgba(70, 130, 180, 0.7)', line=dict(color='rgba(70, 130, 180, 1)', width=1.5))  # Steel blue
        )
    )
    mean_accuracy_arithmetic = arithmetic_data_no_zeros['accuracy'].mean()
    fig_arithmetic.add_vline(
        x=mean_accuracy_arithmetic,
        line=dict(color='red', width=2, dash='dash'),
        annotation_text=f"Mean: {mean_accuracy_arithmetic:.2f}",
        annotation_position="top right"
    )
    fig_arithmetic.update_layout(title_text='Distribution of Problem Accuracy for: Arithmetic', showlegend=False)

    # Geometry accuracy distribution
    geometry_data = df_final_upid_rating[df_final_upid_rating['categories'] == 'Geometry']
    geometry_data_no_zeros = geometry_data[geometry_data['accuracy'] > 0]

    fig_geometry = go.Figure()
    fig_geometry.add_trace(
        go.Histogram(
            x=geometry_data_no_zeros['accuracy'],
            nbinsx=50,
            marker=dict(color='rgba(100, 149, 237, 0.7)', line=dict(color='rgba(100, 149, 237, 1)', width=1.5))  # Cornflower blue
        )
    )
    mean_accuracy_geometry = geometry_data_no_zeros['accuracy'].mean()
    fig_geometry.add_vline(
        x=mean_accuracy_geometry,
        line=dict(color='red', width=2, dash='dash'),
        annotation_text=f"Mean: {mean_accuracy_geometry:.2f}",
        annotation_position="top right"
    )
    fig_geometry.update_layout(title_text='Distribution of Problem Accuracy for: Geometry', showlegend=False)

    # Algebra accuracy distribution
    algebra_data = df_final_upid_rating[df_final_upid_rating['categories'] == 'Algebra']
    algebra_data_no_zeros = algebra_data[algebra_data['accuracy'] > 0]

    fig_algebra = go.Figure()
    fig_algebra.add_trace(
        go.Histogram(
            x=algebra_data_no_zeros['accuracy'],
            nbinsx=50,
            marker=dict(color='rgba(0, 0, 139, 0.7)', line=dict(color='rgba(0, 0, 139, 1)', width=1.5))  # Dark blue
        )
    )
    mean_accuracy_algebra = algebra_data_no_zeros['accuracy'].mean()
    fig_algebra.add_vline(
        x=mean_accuracy_algebra,
        line=dict(color='red', width=2, dash='dash'),
        annotation_text=f"Mean: {mean_accuracy_algebra:.2f}",
        annotation_position="top right"
    )
    fig_algebra.update_layout(title_text='Distribution of Problem Accuracy for: Algebra', showlegend=False)

    # Display histograms in three columns
    akurasi_container = st.container()
    with akurasi_container:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.plotly_chart(fig_arithmetic, use_container_width=True)

        with col2:
            st.plotly_chart(fig_geometry, use_container_width=True)

        with col3:
            st.plotly_chart(fig_algebra, use_container_width=True)

# Calculate average time spent per session
# df_log['timestamp'] = pd.to_datetime(df_log['timestamp_TW'])
# df_log['date'] = df_log['timestamp'].dt.date
# avg_time_per_day = df_log.groupby('date')['total_sec_taken'].mean().reset_index()

@st.cache_data
def data_ready3():
    avg_time_per_day = pd.read_parquet('time_per_day.parquet.gzip')
    return avg_time_per_day
avg_time_per_day = data_ready3()

# User Engagement Metrics
st.header('User Engagement Metrics: Daily New Users and Average Event Duration')

# Calculate login counts per dayƒ
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

# Plot for login counts
fig_login = px.line(
    filtered_login_counts, 
    x='login_date', 
    y='user_count', 
    title='Number of Users Registered Per Day',
    line_shape='spline',  
    markers=True  
)

fig_login.update_traces(
    line=dict(color='rgba(0, 0, 139, 0.8)'),  # Warna biru dongker
    marker=dict(color='rgba(0, 0, 139, 0.8)', size=5)  # Warna biru dongker
)

fig_login.update_layout(
    xaxis_title='Date',
    yaxis_title='Number of Users',
    plot_bgcolor='rgba(255, 255, 255, 0.9)',  # Warna latar belakang putih pastel
    paper_bgcolor='rgba(240, 240, 240, 0.9)'  # Warna latar belakang kertas abu-abu muda pastel
)

# Plot for average time per session
fig_avg_time = px.line(
    filtered_avg_time,
    x='date',
    y='total_sec_taken',
    title='Average Time Spent per Event Per Day',
    line_shape='spline', 
    markers=True  
)

fig_avg_time.update_traces(
    line=dict(color='rgba(0, 0, 139, 0.8)'),  # Warna biru dongker
    marker=dict(color='rgba(0, 0, 139, 0.8)', size=5)  # Warna biru dongker
)

fig_avg_time.update_layout(
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


# Filter out students with more than zero activities
merged_df = merged_df[merged_df['num_activities'] > 100]

st.header('10 Top Outstanding Students')

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
df_rank_rating = df_group.nlargest(10, 'average_rating').sort_values(by='average_rating', ascending=False)
df_rank_attempt = df_group.nlargest(10, 'attempt_count').sort_values(by='attempt_count', ascending=False)

# Define a custom color scale for blue gradient
blue_gradient = ['#B0E0E6', '#87CEEB', '#4682B4', '#4169E1', '#0000CD']

# Plot top 10 students by average rating
rank1, rank2 = st.columns(2)
with rank1:
    fig = px.bar(df_rank_rating, x='alias', y='average_rating', color='user_city',
                 title=f'Top 10 Highest Rated Students in {selected_city}',
                 labels={'alias': 'Student Names', 'average_rating': 'Average Rating'},
                 height=600,
                 )
    st.plotly_chart(fig, use_container_width=True)

# Plot top 10 students by attempt count
with rank2:
    fig = px.bar(df_rank_attempt, x='alias', y='attempt_count', color='user_city',
                 title=f'Top 10 Most Active Students in {selected_city}',
                 labels={'alias': 'Student Names', 'attempt_count': 'Attempt Count'},
                 height=600,)
                #  color_discrete_sequence=blue_gradient)
    st.plotly_chart(fig, use_container_width=True)


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

# Calculate retention rates
cohort_size = cohort_pivot.iloc[:, 0]
retention_matrix = cohort_pivot.divide(cohort_size, axis=0).round(4) * 100

# Define a custom color scale for softer blue gradient
blue_white_colorscale = [
    [0.0, 'rgba(173, 216, 230, 0.1)'],  # Very light blue
    [0.5, 'rgba(173, 216, 230, 0.5)'],  # Light blue
    [1.0, 'rgba(0, 0, 255, 1)']         # Blue
]

# Visualize the cohort
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
    height=800  # Adjust the height of the heatmap
)
st.plotly_chart(fig, use_container_width=True)