import base64
import os

import altair as alt
import cv2
import numpy as np
import pandas as pd
from altair import Tooltip
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from src.common.charts import display_chart
from src.common.logger import get_logger


logger = get_logger(__name__)


def cluster_images(images: list, n_clusters=5):
    X = np.array(images)
    X = X.reshape(X.shape[0], -1)

    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(X)

    return kmeans.labels_


def reduce_features(images: list, n_components=2):
    # Perform dimensionality reduction for plotting
    flattened_images = np.array(images).reshape(len(images), -1)
    pca = PCA(n_components=n_components)
    return pca.fit_transform(flattened_images)


def plot_image_clusters(project_id: str, title: str, filenames: list, images: list, cluster_labels, reduced_features):
    # Verify lengths of arrays
    assert len(filenames) == len(images) == len(cluster_labels), "Array lengths do not match"

    # Create a DataFrame with reduced features, cluster labels, and filenames
    filenames = [os.path.basename(filenames[i]) for i in range(len(filenames))]
    df = pd.DataFrame(
        {'PC1': reduced_features[:, 0], 'PC2': reduced_features[:, 1], 'Cluster': cluster_labels, 'Filename': filenames})

    # Generate thumbnail images and encode them as base64
    thumbnail_images = [cv2.resize(img, (100, 100)) for img in images]
    encoded_images = [base64.b64encode(cv2.imencode('.png', img)[1]).decode() for img in thumbnail_images]

    # Add base64 encoded images to the DataFrame
    df['Thumbnail'] = encoded_images

    # Create Altair scatter plot
    scatter_plot = alt.Chart(df).mark_circle(size=60).encode(
        x='PC1',
        y='PC2',
        color=alt.Color('Cluster:N', scale=alt.Scale(scheme='category10')),
        tooltip=[
            Tooltip('Filename', title='Filename'),
            Tooltip('Cluster', title='Cluster')
        ]
    )

    # make the chart interactive
    chart_image_clusters = scatter_plot.interactive()
    chart_image_clusters = chart_image_clusters.properties(
        width=600,
        height=400
    ).add_selection(
        alt.selection_interval(bind='scales', encodings=['x', 'y'])
    ).add_selection(
        alt.selection(type='interval', bind='scales', encodings=['x', 'y'])
    )

    if chart_image_clusters:
        display_chart(project_id, title, chart_image_clusters)
