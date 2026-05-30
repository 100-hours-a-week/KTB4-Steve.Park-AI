
# Pandas 미니퀘스트 모음 (기본 + 데이터 변환)
import pandas as pd
import numpy as np
from utils.utils import printanswer

df = pd.read_csv("data/metacritic_Toppc_games.csv")
df['Score'] = df['Score'].str.split().str[0].astype(float)

dfscoremean = df.groupby('Rating')['Score'].mean()
dfscoremax = df.groupby('Rating')['Score'].max()
dfscoremin = df.groupby('Rating')['Score'].min()

dffiltered = df[df['Score'] <= 30] 

print("")
print("PC Game Data Source From Kaggle For Pandas Quest:")
print(f"Top Pc Games Score Max:\n{dfscoremax}")
print(f"Top Pc Games Score Min:\n{dfscoremin}")
print(f"Top Pc Games Score Mean:\n{dfscoremean}")

print()
print("Top Pc Games Scores Under 30:")
print(dffiltered)

print("")