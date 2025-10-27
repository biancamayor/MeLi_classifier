from src.bertimbau_classifier import SentimentClassifier
import pandas as pd

def infer_comment_class(csv_path:str):
    classifier = SentimentClassifier()

    df = pd.read_csv(csv_path, sep='█')
    df=df.replace(df.columns, ['rating', 'date','comment','product_name'])
    product_title = df['product_name']
    df=df[['comment', 'rating']]
    
    positives = 0
    negatives=[]
    scores=[]

    for n_comment, comment in df.iterrows():
        text=comment['comment']
        rating = comment['rating']

        if text not in ('Nan', 'nan', 'None', None) and not pd.isna(text):
            result=classifier.predict(text=text, rating=rating)
            score = result['score']
            scores.append(score) 

            if result["label"] == "POSITIVE" and result['score'] >= 0.7:
                positives += 1
            else:
                negatives.append(text)

    total_comments = len(df)
    positives_percent = (positives / total_comments) * 100 if total_comments != 0 else 0
    confidence_avg = sum(scores) / len(scores) if len(scores) != 0 else 0  
    
    return {'positives_percent':positives_percent, 
            'product_name':product_title.iloc[0], 
            'confidence':confidence_avg, 
            'negatives':negatives, 
            'total_comments':total_comments}


if __name__ == "__main__":
    infer_comment_class('data/reviews.csv')