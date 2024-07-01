# Import dependencies.
import streamlit as st
import redis
import pandas as pd
import altair as alt


# Set page configuration.
st.set_page_config(page_title='Looker webpage dashboard', page_icon=None, layout='wide', initial_sidebar_state='expanded')

# Connect to Redis.
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Dashboard title.
st.title("Events Information Dashboard")

# Function to load data from CSV.
@st.cache_data
def load_cache_data():
    data = pd.read_csv('events.csv')
    # Store data in redis.
    store_data(data)
    return data

# Function to store data in Redis.
def store_data(data, batch_size=100000):
    # Convert DataFrame to dictionary.
    data_dict = data.to_dict(orient='records')
    # Split data into batches.
    for i in range(0, len(data_dict), batch_size):
        batch = data_dict[i:i + batch_size]
        with redis_client.pipeline() as pipe:
            for record in batch:
                # Store each record in Redis hash.
                pipe.hmset(f"user:{record['id']}", record)
            pipe.execute()

# Function to retrieve data from Redis.
def get_data():
    data = []
    # Retrieve all keys matching 'user:*'.
    keys = redis_client.keys("user:*")
    for key in keys:
        # Retrieve data for each user and append to list.
        data.append(redis_client.hgetall(key))
    return pd.DataFrame(data)

# Function to filter data based on selected year.
def filter_data(data, selected_year):
    if selected_year == 'All Years':
        data = data.copy()
        return data
    else:
        return data[data['year'] == selected_year]

# Read the data.
with st.spinner("Loading data & visualizations..."):
    events_data = load_cache_data()

# setting up a side bar.
with st.sidebar:
    #  Sidebar title.
    st.title('Looker ecommerce website dashboard')
    # Option to select all years.
    year_list = ['All Years'] + sorted(events_data['year'].unique())
    # Select years from the data.
    selected_year = st.selectbox('Select a year', year_list, index=0)  # Set index to 0 for "All Years"
    # Filter data based on the selected year.
    data_year_selected = filter_data(events_data, selected_year)
    # Select a color theme.
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

# COLUMN 1.
# Faceted plot for time period and the event.
def make_faceted_plot(input_df, y_column, faceting_column, selected_color_scheme):
    # Create a custom color scheme based on the selected theme.
    if selected_color_scheme == 'blues':
        color_scheme = alt.Scale(scheme='blues')
    elif selected_color_scheme == 'cividis':
        color_scheme = alt.Scale(scheme='cividis')
    elif selected_color_scheme == 'greens':
        color_scheme = alt.Scale(scheme='greens')
    elif selected_color_scheme == 'inferno':
        color_scheme = alt.Scale(scheme='inferno')
    elif selected_color_scheme == 'magma':
        color_scheme = alt.Scale(scheme='magma')
    elif selected_color_scheme == 'plasma':
        color_scheme = alt.Scale(scheme='plasma')
    elif selected_color_scheme == 'reds':
        color_scheme = alt.Scale(scheme='reds')
    elif selected_color_scheme == 'rainbow':
        color_scheme = alt.Scale(scheme='rainbow')
    elif selected_color_scheme == 'turbo':
        color_scheme = alt.Scale(scheme='turbo')
    elif selected_color_scheme == 'viridis':
        color_scheme = alt.Scale(scheme='viridis')

    # Create an interactive faceted bar chart.
    chart = alt.Chart(input_df).mark_bar().encode(
        x=alt.X('count()', axis=alt.Axis(title='Event Count')),
        y=alt.Y(y_column, axis=alt.Axis(title='Event Type')),
        color=alt.Color(y_column, scale=color_scheme),
        tooltip=[y_column, alt.Tooltip('count()', title='Event Count')]
    ).properties(
        width=180,
        height=150
    ).facet(
        facet=alt.Facet(faceting_column, title=None),
        columns=1
    ).interactive()

    return chart


