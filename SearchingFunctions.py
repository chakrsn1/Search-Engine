import numpy as np
def PageRank(links, iterations = 100, damping_factor = 0.85):
    #Finding Length of links
    N = len(links)

    #Initializing our pageRank values
    pagerank = np.ones(N)/N

    #Creating Link Matrix
    link_matrix = np.zeros((N, N))
    for i, outgoing_links in enumerate(links):
        if outgoing_links:
            link_matrix[i, outgoing_links] = 1 / len(outgoing_links)

    #Going through our iterations to make a more accurate pagerank value
    for _ in range(iterations):
        new_pagerank = (1 - damping_factor) / N + damping_factor * link_matrix.T.dot(pagerank)
        if np.allclose(new_pagerank, pagerank):
            break
        pagerank = new_pagerank

    return pagerank

