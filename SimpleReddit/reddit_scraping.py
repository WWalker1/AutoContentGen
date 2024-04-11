import praw
import pandas as pd

'''
Params: 
1. subreddit -> subreddit that it will pull posts from
2. num_posts -> the number of posts that the function will retrieve
Returns: dataframe of the hottest posts from the subreddit
'''
def pull_posts(subreddit_name, num_posts): 

    # Initialize the Reddit instance
    reddit = praw.Reddit(client_id='VkuHzBrorLCQGKh3gOnKdA',
                        client_secret='MmXgUMTPjtJtKJqyGUhkqaPyIC3NgA',
                        user_agent='Platform:YTshorts:1.0 by Weston Walker')

    # Specify the subreddit you want to scrape
    subreddit = reddit.subreddit(subreddit_name)

    # Initialize lists to store the data
    data = []

    # Retrieve the posts from the subreddit
    for post in subreddit.hot(limit=num_posts):  # Adjust the limit as needed
        if (len(post.selftext) > 10):
            data.append({"Title": post.title, "Body": post.selftext})

    # Create a Pandas DataFrame
    df = pd.DataFrame(data)
    return df


print(pull_posts("relationship_advice", 10).iloc[0])

