# import dependencies.
import streamlit as st
import redis
import pandas as pd
import plotly.express as px
import altair as alt

# Set page configuration.
st.set_page_config(page_title='Looker webpage dashboard', page_icon=None, layout='wide', initial_sidebar_state='expanded')

# Dashboard title.
st.title("Users Information Dashboard")

# Connect to Redis.
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Function to load data from CSV.
@st.cache_data
def load_cache_data():
    data = pd.read_csv('users.csv')
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
        # Select all years.
        return data.copy()  
    else:
        return data[data['year'] == selected_year]


# load the data to the variable data.
with st.spinner("Loading data & plots..."):
    # Load data.
    data = load_cache_data()


# setting up a side bar.
with st.sidebar:
    #  Sidebar title.
    st.title('Looker ecommerce website dashboard')
    # Option to select all years.
    year_list = ['All Years'] + sorted(data['year'].unique())
    # Select years from the data.
    selected_year = st.selectbox('Select a year', year_list, index=0)  # Set index to 0 for "All Years"
    # Filter and cache data based on the selected year.
    data_year_selected = filter_data(data, selected_year)
    # Select color themes.
    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


# Function to calculate the total number of female and male users in each country.
def calculate_gender_counts(data):
    # Group by country and gender and count occurrences.
    gender_counts = data.groupby(['country', 'gender']).size().unstack().fillna(0)
    gender_counts['Female'] = gender_counts['F']
    gender_counts['Male'] = gender_counts['M']
    gender_counts = gender_counts[['Female', 'Male']]
    return gender_counts


# Function to display the highest female and male populations as cards.
def display_highest_population_cards(gender_counts, selected_color_theme):
    # Find the country with the highest female population.
    highest_female_country = gender_counts['Female'].idxmax()
    highest_female_population = gender_counts.loc[highest_female_country, 'Female']
    # Find the country with the highest male population.
    highest_male_country = gender_counts['Male'].idxmax()
    highest_male_population = gender_counts.loc[highest_male_country, 'Male']

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
    selected_color = box_colors.get(selected_color_theme, '#1f77b4')  # Default color if not found
    # CSS styling for the box.
    box_style = f"""
        background-color: {selected_color};
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin-bottom: 10px; 
        text-align: center;
        font-size: larger;
    """
    subheader_style = "font-size: small;"
    # Text for the boxes with line breaks.
    female_box_text = f"Female<br>{highest_female_country}<br>{highest_female_population}"
    male_box_text = f"Male<br>{highest_male_country}<br>{highest_male_population}"
    # Render the boxes with text.
    st.write(f'<div style="{box_style}">{female_box_text}</div>', unsafe_allow_html=True)
    st.write(f'<div style="{box_style}">{male_box_text}</div>', unsafe_allow_html=True)


# Make a choroplet map.
def make_choropleth(input_df, input_id, input_color_theme):
    # Calculate count of people for each country.
    count_by_country = input_df.groupby(input_id).size().reset_index(name='Count')
    # Create the choropleth map.
    choropleth = px.choropleth(count_by_country, 
                               locations=input_id, 
                               color='Count', 
                               locationmode="country names", 
                               color_continuous_scale=input_color_theme,
                               labels={'Count': "Count of People"}
                              )
    # Update layout settings.
    choropleth.update_layout(
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=0, r=0, t=0, b=0),
        height=300
    )

    return choropleth

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


# count plot of users of different traffic sources.
def make_count_plot(input_df, input_column, selected_color_theme):
    # Create a DataFrame with counts of each traffic source
    traffic_counts = input_df[input_column].value_counts().reset_index()
    traffic_counts.columns = ['Traffic Source', 'Count']
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
    # Create a bar chart.
    chart = alt.Chart(traffic_counts).mark_bar().encode(
        x='Traffic Source',
        y='Count',
        color=alt.Color('Traffic Source', scale=color_scheme),
        tooltip=['Traffic Source', 'Count']
    ).properties(
        width=550,
        height=400
    ).interactive()

    return chart

# Pie chart of the distribution of the countries.
def make_pie_chart(input_df, input_column, selected_color_theme):
    # Create a DataFrame with counts of each country.
    country_counts = input_df[input_column].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']
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
    chart = alt.Chart(country_counts).mark_arc().encode(
        color=alt.Color('Country', scale=color_scheme),
        tooltip=['Country', 'Count'],
        theta='Count:Q',
        radius=alt.value(130)
    ).properties(
        width=450,
        height=400
    ).interactive()

    return chart


# Making a bar plot.
def make_age_group_bar_plot(input_df, selected_color_theme):
    # Count occurrences of each age group
    age_group_counts = input_df['age_group'].value_counts().reset_index()
    age_group_counts.columns = ['Age Group', 'Count']
    # Interactive bar chart.
    chart = alt.Chart(age_group_counts).mark_bar().encode(
        x=alt.X('Age Group', title='Age Group'),
        y=alt.Y('Count', title='Count'),
        color=alt.Color('Age Group', scale=alt.Scale(scheme=selected_color_theme)),
        tooltip=['Age Group', 'Count']
    ).properties(
        width=450,
        height=300
    ).interactive()

    return chart



# APP LAYOUT.
# Creating columns (3 columns).
col = st.columns((1.4, 4.2, 2.4), gap='medium')

with col[0]:
     st.markdown('#### Maximum count')

     # Calculate gender counts.
     gender_counts = calculate_gender_counts(data_year_selected)

     # Display highest female and male populations.
     display_highest_population_cards(gender_counts, selected_color_theme)

     st.divider()

     st.markdown('#### Distribution in countries')
     st.write(gender_counts)


with col[1]:
    st.markdown('#### Total Users')
    choropleth = make_choropleth(data_year_selected, 'country', selected_color_theme)
    st.plotly_chart(choropleth, use_container_width=True)
    
    # Heat map to vsualize the average age
    # heatmap = make_heatmap(data_year_selected, 'year', 'country', 'age', selected_color_theme)
    # st.altair_chart(heatmap, use_container_width=True)

    st.divider()
    
    # Make count plot/
    st.markdown('#### Traffic sources')
    count_plot = make_count_plot(data_year_selected, 'traffic_source', selected_color_theme)
    st.write(count_plot)

with col[2]:
    st.markdown('#### Country distribution')
    # Make pie chart.
    pie_chart = make_pie_chart(data_year_selected, 'country', selected_color_theme)
    st.write(pie_chart)

    # Horizontal divider between plots.
    st.divider()

    # Make a count plot of age group,
    st.markdown('#### Age group')
    age_group_bar_plot = make_age_group_bar_plot(data_year_selected, selected_color_theme)
    st.write(age_group_bar_plot)

