import datetime as dt
import streamlit as st 
import pandas as pd

class DataAnalisis:
    def __init__(self, df):
        self.df = df

    def create_daily_orders_df(self):
        daily_orders_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "order_id": "nunique",
            "payment_value": "sum"
        })
        daily_orders_df = daily_orders_df.reset_index()
        daily_orders_df.rename(columns={
            "order_id": "order_count",
            "payment_value": "revenue"
        }, inplace=True)
        
        return daily_orders_df
    
    def create_sum_spend_df(self):
        sum_spend_df = self.df.resample(rule='D', on='order_approved_at').agg({
            "payment_value": "sum"
        })
        sum_spend_df = sum_spend_df.reset_index()
        sum_spend_df.rename(columns={
            "payment_value": "total_spend"
        }, inplace=True)

        return sum_spend_df

    def create_sum_order_items_df(self):
        sum_order_items_df = self.df.groupby("product_category_name_english")["product_id"].count().reset_index()
        sum_order_items_df.rename(columns={
            "product_id": "product_count"
        }, inplace=True)
        sum_order_items_df = sum_order_items_df.sort_values(by='product_count', ascending=False)

        return sum_order_items_df

    def review_score_df(self):
        review_scores = self.df['review_score'].value_counts().sort_values(ascending=False)
        most_common_score = review_scores.idxmax()

        return review_scores, most_common_score

    def create_customer_city_df(self):
        city_counts = self.df['customer_city'].value_counts().reset_index()
        city_counts.columns = ['city', 'customer_count']
        city_counts = city_counts.sort_values(by='customer_count', ascending=False)

        return city_counts

    def create_customer_state_df(self):
        state_counts = self.df['customer_state'].value_counts().reset_index()
        state_counts.columns = ['state', 'customer_count']
        state_counts = state_counts.sort_values(by='customer_count', ascending=False)

        return state_counts
    

    def create_rfm_df(self):
        # Ensure that 'order_approved_at' column is datetime
        self.df['order_approved_at'] = pd.to_datetime(self.df['order_approved_at'])

        # Define snapshot date (the date when you are performing the analysis)
        snapshot_date = self.df['order_approved_at'].max() + pd.DateOffset(days=1)
        
        # Calculate Recency, Frequency, and Monetary for each customer
        rfm_df = self.df.groupby('customer_id').agg({
            'order_approved_at': lambda x: (snapshot_date - x.max()).days, # Recency
            'order_id': 'count',  # Frequency
            'payment_value': 'sum' # Monetary
        }).reset_index()
        
        # Rename columns
        rfm_df.rename(columns={
            'order_approved_at': 'Recency',
            'order_id': 'Frequency',
            'payment_value': 'Monetary'
        }, inplace=True)
        
        # Convert Monetary to float for consistency
        rfm_df['Monetary'] = rfm_df['Monetary'].astype(float)

        return rfm_df
    
  
    
