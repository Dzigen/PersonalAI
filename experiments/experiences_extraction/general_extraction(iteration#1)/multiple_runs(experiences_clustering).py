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

EXPERIENCES_SUMMARISATION_SYSTEM_PROMPT = '''
Your task is to summarize the given list of experiences into one experience. Return only requested summarized experience without any explanation.

## List of experiences:
{experiences}
'''
EXPERIENCES_SUMMARISATION_ASSISTANT_PROMPT = '''
## Summarized experience:

'''
WHENTOUSE_SUMMARISATION_SYSTEM_PROMPT = '''
Your task is to summarize the given list of 'when_to_use' statements into one statement. Return only requested summarized statement without any explanation.

## List of 'when_to_use' statements:
{whentouses}
'''
WHENTOUSE_SUMMARISATION_ASSISTANT_PROMPT = '''
## Summarized 'when_to_use' statements:

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
    EXPERIENCE_TYPE = prepared_setting['EXPERIENCE_TYPE']
    EXP_NAME = prepared_setting['EXP_NAME']

    EXPERIENCES_LOAD_PATH = f"../../../data/experiences_extraction/general_extraction(iteration#1)/{BENCHMARK}/raw_extracted_experiences.json"
    SAVE_ARTIFACTS_DIR = f"./artifacts/experiences_clustering/{BENCHMARK}/{EXPERIENCE_TYPE}/{EXP_NAME}"

    SETTING = {
        'llm': 'gemma3:12b', # FIXED
        'embedder': "../../../models/intfloat/multilingual-e5-large", # FIXED
        'normalize_embeddings': True,
        'apply_dimension_reduction': True,
        'batch_size': 25,
        'top_k': 5,
        'max_keywords': 5,
        'max_tags': 5,
        'max_tools': 5,
        'min_cluster_size': 5,
        'min_samples': 5,
        'umap_random_state': 42,
        'experienes_summarisation_task': {
            'system_prompt': EXPERIENCES_SUMMARISATION_SYSTEM_PROMPT,
            'assistant_prompt': EXPERIENCES_SUMMARISATION_ASSISTANT_PROMPT
        },
        'whentouse_summarisation_task': {
            'system_prompt': WHENTOUSE_SUMMARISATION_SYSTEM_PROMPT,
            'assistant_prompt': WHENTOUSE_SUMMARISATION_ASSISTANT_PROMPT
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

    with open(EXPERIENCES_LOAD_PATH, 'r', encoding='utf-8') as fd:
        data = json.loads(fd.read())

    experiences = reduce(lambda acc, v:  acc + [(v[0], i, exp.get(EXPERIENCE_TYPE, None), exp.get('when_to_use', None), exp.get('tags', None), exp.get('keywords', None), exp.get('tools_used', None)) for i, exp in enumerate(v[1]['experiences'])] if v[1] is not None else [], data.items(), [])
    print(len(experiences))
    experiences = list(filter(lambda val: val[2] is not None, experiences))
    print(len(experiences))

    embeddings = []
    for i in tqdm(range(0, len(experiences), SETTING['batch_size'])):
        embeddings_batch = embedder.encode_passages(list(map(lambda item: item[2], experiences[i:i+SETTING['batch_size']])))
        embeddings += embeddings_batch
    print(len(embeddings))

    #==========================================

    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(embeddings)
    fig = plt.figure(figsize=(8,6))
    plt.scatter(X_pca[:, 0], X_pca[:, 1], edgecolor='k')
    plt.grid()
    plt.title(EXPERIENCE_TYPE)
    plt.savefig(f"{SAVE_ARTIFACTS_DIR}/PCA_{EXPERIENCE_TYPE}_{BENCHMARK}(emb_norm={SETTING['normalize_embeddings']}).png")
    plt.close(fig)

    #==========================================

    def draw_points_distributions(points, points_labels, experience_type: str, benchmark: str, save_dir: str, min_cluster_size=5, min_samples=5):
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

        fig.suptitle(f"{experience_type} / emb_norm={SETTING['normalize_embeddings']} / PCA(1024->128)+UMAP(128->2)\n{benchmark}")
        plt.savefig(f"{save_dir}/PCA(1024->128)+UMAP(128->2)_{experience_type}_{benchmark}(multiple_plots).png")
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
        plt.title(f"{EXPERIENCE_TYPE} / emb_norm={SETTING['normalize_embeddings']} / PCA(1024->128)+UMAP(128->2)\n{BENCHMARK}")
        plt.savefig(f"{SAVE_ARTIFACTS_DIR}/PCA(1024->128)+UMAP(128->2)_{EXPERIENCE_TYPE}_{BENCHMARK}.png")
        plt.close(fig)
    else:
        u = np.array(embeddings)

    clusterer = hdbscan.HDBSCAN(
            min_cluster_size=SETTING['min_cluster_size'], min_samples=SETTING['min_samples'], 
            cluster_selection_method='eom', metric='euclidean', algorithm='best')
    clusterer.fit(u)

    if SETTING['apply_dimension_reduction']:
        draw_points_distributions(u, clusterer.labels_, EXPERIENCE_TYPE, BENCHMARK, SAVE_ARTIFACTS_DIR, SETTING['min_cluster_size'], SETTING['min_samples'])

    #==========================================

    labels_freq = Counter(clusterer.labels_)
    print(labels_freq)
    print(len(list(labels_freq.keys())))
    STATISTICS['labels_freq'] = {int(k): v for k,v in labels_freq.items()}

    #==========================================

    GROUPED_EXPERIENCES = defaultdict(list)
    for experience, label in zip(experiences, clusterer.labels_):
        GROUPED_EXPERIENCES[int(label)].append(experience)
    GROUPED_EXPERIENCES = dict(GROUPED_EXPERIENCES)

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

        plt.title(f"Clusters centroids with labels\nand mean distances to their points (marked as red circles)\n{EXPERIENCE_TYPE} / {BENCHMARK} / emb_norm={SETTING['normalize_embeddings']}")
        plt.grid()
        plt.savefig(f"{SAVE_ARTIFACTS_DIR}/clusters_centroids(PCA(1024->128)+UMAP(128->2)_{EXPERIENCE_TYPE}_{BENCHMARK}).png")
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

    GROUPED_WTAGS = defaultdict(list) 
    for label, experiences in GROUPED_EXPERIENCES.items():
        GROUPED_WTAGS[label] = reduce(lambda acc, v: acc + (v[5] if v[5] is not None else []), experiences, [])
    GROUPED_ETAGS = defaultdict(list) 
    for label, experiences in GROUPED_EXPERIENCES.items():
        GROUPED_ETAGS[label] = reduce(lambda acc, v: acc + (v[4] if v[4] is not None else []), experiences, [])
    GROUPED_TOOLS = defaultdict(list) 
    for label, experiences in GROUPED_EXPERIENCES.items():
        GROUPED_TOOLS[label] = reduce(lambda acc, v: acc + (v[6] if v[6] is not None else []), experiences, [])

    #==========================================

    print("Generating summaries...")
    SUMMARIZED_GROUPED_EXPERIENCES = dict()
    for label in points_to_centroids_distances.keys():
        #print("LABEL: ", label)
        sorted_experiences = sorted(list(zip(points_to_centroids_distances[label], GROUPED_EXPERIENCES[label])), reverse=False)
        # for top_experience in sorted_experiences[:SETTING['top_k']]:
        #     print(top_experience[1])

        formatted_whentouses = '\n'.join([f"* {experience_info[1][3]}" for experience_info in sorted_experiences[:SETTING['top_k']]])
        response1, stat1 = agent.generate(
            system_prompt=SETTING['whentouse_summarisation_task']['system_prompt'].format(whentouses=formatted_whentouses),
            assistant_prompt=SETTING['whentouse_summarisation_task']['assistant_prompt']
        )

        formatted_experiences = '\n'.join([f"* {experience_info[1][2]}" for experience_info in sorted_experiences[:SETTING['top_k']]])
        response2, stat2 = agent.generate(
            system_prompt=SETTING['experienes_summarisation_task']['system_prompt'].format(experiences=formatted_experiences),
            assistant_prompt=SETTING['experienes_summarisation_task']['assistant_prompt']
        )

        #print(f"SUMMARY:\n- when to use: {response1}\n- experience: {response2}")
        SUMMARIZED_GROUPED_EXPERIENCES[label] = [labels_freq[label], response1, response2]

    for label in points_to_centroids_distances.keys():    
        wtags_frequency = Counter(GROUPED_WTAGS[label])
        sorted_wtags = sorted(list(wtags_frequency.items()), key=lambda v: v[1], reverse=True)
        wtags_names = list(map(lambda v: v[0], sorted_wtags))

        etags_frequency = Counter(GROUPED_ETAGS[label])
        sorted_etags = sorted(list(etags_frequency.items()), key=lambda v: v[1], reverse=True)
        etags_names = list(map(lambda v: v[0], sorted_etags))

        tooluse_frequency = Counter(GROUPED_TOOLS[label])
        sorted_tools = sorted(list(tooluse_frequency.items()), key=lambda v: v[1], reverse=True)
        tooluse_names = list(map(lambda v: v[0], sorted_tools))

        SUMMARIZED_GROUPED_EXPERIENCES[label] += [
            wtags_names[:SETTING['max_keywords']], 
            etags_names[:SETTING['max_tags']], 
            tooluse_names[:SETTING['max_tools']]
        ]

    #==========================================

    with open(f"{SAVE_ARTIFACTS_DIR}/grouped_{EXPERIENCE_TYPE}_{BENCHMARK}(dim_reduction={SETTING['apply_dimension_reduction']},emb_norm={SETTING['normalize_embeddings']}).json", 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(GROUPED_EXPERIENCES, ensure_ascii=False, indent=2))
    with open(f"{SAVE_ARTIFACTS_DIR}/summarized_{EXPERIENCE_TYPE}_{BENCHMARK}(dim_reduction={SETTING['apply_dimension_reduction']}, emb_norm={SETTING['normalize_embeddings']}).json", 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(SUMMARIZED_GROUPED_EXPERIENCES, ensure_ascii=False, indent=2))
    with open(f"{SAVE_ARTIFACTS_DIR}/statistics_{EXPERIENCE_TYPE}_{BENCHMARK}(dim_reduction={SETTING['apply_dimension_reduction']}, emb_norm={SETTING['normalize_embeddings']}).json", 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(STATISTICS, ensure_ascii=False, indent=2))
    with open(f"{SAVE_ARTIFACTS_DIR}/setting.json", 'w', encoding='utf-8') as fd:
        fd.write(json.dumps(SETTING, ensure_ascii=False, indent=2))

##########################################

agent.close_connection()
del embedder

##########################################