from collect import collect
from analyze import analyze
from graph import graph

# What to search on Twitter?
search_query = "SNDL OR sundial"
name_of_stock = "SNDL"

# Collect data about the search query?
should_collect = True

# Analyze sentiment of collected data?
should_analyze = True

# Graph the collected sentiment data?
should_graph = True

if __name__ == "__main__":
    if should_collect:
        collect(search_query)

    if should_analyze:
        analyze()

    if should_graph:
        graph(name_of_stock)


# http://gambiste.com/