# COLUMN 2.
# A line plot of traffic sources over time.
def line_plot(input_df, x_column, y_column, selected_color_scheme):
    # Group by 'year', 'month', and 'traffic_source', and count the records.
    traffic_counts = input_df.groupby([x_column, y_column]).size().unstack(fill_value=0).reset_index()
    # Melt the dataframe to have each traffic source as a separate row
    traffic_counts_melted = pd.melt(traffic_counts, id_vars=[x_column], value_vars=list(traffic_counts.columns[1:]),
                                    var_name=y_column, value_name='Count')
    # Create a custom color scheme based on the selected theme.
    if selected_color_scheme == 'blues':
        color_scheme = alt.Scale(scheme='blues')
    elif selected_color_scheme == 'cividis':
        color_scheme = alt.Scale(scheme='cividis')
    elif selected_color_scheme == 'greens':
        color_scheme = alt.Scale(scheme='greens')
    elif selected_color_scheme == 'inferno':
        color_scheme = alt.Scale(scheme='inferno')
    elif selected_color_scheme == 'magma':
        color_scheme = alt.Scale(scheme='magma')
    elif selected_color_scheme == 'plasma':
        color_scheme = alt.Scale(scheme='plasma')
    elif selected_color_scheme == 'reds':
        color_scheme = alt.Scale(scheme='reds')
    elif selected_color_scheme == 'rainbow':
        color_scheme = alt.Scale(scheme='rainbow')
    elif selected_color_scheme == 'turbo':
        color_scheme = alt.Scale(scheme='turbo')
    elif selected_color_scheme == 'viridis':
        color_scheme = alt.Scale(scheme='viridis')

    # Create a line chart.
    line_chart = alt.Chart(traffic_counts_melted).mark_line().encode(
        x=alt.X(x_column, type='ordinal', axis=alt.Axis(labelAngle=-45)),
        y='Count',
        color=alt.Color(y_column, scale=color_scheme),
        tooltip=[x_column, 'Count']
    )
    # Create a scatter plot for dots.
    scatter_chart = alt.Chart(traffic_counts_melted).mark_circle(color='black').encode(
        x=alt.X(x_column, type='ordinal'),
        y='Count',
        size=alt.value(50)  # Size of dots
    )
    # Combine line chart and scatter plot.
    chart = (line_chart + scatter_chart).properties(
        width=700,
        height=350
    ).interactive()

    return chart


# count plot of the traffic and browser.
def count_plot(input_df, x_column, hue_column, selected_color_scheme):
    # Create a custom color scheme based on the selected theme.
    if selected_color_scheme == 'blues':
        color_scheme = alt.Scale(scheme='blues')
    elif selected_color_scheme == 'cividis':
        color_scheme = alt.Scale(scheme='cividis')
    elif selected_color_scheme == 'greens':
        color_scheme = alt.Scale(scheme='greens')
    elif selected_color_scheme == 'inferno':
        color_scheme = alt.Scale(scheme='inferno')
    elif selected_color_scheme == 'magma':
        color_scheme = alt.Scale(scheme='magma')
    elif selected_color_scheme == 'plasma':
        color_scheme = alt.Scale(scheme='plasma')
    elif selected_color_scheme == 'reds':
        color_scheme = alt.Scale(scheme='reds')
    elif selected_color_scheme == 'rainbow':
        color_scheme = alt.Scale(scheme='rainbow')
    elif selected_color_scheme == 'turbo':
        color_scheme = alt.Scale(scheme='turbo')
    elif selected_color_scheme == 'viridis':
        color_scheme = alt.Scale(scheme='viridis')

    # Create an interactive count plot using Altair with custom color scheme.
    chart = alt.Chart(input_df).mark_bar().encode(
        x=alt.X(x_column, axis=alt.Axis(title='Traffic source')),
        y=alt.Y('count()', axis=alt.Axis(title='Count')),
        color=alt.Color(hue_column, scale=color_scheme),
        tooltip=[x_column, alt.Tooltip('count()', title='Count')]
    ).properties(
        width=700,
        height=350
    ).interactive()

    return chart

# Data cards.
def highest_count_summary(input_df):
    # Group by 'year', 'event_type', 'traffic_source', and 'browser', and count the records.
    summary_df = input_df.groupby(['year', 'event_type', 'traffic_source', 'browser']).size().reset_index()
    summary_df.columns = ['year', 'event_type', 'traffic_source', 'browser', 'count']
    # Get the rows with the highest count for each year.
    summary_df = summary_df.loc[summary_df.groupby('year')['count'].idxmax()]
    # Reset index and rename columns.
    summary_df.reset_index(drop=True, inplace=True)
    summary_df.rename(columns={'event_type': 'highest_count_event_type',
                               'traffic_source': 'highest_count_traffic_source',
                               'browser': 'highest_count_browser'
                               }, inplace=True)
    # Drop the 'count' column.
    summary_df.drop(columns=['count'], inplace=True)

    return summary_df


