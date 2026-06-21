import os
# Suppress the oneDNN optimization messages
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# math 
import math

# data
import numpy as np
import pandas as pd

# machine learning
import keras
import ml_edu.experiment
import ml_edu.results

# data visualization
import plotly.express as px
TF_ENABLE_ONEDNN_OPTS=0
house_prices_data = pd.read_csv("Data/train.csv")
training_df = house_prices_data.loc[:, ("OverallQual", "GrLivArea", "1stFlrSF", "GarageArea", "Neighborhood", "SalePrice")]
print(training_df.describe(include='all'))


answer = '''
What is the maximum sale price?                         Answer: $755000.00
What is the mean ground live area across all houses?    Answer: 1515.4637 sq ft
How many neighborhoods are in the dataset?              Answer: 25
What is the most frequent overall quality number?       Answer: 5
Are any features missing data?                          Answer: No
'''

# 1. What is the maximum sale price?
max_sale_price = training_df['SalePrice'].max()
print("What is the maximum SalePrice?                  Answer: ${price:.2f}".format(price = max_sale_price))

# 2. What is the mean ground live area across all houses? (Đã sửa chữ 'trips/miles' thành 'GrLivArea/sq ft')
mean_ground_live_area = training_df['GrLivArea'].mean()
print("What is the mean ground live area?              Answer: {mean:.4f} sq ft".format(mean = mean_ground_live_area))

# 3. How many neighborhoods are in the dataset?
num_unique_neighborhood = training_df['Neighborhood'].nunique()
print("How many neighborhoods are in the dataset?       Answer: {number}".format(number = num_unique_neighborhood))

# 4. What is the most frequent overall quality number? (Tìm giá trị xuất hiện nhiều nhất - Mode)
most_freq_overall_qual = training_df['OverallQual'].value_counts().idxmax()
print("What is the most frequent overall quality?       Answer: {qual}".format(qual = most_freq_overall_qual))

# 5. Are any features missing data trong training_df?
# (Hàm này sẽ tự động in ra Yes nếu có bất kỳ ô nào bị trống)
missing_values = training_df.isnull().sum().sum()
print("Are any features missing data?                  Answer:", "No" if missing_values == 0 else "Yes")

training_df.corr(numeric_only = True)



fig = px.box(
    training_df, 
    x="OverallQual",      # Categorical axis
    y="SalePrice",             # Numeric axis
    color="OverallQual",  # Color code individual groups
    title="Interactive House Price Distribution by Neighborhood"
)

# Show the interactive plot
fig.show()
#@title Code - Process dataset 
# 1. Target Encoding for the 'Neighborhood' categorical feature:
# Replace each neighborhood name with the mean 'SalePrice' of that specific neighborhood.
# This converts a text-based categorical variable into a meaningful numerical feature for the model.
training_df["Neighborhood"] = training_df.groupby("Neighborhood")["SalePrice"].transform("mean")


# 2. Calculate descriptive statistics for normalization:
# - Find the mean of all numeric columns
feature_mean = training_df.mean(numeric_only=True)
# - Find the standard deviation (std) of all numeric columns
feature_std = training_df.std(numeric_only=True)

# 3. Extract the names of all columns that contain numeric data types
numerical_features = training_df.select_dtypes('number').columns

# 4. Perform Z-score Standardization:
# Formula: z = (x - mean) / std
# This scales all numerical features to have a mean of 0 and a standard deviation of 1.
normalized_dataset = (
    training_df[numerical_features] - feature_mean
) / feature_std

# 5. Update the original DataFrame with the newly normalized values
training_df[numerical_features] = normalized_dataset

# 6. Display the first 200 rows of the processed dataset to inspect the results
normalized_dataset.head(200)
# @title Define the functions that create and train a model.


def create_model(
    settings: ml_edu.experiment.ExperimentSettings,
    metrics: list[keras.metrics.Metric],
) -> keras.Model:
  """Create and compile a simple classification model."""
  model_inputs = [
      keras.Input(name=feature, shape=(1,))
      for feature in settings.input_features
  ]
  # Use a Concatenate layer to assemble the different inputs into a single
  # tensor which will be given as input to the Dense layer.
  # For example: [input_1[0][0], input_2[0][0]]

  concatenated_inputs = keras.layers.Concatenate()(model_inputs)
  model_output = keras.layers.Dense(
      units=1, name='dense_layer', activation=keras.activations.sigmoid
  )(concatenated_inputs)
  model = keras.Model(inputs=model_inputs, outputs=model_output)
  # Call the compile method to transform the layers into a model that
  # Keras can execute.  Notice that we're using a different loss
  # function for classification than for regression.
  model.compile(
      optimizer=keras.optimizers.RMSprop(
          settings.learning_rate
      ),
      loss=keras.losses.BinaryCrossentropy(),
      metrics=metrics,
  )
  return model


def train_model(
    experiment_name: str,
    model: keras.Model,
    dataset: pd.DataFrame,
    labels: np.ndarray,
    settings: ml_edu.experiment.ExperimentSettings,
) -> ml_edu.experiment.Experiment:
  """Feed a dataset into the model in order to train it."""

  # The x parameter of keras.Model.fit can be a list of arrays, where
  # each array contains the data for one feature.
  features = {
      feature_name: np.array(dataset[feature_name])
      for feature_name in settings.input_features
  }

  history = model.fit(
      x=features,
      y=labels,
      batch_size=settings.batch_size,
      epochs=settings.number_epochs,
  )

  return ml_edu.experiment.Experiment(
      name=experiment_name,
      settings=settings,
      model=model,
      epochs=history.epoch,
      metrics_history=pd.DataFrame(history.history),
  )


print('Defined the create_model and train_model functions.')

# Let's define our first experiment settings.
settings = ml_edu.experiment.ExperimentSettings(
    learning_rate=0.001,
    number_epochs=60,
    batch_size=100,
    classification_threshold=0.35,
    input_features=input_features,
)

metrics = [
    keras.metrics.BinaryAccuracy(
        name='accuracy', threshold=settings.classification_threshold
    ),
    keras.metrics.Precision(
        name='precision', thresholds=settings.classification_threshold
    ),
    keras.metrics.Recall(
        name='recall', thresholds=settings.classification_threshold
    ),
    keras.metrics.AUC(num_thresholds=100, name='auc'),
]

# Establish the model's topography.
model = create_model(settings, metrics)

# Train the model on the training set.
experiment = train_model(
    'baseline', model, train_features, train_labels, settings
)

# Plot metrics vs. epochs
ml_edu.results.plot_experiment_metrics(experiment, ['accuracy', 'precision', 'recall'])
ml_edu.results.plot_experiment_metrics(experiment, ['auc'])