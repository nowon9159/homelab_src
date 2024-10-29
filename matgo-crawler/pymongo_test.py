from pymongo import MongoClient
client = MongoClient('127.0.0.1', 45243) # minikube service mongodb --url
db_matgo = client.matgo


all_metadata = list(db_matgo.metadata.find({}))
print(all_metadata[0])

# DML
# Insert

# db_matgo.metadata.insert_one(
#     {
#         'name':'bobby','age':21
#         }
#     )

# db_matgo.metadata.insert_many(
#     [
#         {
#         'name':'bobby','age':21
#         },
#         {
#         'name':'john','age':23
#         },
#     ]
#     )

# Select

# db_matgo.metadata.find(
#     {
#         "name": "bobby",
#         "age": 21
#     }
# )

