from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient # type: ignore

# Create an instance of the FastAPI class
app = FastAPI()

# MongoDB connection URI
MONGODB_URI = "mongodb+srv://alnabeel:123456%40al@atlascluster.jjglekx.mongodb.net/"
# MongoDB database name
DATABASE_NAME = "fastapi_demo"
# MongoDB collection name
COLLECTION_NAME = "items"

# Define a request body model using Pydantic
class Item(BaseModel):
    name: str
    description: str
    price: float
    tax: float

# Connect to MongoDB
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Define a route to create a new item
@app.post("/items/")
async def create_item(item: Item):
    result = await collection.insert_one(item.dict())
    return {"message": "Item created successfully", "item_id": str(result.inserted_id)}

# Define a route to retrieve all items
@app.get("/items/")
async def read_items():
    items = []
    async for item in collection.find():
        items.append(item)
    return items

# Define a route to retrieve a specific item by its ID
@app.get("/items/{item_id}")
async def read_item(item_id: str):
    item = await collection.find_one({"_id": item_id})
    if item:
        return item
    else:
        raise HTTPException(status_code=404, detail="Item not found")

# Define a route to update an existing item
@app.put("/items/{item_id}")
async def update_item(item_id: str, item: Item):
    result = await collection.update_one({"_id": item_id}, {"$set": item.dict()})
    if result.modified_count == 1:
        return {"message": "Item updated successfully", "item_id": item_id}
    else:
        raise HTTPException(status_code=404, detail="Item not found")

# Define a route to delete an existing item
@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    result = await collection.delete_one({"_id": item_id})
    if result.deleted_count == 1:
        return {"message": "Item deleted successfully", "item_id": item_id}
    else:
        raise HTTPException(status_code=404, detail="Item not found")
