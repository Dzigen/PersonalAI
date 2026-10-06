import sys
sys.path.insert(0, "../../../")

import json
from functools import reduce
from tqdm import tqdm
import os
from sklearn.decomposition import PCA
from sklearn.cluster import DBSCAN, HDBSCAN
import matplotlib.pyplot as plt
import hdbscan
import numpy as np
import matplotlib.pyplot as plt
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score, adjusted_rand_score
import umap
from collections import Counter, defaultdict
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import itertools
from scipy.spatial import distance

from src.agents import AgentDriver, AgentDriverConfig
from src.agents.utils import AgentConnectorConfig
from src.db_drivers.vector_driver.embedders import EmbedderModel, EmbedderModelConfig
from wordcloud import WordCloud

import gc
import torch

##########################################

PATH_TO_PREPARED_SETTINGS_DIR = sys.argv[1]
print(PATH_TO_PREPARED_SETTINGS_DIR)
settings_filnames = os.listdir(PATH_TO_PREPARED_SETTINGS_DIR)
print(settings_filnames)

prepared_settings = []
for filename in settings_filnames:
    with open(f"{PATH_TO_PREPARED_SETTINGS_DIR}/{filename}", 'r', encoding='utf-8') as fd:
        prepared_settings.append(json.loads(fd.read()))

##########################################

QUERIES_SUMMARISATION_SYSTEM_PROMPT = '''
Your task is to summarize the given list of queries into one query. Return only requested summarized query without any explanation.

## List of queries:
{queries}
'''
QUERIES_SUMMARISATION_ASSISTANT_PROMPT = '''
## Summarized query:

'''

gc.collect()
torch.cuda.empty_cache()

# !!! PAY ATTENTION !!!
agentd_config = AgentDriverConfig(
    agent_config=AgentConnectorConfig(
        credentials={ 'model': 'gemma3:12b' ,'host': 'localhost','port': 11437 }
    )
)
agent = AgentDriver.connect(agentd_config)

# !!! PAY ATTENTION !!!
embedder_config = EmbedderModelConfig(
    model_name_or_path="../../../models/intfloat/multilingual-e5-large")
embedder = EmbedderModel(embedder_config)

##########################################

