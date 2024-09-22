import pandas as pd
import numpy as np
data = pd.read_csv('c:\subway_excel_data\월\subway_excel_data_2023-10-23.csv')
data = data.dropna()

y데이터 = data['color'].values

x데이터 = []

for i, rows in data.iterrows():
    x데이터.append([rows['day_of_week'],rows['time']])
import tensorflow as tf

model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(64,activation='tanh'),
    tf.keras.layers.Dense(128,activation='tanh'),
    tf.keras.layers.Dense(1,activation='linear'),
])

model.compile(optimizer='adam', loss='binary_crossentropy',metrics=['accuracy'])
model.fit(np.array(x데이터),np.array(y데이터), epochs =10)
new_data = np.array([[1, 1723]])
predictions = model.predict(new_data)
print(predictions)