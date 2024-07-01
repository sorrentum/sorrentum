# Import dependencies.
import streamlit as st
import redis
import pandas as pd
import altair as alt


# Set page configuration.
st.set_page_config(page_title='Looker webpage dashboard', page_icon=None, layout='wide', initial_sidebar_state='expanded')

# Dashboard title.
st.title("Inventory Information Dashboard")

# Connect to Redis.
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Function to load data from CSV.
@st.cache_data
def load_cache_data():
    data = pd.read_csv('inventory.csv')
    # Store data in redis.
    store_data(data)
    return data

# Function to store data in Redis.
def store_data(data, batch_size=10000):
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
        return data.copy()  # Select all years.
    else:
        return data[data['year'] == selected_year]
    
# Read the data.
with st.spinner("Loading data & visualizations..."):
    inventory_data = load_cache_data()

# setting up a side bar.
with st.sidebar:
    #  Add a title to the sidebar.
    st.title('Looker ecommerce website dashboard')
    # Add an option to select all years.
    year_list = ['All Years'] + sorted(inventory_data['year'].unique())
    # Select years from the data.
    selected_year = st.selectbox('Select a year', year_list, index=0) 
    # Filter and cache data based on the selected year.
    data_year_selected = filter_data(inventory_data, selected_year)
    # Select a color theme.
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


# COLUMN 1.
# Make a pie chart to display male and female products.
def make_pie_chart(input_df, input_column, selected_color_theme):
 # Create a DataFrame with counts of both the genders.
    gender_counts = input_df[input_column].value_counts().reset_index()
    gender_counts.columns = ['product_department', 'Count']
    # Create a custom color scheme based on the selected theme.
    color_scheme = alt.Scale(scheme=selected_color_theme)
    # Create an interactive pie chart using Altair with custom color scheme and legend on the left side.
    chart = alt.Chart(gender_counts).mark_arc().encode(
        color=alt.Color('product_department', scale=color_scheme, legend=alt.Legend(title=None, orient='left')),
        tooltip=['product_department', 'Count'],
        theta='Count:Q',
        radius=alt.value(80)
    ).properties(
        width=250,
        height=200
    ).interactive()

    return chart

# Function to display the highest count for each category.
def display_highest_category_counts(df, category, selected_color_theme):
    # Group by product_department and calculate count for each category.
    counts_by_gender = df.groupby('product_department')[category].value_counts()
    # Find the category with the highest count for each gender.
    highest_female_category = counts_by_gender['Women'].idxmax()
    highest_female_count = counts_by_gender['Women'].max()
    highest_male_category = counts_by_gender['Men'].idxmax()
    highest_male_count = counts_by_gender['Men'].max()

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
    selected_color = box_colors.get(selected_color_theme, '#1f77b4') 
    # CSS styling for the box.
    box_style = f"""
        background-color: {selected_color};
        padding: 10px;
        border-radius: 10px;
        color: white;
        margin-bottom: 10px; 
        text-align: center;
        font-size: 16px;
    """
    # Text for the boxes with line breaks.
    female_box_text = f"Female: {highest_female_category}<br>Male: {highest_male_category}"
    # Render the boxes with text.
    st.write(f'<div style="{box_style}">{female_box_text}</div>', unsafe_allow_html=True)


# COLUMN 2.
# A line plot of product categories over time.
def line_plot(input_df, x_column, y_column, selected_color_scheme):
    # Group by 'year', 'product category', and count the records.
    category_counts = input_df.groupby([x_column, y_column]).size().unstack(fill_value=0).reset_index()
    # Melt the dataframe to have each traffic source as a separate row.
    category_counts_melted = pd.melt(category_counts, id_vars=[x_column], value_vars=list(category_counts.columns[1:]),
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

    # Create a line chart using Altair with custom color scheme.
    line_chart = alt.Chart(category_counts_melted).mark_line().encode(
        x=alt.X(x_column, type='ordinal', axis=alt.Axis(labelAngle=-45)),
        y='Count',
        color=alt.Color(y_column, scale=color_scheme),
        tooltip=[x_column, 'Count']
    )
    # Create a scatter plot for dots.
    scatter_chart = alt.Chart(category_counts_melted).mark_circle(color='black').encode(
        x=alt.X(x_column, type='ordinal'),
        y='Count',
        size=alt.value(50)  
    )
    # Combine line chart and scatter plot.
    chart = (line_chart + scatter_chart).properties(
        width=750,
        height=300
    ).interactive()

    return chart

# Function to create an interactive bar plot of product categories.
def create_horizontal_bar_plot(input_df, color_scheme):
    # Group by product category and calculate counts.
    category_counts = input_df['product_category'].value_counts().reset_index()
    category_counts.columns = ['product_category', 'count']
    # Create the horizontal bar plot.
    bars = alt.Chart(category_counts).mark_bar().encode(
        y='product_category',
        x='count',
        color=alt.Color('product_category', scale=alt.Scale(scheme=color_scheme))
    ).properties(
        width=500,
        height=800
    ).interactive()

    return bars

# COLUMN 3.
def create_bubble_plot(df, color_scheme):
    # Group by product category and calculate counts.
    category_counts = df['product_category'].value_counts().reset_index()
    category_counts.columns = ['product_category', 'count']
    # Create the Altair bubble plot.
    bubble_plot = alt.Chart(category_counts).mark_circle().encode(
        x='product_category:N',
        y='count:Q',
        size='count:Q',
        color='product_category:N',
        tooltip=['product_category:N', 'count:Q']
    ).properties(
        width=800,
        height=380
    ).interactive()

    return bubble_plot


# Making a heat map.
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
        y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="Year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
        x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
        color=alt.Color(f'average({input_color}):Q', 
                        legend=None,
                        scale=alt.Scale(scheme=input_color_theme)),
        stroke=alt.value('black'),
        strokeWidth=alt.value(0.25),
    ).properties(width=0, height=300
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
    )
    
    return heatmap

# APP LAYOUT.
# Creating columns (3 columns).
col = st.columns((1.2, 4.1, 2.7), gap='medium')

with col[0]:

    # Cards to display mostly bought products.
    st.markdown('#### Maximum bought')
    st.markdown('###### Product Category')
    display_highest_category_counts(data_year_selected, 'product_category', selected_color_theme)
    st.markdown('###### Product Name')
    display_highest_category_counts(data_year_selected, 'product_name', selected_color_theme)
    st.markdown('###### Product Brand')
    display_highest_category_counts(data_year_selected, 'product_brand', selected_color_theme)

    st.divider()

    st.markdown('#### Gender distribution')
    pie_chart = make_pie_chart(data_year_selected, 'product_department', selected_color_theme)
    st.write(pie_chart)

with col[1]:

    st.markdown('#### Cost vs product categories')
    heatmap = make_heatmap(data_year_selected, 'year', 'product_category', 'cost', selected_color_theme)
    st.altair_chart(heatmap, use_container_width=True)

    st.divider()

    st.markdown('#### Trend of categories over years')
    altair_count_plot = line_plot(data_year_selected, 'year', 'product_category', selected_color_theme)
    st.altair_chart(altair_count_plot)
    

with col[2]:

    # Make count plot of product categories.
    st.markdown('#### Product categories')
    count_plot = create_horizontal_bar_plot(data_year_selected, selected_color_theme)
    st.write(count_plot)
    