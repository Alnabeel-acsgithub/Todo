from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List

app = FastAPI()

# MongoDB connection URI
MONGODB_URI = "mongodb+srv://alnabeel27:123456%40al@cluster0.wejylnu.mongodb.net/db.net/"
DATABASE_NAME = "fastapi_demo"
COLLECTION_NAME = "items"

# MongoDB client and database
client = AsyncIOMotorClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Pydantic model for data validation
class Item(BaseModel):
    name: str
    description: str
    price: float
    tax: float

class ItemInDB(Item):
    id: str

# Helper function to convert MongoDB document to Pydantic model
def item_helper(item) -> ItemInDB:
    return ItemInDB(
        id=str(item["_id"]),
        name=item["name"],
        description=item["description"],
        price=item["price"],
        tax=item["tax"],
    )

# Create a new item
@app.post("/items/", response_model=ItemInDB)
async def create_item(item: Item):
    new_item = await collection.insert_one(item.dict())
    created_item = await collection.find_one({"_id": new_item.inserted_id})
    return item_helper(created_item)

# Retrieve all items
@app.get("/items/", response_model=List[ItemInDB])
async def read_items():
    items = []
    async for item in collection.find():
        items.append(item_helper(item))
    return items

# Retrieve a specific item by its ID
@app.get("/items/{item_id}", response_model=ItemInDB)
async def read_item(item_id: str):
    if (item := await collection.find_one({"_id": ObjectId(item_id)})) is not None:
        return item_helper(item)
    raise HTTPException(status_code=404, detail="Item not found")

# Update an existing item
@app.put("/items/{item_id}", response_model=ItemInDB)
async def update_item(item_id: str, item: Item):
    if (existing_item := await collection.find_one({"_id": ObjectId(item_id)})) is not None:
        await collection.update_one({"_id": ObjectId(item_id)}, {"$set": item.dict()})
        updated_item = await collection.find_one({"_id": ObjectId(item_id)})
        return item_helper(updated_item)
    raise HTTPException(status_code=404, detail="Item not found")

# Delete an existing item
@app.delete("/items/{item_id}")
async def delete_item(item_id: str):
    delete_result = await collection.delete_one({"_id": ObjectId(item_id)})
    if delete_result.deleted_count == 1:
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")