# COLUMN 3.
# Text boxes to display the unique visitors of different pages.
def display_unique_visitors(input_df, column_name):
    # counting the number of unique visitors in each event type.
    events = {}
    for i in input_df[column_name].unique():
        temp_df = input_df[input_df['event_type'] == i]

        unique_visitors_event_type = temp_df['ip_address'].nunique() 
        events[i] = unique_visitors_event_type
    # Define box colors based on selected color theme.
    box_colors = {
        'blues': '#1f77b4',
        'cividis': '#d9c55c',
        'greens': '#50c878',
        'inferno': '#fac228',
        'magma': '#f8765c',
        'plasma': '#febd2a',
        'reds': '#e97451',
        'rainbow': '#ff6d38',
        'turbo': '#1bd0d5',
        'viridis': '#1fa187'
    }

    # Get the selected color for the boxes.
    # Default color if not found.
    selected_color = box_colors.get(selected_color_theme, '#1f77b4') 
    # CSS styling for the box.
    box_style = f"""
        background-color: {selected_color};
        padding: 5px;
        border-radius: 15px;
        color: white;
        margin-bottom: 10px; 
        text-align: center;
        font-size: larger;
    """

    for event, unique_value in events.items():
        subheader_style = "font-size: small;"
        # Text for the boxes with line breaks.
        text_box = f"{event}<br>{unique_value}"
        # Render the boxes with text.
        st.write(f'<div style="{box_style}">{text_box}</div>', unsafe_allow_html=True)


# Pie chart of the distribution of the traffic sources.
def make_pie_chart(input_df, input_column, selected_color_theme):
    # Create a DataFrame with counts of each country.
    traffic_counts = input_df[input_column].value_counts().reset_index()
    traffic_counts.columns = ['traffic_source', 'Count']

    # Create a custom color scheme based on the selected theme.
    if selected_color_theme == 'blues':
        color_scheme = alt.Scale(scheme='blues')
    elif selected_color_theme == 'cividis':
        color_scheme = alt.Scale(scheme='cividis')
    elif selected_color_theme == 'greens':
        color_scheme = alt.Scale(scheme='greens')
    elif selected_color_theme == 'inferno':
        color_scheme = alt.Scale(scheme='inferno')
    elif selected_color_theme == 'magma':
        color_scheme = alt.Scale(scheme='magma')
    elif selected_color_theme == 'plasma':
        color_scheme = alt.Scale(scheme='plasma')
    elif selected_color_theme == 'reds':
        color_scheme = alt.Scale(scheme='reds')
    elif selected_color_theme == 'rainbow':
        color_scheme = alt.Scale(scheme='rainbow')
    elif selected_color_theme == 'turbo':
        color_scheme = alt.Scale(scheme='turbo')
    elif selected_color_theme == 'viridis':
        color_scheme = alt.Scale(scheme='viridis')
    # Create an interactive pie chart using Altair with custom color scheme.
    chart = alt.Chart(traffic_counts).mark_arc().encode(
        color=alt.Color('traffic_source', scale=color_scheme),
        tooltip=['traffic_source', 'Count'],
        theta='Count:Q',
        radius=alt.value(70)
    ).properties(
        width=250,
        height=200
    ).interactive()

    return chart



# APP LAYOUT.
# Creating columns (3 columns.
col = st.columns((2.2, 4.0, 1.4), gap='medium')

with col[0]:
    st.markdown("#### Events over time")
    faceted_plot = make_faceted_plot(data_year_selected, 'event_type', 'time_period', selected_color_theme)
    st.altair_chart(faceted_plot)

with col[1]:
    st.markdown('#### Trend of events over years')
    altair_count_plot = line_plot(data_year_selected, 'year', 'event_type', selected_color_theme)
    st.altair_chart(altair_count_plot)

    st.divider()

    st.markdown('#### Traffic source and browser')
    count_plot_time = count_plot(data_year_selected, 'traffic_source', 'browser', selected_color_theme)
    st.altair_chart(count_plot_time)

    # st.divider()

    # st.markdown('##### Highest statistics')
    # highest_count = highest_count_summary(data_year_selected)
    # # st.table(highest_count.style.set_table_styles([{'selector': 'table', 'props': [('width', '350px')]}]))
    # st.write(highest_count, height=250)
    

with col[2]:
    st.markdown('#### Unique visitors')
    display_unique_visitors(data_year_selected, 'event_type')

    st.divider()

    st.markdown('#### Traffic sources')
    pie_chart = make_pie_chart(data_year_selected, 'traffic_source', selected_color_theme)
    st.write(pie_chart)

    