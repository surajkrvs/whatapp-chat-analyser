import streamlit as st
import preprocessor  # Ensure this module exists and has a preprocess function
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import emoji
import re
from nltk.corpus import stopwords
import nltk

# Download NLTK stopwords
nltk.download('stopwords')


# Function to get the most common words
def get_most_common_words(messages, num=10):
    f = open('stop_hinglish.txt', 'r')
    stopwords_custom = f.read()

    # Join all the messages into a single text
    words = ' '.join(messages)

    # Remove non-alphabetic characters
    words = re.sub(r'[^A-Za-z\s]', '', words.lower())

    # Tokenize the words and remove stopwords
    words = words.split()
    filtered_words = [word for word in words if word not in stopwords_custom]

    # Use Counter to count the frequency of each word
    word_counts = Counter(filtered_words)

    # Get the 'num' most common words
    return word_counts.most_common(num)


# Function to extract emojis from messages
def extract_emojis(messages):
    emojis = []
    for message in messages:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])
    return emojis


# Function to analyze timeline
def timeline_analysis(df):
    df['date'] = pd.to_datetime(df['date'])  # Ensure 'date' column is in datetime format
    # Group by day and count the number of messages per day
    daily_timeline = df.groupby(df['date'].dt.date).size().reset_index(name='message_count')

    # Plot the daily timeline
    st.title("Daily Timeline")
    st.line_chart(daily_timeline.set_index('date'))

    # Group by month-year and count the number of messages per month
    monthly_timeline = df.groupby(df['date'].dt.to_period('M')).size().reset_index(name='message_count')

    # Convert Period to datetime for plotting
    monthly_timeline['date'] = monthly_timeline['date'].dt.to_timestamp()

    # Plot the monthly timeline
    st.title("Monthly Timeline")
    st.line_chart(monthly_timeline.set_index('date'))


st.sidebar.title("Whatsapp Chat Analyzer")

# Upload file from the sidebar
uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    # Read the uploaded file as a string
    file_content = uploaded_file.getvalue().decode("utf-8")

    # Display the raw file content in a text area
    st.text_area("Raw Chat Data", file_content, height=300)

    # Call the preprocess function from the preprocessor module
    df = preprocessor.preprocess(file_content)

    # Display the preprocessed DataFrame
    st.dataframe(df)

    # Fetch unique users
    user_list = df['user'].unique().tolist()

    # Remove "group_notification" if present
    if "group_notification" in user_list:
        user_list.remove("group_notification")

    # Sort users alphabetically
    user_list.sort()

    # Add "Overall" at the beginning of the list
    user_list.insert(0, "Overall")

    # Sidebar selectbox for choosing analysis by user
    selected_user = st.sidebar.selectbox("Show analysis with respect to", user_list)

    # Add button for analysis
    if st.sidebar.button("Show Analysis"):
        # Filter the DataFrame based on the selected user
        if selected_user == "Overall":
            # Show overall stats (all users)
            filtered_df = df
        else:
            # Filter messages by the selected user
            filtered_df = df[df['user'] == selected_user]

        # Timeline analysis
        timeline_analysis(filtered_df)

        # Create columns for displaying stats
        col1, col2, col3, col4 = st.columns(4)

        # Example content in the first column (Total Messages)
        with col1:
            st.header('Total Messages')
            total_messages = len(filtered_df)  # Number of messages sent by the selected user
            st.subheader(total_messages)

        # Total Words sent by the selected user
        with col2:
            st.header('Total Words')
            total_words = filtered_df['message'].apply(lambda x: len(x.split())).sum()
            st.subheader(total_words)

        # Media shared by the selected user
        with col3:
            st.header('Media Shared')
            media_messages = filtered_df[filtered_df['message'] == '<Media omitted>']  # Adjust based on your data
            st.subheader(len(media_messages))

        # Links shared by the selected user
        with col4:
            st.header('Links Shared')
            links_shared = filtered_df['message'].str.contains('http').sum()
            st.subheader(links_shared)

        # Display most common words
        st.title("Most Common Words")
        most_common_words = get_most_common_words(filtered_df['message'], num=10)

        # Display the most common words as a table
        st.write(pd.DataFrame(most_common_words, columns=['Word', 'Count']))

        # WordCloud generation
        st.title('WordCloud')
        words = ' '.join(filtered_df['message'].tolist())

        # Generate wordcloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(words)

        # Display the WordCloud using matplotlib
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")  # Hide axis
        st.pyplot(fig)

        # Extract and display emojis
        st.title('Emoji Analysis')
        emojis = extract_emojis(filtered_df['message'])

        if emojis:
            emoji_counts = Counter(emojis)
            common_emojis = emoji_counts.most_common(10)

            # Display the most common emojis as a table
            st.write(pd.DataFrame(common_emojis, columns=['Emoji', 'Count']))

            # Display emojis in WordCloud
            emoji_cloud = ' '.join(emojis)
            emoji_wordcloud = WordCloud(width=800, height=400, background_color='white').generate(emoji_cloud)

            fig, ax = plt.subplots()
            ax.imshow(emoji_wordcloud, interpolation='bilinear')
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.write("No emojis found.")
