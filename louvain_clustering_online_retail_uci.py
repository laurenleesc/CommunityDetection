import pandas as pd
import igraph as ig
import louvain
import datetime

# get the data file from https://archive.ics.uci.edu/ml/datasets/Online%20Retail
data_org = pd.read_excel("Online Retail.xlsx")

data = data_org[['StockCode', 'CustomerID', 'Quantity']]

data = data.dropna()

data = data.groupby(["StockCode", "CustomerID"]).count().reset_index()

data["CustomerID"] = data["CustomerID"].astype(int)
data["CustomerID"] = "c" + data["CustomerID"].astype(str)
data["StockCode"] = "p" + data["StockCode"].astype(str)

tuples = [tuple(x) for x in data.values]
G = ig.Graph.TupleList(tuples, edge_attrs = ["Quantity"])

vs_type = []

for v in G.vs:
    if v["name"][0]=="c": 
        vs_type.append(0)
    else:
        vs_type.append(1)
        
G.vs['type'] = vs_type

print("The graph is a bipartite graph?", G.is_bipartite())

print("The number of vertices: ", G.vcount())
print("The number of edges: ", G.ecount())

t1 = datetime.datetime.now()

partition = louvain.find_partition(G, louvain.ModularityVertexPartition, weights='Quantity')

t2 = datetime.datetime.now()

print("The running time of clustering the graph: ", t2-t1)

print("The clustering summary: ", partition.summary())

cluster_count = int(partition.summary().split()[-2])

print("The number of clusters: ", cluster_count)

G.vs["membership"] = partition._membership

customers_df = []
products_df = []

for i in range(cluster_count):
    customerID = []
    productID = []
    for v in G.vs:
        if v["membership"]==i:
            if "p" in v["name"]:
                #productID.append(v["name"][1:])
                productID.append(v["name"])
            else:
                #customerID.append(int(v["name"][1:]))
                customerID.append(v["name"])
    
    customer = pd.DataFrame()
    customer["CustomerID"] = customerID
    
    product = pd.DataFrame()
    product["StockCode"] = productID
    
    customer["cluster"] = i
    product["cluster"] = i
    
    customers_df.append(customer)
    products_df.append(product)
    
customers = pd.concat(customers_df)
products = pd.concat(products_df)