for setting_fname, prepared_setting in tqdm(zip(settings_filnames, prepared_settings)):
    print(setting_fname)
    print(prepared_setting)

    BENCHMARK = prepared_setting['BENCHMARK']
    QUERY_TYPE = prepared_setting['QUERY_TYPE']
    EXP_NAME = prepared_setting['EXP_NAME']

    RESPECTIVE_TYPE_FNAMES = {
        'formalized_query': {
            'intents': 'specialized_intents',
            'tags': 'specialized_tags'
        },
        'generalized_query': {
            'intents': 'generalized_intents',
            'tags': 'generalized_tags'
        },
        'masked_query': {
            'intents': 'generalized_intents',
            'tags': 'generalized_tags'
        }
    }

    QUERIES_LOAD_PATH = f"../../../data/experiences_extraction/general_extraction(iteration#1)/{BENCHMARK}/queries_analysis.json"
    SAVE_ARTIFACTS_DIR = f"./artifacts/queries_clustering/{BENCHMARK}/{QUERY_TYPE}/{EXP_NAME}"

    SETTING = {
        'llm': 'gemma3:12b',
        'embedder': "../../../models/intfloat/multilingual-e5-large",
        'normalize_embeddings': True, # TO CHANGE
        'apply_dimension_reduction': True, # TO CHANGE
        'batch_size': 25,
        'top_k': 5,
        'max_intents': 5,
        'max_tags': 5,
        'min_cluster_size': 5, # TO CHANGE
        'min_samples': 5, # TO CHANGE
        'umap_random_state': 42,
        'queries_summarisation_task': {
            'system_prompt': QUERIES_SUMMARISATION_SYSTEM_PROMPT,
            'assistant_prompt': QUERIES_SUMMARISATION_ASSISTANT_PROMPT
        }
    }

    STATISTICS = {
        'labels_freq': None,
        'mean/std average point-centroid distance': None,
        'mean/std std point-centroid distance': None,
        'mean/std min inter-clusters distance': None,
        'mean/std mean inter-clusters distance': None
    }

    SETTING.update(prepared_setting['exp_hyperp'])
    os.mkdir(SAVE_ARTIFACTS_DIR)
    embedder.config.normalize_embeddings=SETTING['normalize_embeddings']

    #==========================================

    with open(QUERIES_LOAD_PATH, 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())

    queries = []
    for query_id, query_info in data.items():
        query_info = query_info['properties'] if (type(query_info) is dict) and ('properties' in query_info) else query_info 
        if type(query_info) is dict: 
            queries.append(
                (query_id, query_info.get(QUERY_TYPE, None), 
                query_info.get(RESPECTIVE_TYPE_FNAMES[QUERY_TYPE]['intents'], None), 
                query_info.get(RESPECTIVE_TYPE_FNAMES[QUERY_TYPE]['tags'], None))
            )
        else:
            queries.append((query_id, None))

    print(len(queries))
    queries = list(filter(lambda val: val[1] is not None, queries))
    print(len(queries))

    embeddings = []
    for i in tqdm(range(0, len(queries), SETTING['batch_size'])):
        embeddings_batch = embedder.encode_passages(list(map(lambda item: item[1], queries[i:i+SETTING['batch_size']])))
        embeddings += embeddings_batch
    print(len(embeddings))

    #==========================================

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(embeddings)
    fig = plt.figure(figsize=(8,6))
    plt.scatter(X_pca[:, 0], X_pca[:, 1], edgecolor='k')
    plt.grid()
    plt.title(QUERY_TYPE)
    plt.savefig(f"{SAVE_ARTIFACTS_DIR}/PCA_{QUERY_TYPE}_{BENCHMARK}(emb_norm={SETTING['normalize_embeddings']}).png")
    plt.close(fig)

    #==========================================

    def draw_points_distributions(points, points_labels, query_type: str, benchmark: str, save_dir: str, min_cluster_size=5, min_samples=5):
        x, y = points[:, 0], points[:, 1]
    
        # Create a figure with 6 plot areas
        fig, axes = plt.subplots(ncols=2, nrows=2, figsize=(12, 8))
        
        # Everything starts with a Scatterplot
        axes[0][0].set_title('Scatterplot')
        axes[0][0].scatter(x, y, edgecolor='k')
        axes[0][0].grid()
        
        # Thus we can cut the plotting window in several hexbins
        nbins = 20
        axes[0][1].set_title('Hexbin')
        hexbin = axes[0][1].hexbin(x, y, gridsize=nbins, cmap=plt.cm.Blues_r)
        axes[0][1].grid()
        fig.colorbar(hexbin, ax=axes[0][1], orientation='vertical', fraction=.1)

        # Evaluate a gaussian kde on a regular grid of nbins x nbins over data extents
        k = gaussian_kde(points.T)
        xi, yi = np.mgrid[x.min():x.max():nbins*1j, y.min():y.max():nbins*1j]
        zi = k(np.vstack([xi.flatten(), yi.flatten()]))

        # contour
        axes[1][0].set_title('Contour')
        contour = axes[1][0].pcolormesh(xi, yi, zi.reshape(xi.shape), shading='gouraud', cmap=plt.cm.Blues_r)
        axes[1][0].contour(xi, yi, zi.reshape(xi.shape) )
        axes[1][0].grid()
        fig.colorbar(contour, ax=axes[1][0], orientation='vertical', fraction=.1)


        # clustering
        clusters = axes[1][1].scatter(x, y, c=points_labels, edgecolor='k')
        axes[1][1].grid()
        fig.colorbar(clusters, ax=axes[1][1], orientation='vertical', fraction=.1)
        axes[1][1].set_title(f'Clustered points (min cluster size = {min_cluster_size}, min samplels = {min_samples})')

        fig.suptitle(f"{query_type} / emb_norm={SETTING['normalize_embeddings']} / PCA(1024->128)+UMAP(128->2)\n{benchmark}")
        plt.savefig(f"{save_dir}/PCA(1024->128)+UMAP(128->2)_{query_type}_{benchmark}(multiple_plots).png")

        plt.close(fig)

    #==========================================

    if SETTING['apply_dimension_reduction']:
        pca = PCA(n_components=128)
        transformed_embeddings = pca.fit_transform(embeddings)
        print(transformed_embeddings.shape)
        fit = umap.UMAP(random_state=SETTING['umap_random_state'])
        u = fit.fit_transform(transformed_embeddings)
        print(u.shape)

        # 
        fig = plt.figure(figsize=(8,6))
        plt.scatter(u[:, 0], u[:, 1], edgecolor='k')
        plt.grid()
        plt.title(f"{QUERY_TYPE} / emb_norm={SETTING['normalize_embeddings']} / PCA(1024->128)+UMAP(128->2)\n{BENCHMARK}")
        plt.savefig(f"{SAVE_ARTIFACTS_DIR}/PCA(1024->128)+UMAP(128->2)_{QUERY_TYPE}_{BENCHMARK}.png")
        plt.close(fig)
    else:
        u = np.array(embeddings)

    clusterer = hdbscan.HDBSCAN(
            min_cluster_size=SETTING['min_cluster_size'], min_samples=SETTING['min_samples'], 
            cluster_selection_method='eom', metric='euclidean', algorithm='best')
    clusterer.fit(u)

    if SETTING['apply_dimension_reduction']:
        draw_points_distributions(u, clusterer.labels_, QUERY_TYPE, BENCHMARK, SAVE_ARTIFACTS_DIR, SETTING['min_cluster_size'], SETTING['min_samples'])

    #==========================================

    labels_freq = Counter(clusterer.labels_)
    print(labels_freq)
    print(len(list(labels_freq.keys())))
    STATISTICS['labels_freq'] = {int(k): v for k,v in labels_freq.items()}

    #==========================================

    GROUPED_QUERIES = defaultdict(list)
    for query, label in zip(queries, clusterer.labels_):
        GROUPED_QUERIES[int(label)].append(query)
    GROUPED_QUERIES = dict(GROUPED_QUERIES)

    grouped_points = defaultdict(list)
    for point, label in zip(u, clusterer.labels_):
        grouped_points[int(label)].append(point.tolist())
    grouped_points = dict(grouped_points)
    if -1 in grouped_points.keys(): 
        del grouped_points[-1]

    clusters_centroids = dict()
    for label, points in grouped_points.items():
        clusters_centroids[label] = np.array(points).mean(0).tolist()

    #==========================================

    if SETTING['apply_dimension_reduction']:
        fig, ax = plt.subplots(figsize=(8,6))
        centroid_points = np.array(list(clusters_centroids.values()))
        plt.scatter(centroid_points[:,0], centroid_points[:,1], c=list(clusters_centroids.keys()))

        eps = 0.1
        for label, points in grouped_points.items():
            plt.text(clusters_centroids[label][0]+eps, clusters_centroids[label][1]+eps, str(label))
            distances = distance.euclidean(np.array(points),clusters_centroids[label])
            points_to_centroid_mean = np.mean(distances)
            points_to_centroid_std = np.std(distances)
            circle_mean = plt.Circle(xy=clusters_centroids[label], radius=points_to_centroid_mean, color='red', fill=False, linewidth=1)
            #circle_std = plt.Circle(xy=clusters_centroids[label], radius=points_to_centroid_std, color='blue', fill=False, linewidth=1)
            ax.add_patch(circle_mean)
            #ax.add_patch(circle_std)

        plt.title(f"Clusters centroids with labels\nand mean distances to their points (marked as red circles)\n{QUERY_TYPE} / {BENCHMARK} / emb_norm={SETTING['normalize_embeddings']}")
        plt.grid()
        plt.savefig(f"{SAVE_ARTIFACTS_DIR}/clusters_centroids(PCA(1024->128)+UMAP(128->2)_{QUERY_TYPE}_{BENCHMARK}).png")
        plt.close(fig)

    #==========================================

    points_to_centroids_distances = dict()
    points_to_centroid_means = dict()
    points_to_centroid_stds = dict()
    for label, points in grouped_points.items():
        points_to_centroids_distances[label] = distance.euclidean(np.array(points),clusters_centroids[label])
        points_to_centroid_mean = np.mean(points_to_centroids_distances[label])
        points_to_centroid_std = np.std(points_to_centroids_distances[label])
        points_to_centroid_means[label] = float(points_to_centroid_mean)
        points_to_centroid_stds[label] = float(points_to_centroid_std)

    STATISTICS['mean/std average point-centroid distance'] = (
        float(np.mean(list(points_to_centroid_means.values()))),
        float(np.std(list(points_to_centroid_means.values())))
    )
    STATISTICS['mean/std std point-centroid distance'] = (
        float(np.mean(list(points_to_centroid_stds.values()))),
        float(np.std(list(points_to_centroid_stds.values())))
    )
    print(STATISTICS['mean/std average point-centroid distance'])
    print(STATISTICS['mean/std std point-centroid distance'])

    #==========================================

    centroid_distances = defaultdict(list)
    for i in range(max(clusterer.labels_)+1):
        for j in range(max(clusterer.labels_)+1):
            if i != j:
                centroid_distances[i].append(float(distance.euclidean(clusters_centroids[i],clusters_centroids[j])))

    mean_centroid_distances = {k: float(np.mean(v)) for k,v in dict(centroid_distances).items()}
    min_centroid_distances = {k: float(np.min(v)) for k,v in dict(centroid_distances).items()}

    STATISTICS['mean/std min inter-clusters distance'] = (
        float(np.mean(list(min_centroid_distances.values()))),
        float(np.std(list(min_centroid_distances.values())))
    )
    print(STATISTICS['mean/std min inter-clusters distance'])

    STATISTICS['mean/std mean inter-clusters distance'] = (
        float(np.mean(list(mean_centroid_distances.values()))),
        float(np.std(list(mean_centroid_distances.values())))
    )
    print(STATISTICS['mean/std mean inter-clusters distance'])

    #==========================================

    GROUPED_INTENTS = defaultdict(list) 
    for label, queries in GROUPED_QUERIES.items():
        GROUPED_INTENTS[label] = reduce(lambda acc, v: acc + v[2], queries, [])
    GROUPED_TAGS = defaultdict(list) 
    for label, queries in GROUPED_QUERIES.items():
        GROUPED_TAGS[label] = reduce(lambda acc, v: acc + v[3], queries, [])

    #==========================================

    print("Generating summaries...")
    SUMMARIZED_GROUPED_QUERIES = dict()
    for label in points_to_centroids_distances.keys():
        #print("LABEL: ", label)
        sorted_queries = sorted(list(zip(points_to_centroids_distances[label], GROUPED_QUERIES[label])), key=lambda v: v[0], reverse=False)
        # for top_experience in sorted_queries[:SETTING['top_k']]:
        #     print(top_experience[1])

        formatted_queries = '\n'.join([f"* {query_info[1][2]}" for query_info in sorted_queries[:SETTING['top_k']]])
        response, stat = agent.generate(
            system_prompt=SETTING['queries_summarisation_task']['system_prompt'].format(queries=formatted_queries),
            assistant_prompt=SETTING['queries_summarisation_task']['assistant_prompt']
        )

        #print(f"SUMMARY:\n- query: {response}")
        SUMMARIZED_GROUPED_QUERIES[label] = [labels_freq[label], response]

    #==========================================

    for label in points_to_centroids_distances.keys():    
        intents_frequency = Counter(GROUPED_INTENTS[label])
        sorted_intents = sorted(list(intents_frequency.items()), key=lambda v: v[1], reverse=True)
        intents_names = list(map(lambda v: v[0], sorted_intents))

        tags_frequency = Counter(GROUPED_TAGS[label])
        sorted_tags = sorted(list(tags_frequency.items()), key=lambda v: v[1], reverse=True)
        tags_names = list(map(lambda v: v[0], sorted_tags))

        SUMMARIZED_GROUPED_QUERIES[label] += [
            intents_names[:SETTING['max_intents']], 
            tags_names[:SETTING['max_tags']], 
        ]

    #==========================================

    with open(f"{SAVE_ARTIFACTS_DIR}/grouped_{QUERY_TYPE}_{BENCHMARK}(dim_reduction={SETTING['apply_dimension_reduction']},emb_norm={SETTING['normalize_embeddings']}).json", 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(GROUPED_QUERIES, ensure_ascii=False, indent=2))
    with open(f"{SAVE_ARTIFACTS_DIR}/summarized_{QUERY_TYPE}_{BENCHMARK}(dim_reduction={SETTING['apply_dimension_reduction']}, emb_norm={SETTING['normalize_embeddings']}).json", 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(SUMMARIZED_GROUPED_QUERIES, ensure_ascii=False, indent=2))
    with open(f"{SAVE_ARTIFACTS_DIR}/statistics_{QUERY_TYPE}_{BENCHMARK}(dim_reduction={SETTING['apply_dimension_reduction']}, emb_norm={SETTING['normalize_embeddings']}).json", 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(STATISTICS, ensure_ascii=False, indent=2))
    with open(f"{SAVE_ARTIFACTS_DIR}/setting.json", 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(SETTING, ensure_ascii=False, indent=2))

##########################################

agent.close_connection()
del embedder

##########################################