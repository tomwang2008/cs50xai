import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    n_pages = len(corpus)
    probabilities = dict()

    links = corpus[page]
    if links:
        for p in corpus:
            probabilities[p] = (1 - damping_factor) / n_pages
            if p in links:
                probabilities[p] += damping_factor / len(links)
    else:
        # If no outgoing links, treat as linking to all pages
        for p in corpus:
            probabilities[p] = 1 / n_pages

    return probabilities


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_counts = {page: 0 for page in corpus}
    pages = list(corpus.keys())
    current_page = random.choice(pages)

    for _ in range(n):
        page_counts[current_page] += 1
        model = transition_model(corpus, current_page, damping_factor)
        next_pages = list(model.keys())
        probabilities = list(model.values())
        current_page = random.choices(next_pages, weights=probabilities, k=1)[0]

    pagerank = {page: count / n for page, count in page_counts.items()}
    return pagerank

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    pagerank = {page: 1 / N for page in corpus}
    convergence = False
    threshold = 0.001

    while not convergence:
        new_pagerank = {}
        for page in corpus:
            total = 0
            for possible_page in corpus:
                # If possible_page has no links, treat as linking to all pages
                links = corpus[possible_page] if corpus[possible_page] else set(corpus.keys())
                if page in links:
                    total += pagerank[possible_page] / len(links)
            new_pagerank[page] = (1 - damping_factor) / N + damping_factor * total

        # Check for convergence
        convergence = all(abs(new_pagerank[page] - pagerank[page]) < threshold for page in pagerank)
        pagerank = new_pagerank

    # Normalize to ensure sum is 1
    total_sum = sum(pagerank.values())
    pagerank = {page: rank / total_sum for page, rank in pagerank.items()}
    return pagerank
    

if __name__ == "__main__":
    main()
